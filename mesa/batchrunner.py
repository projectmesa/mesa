"""
Batchrunner
===========

A single class to manage a batch run or parameter sweep of a given model.
"""
import copy
import itertools
import random
from functools import partial
from itertools import count, product
from multiprocessing import Pool, cpu_count
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)
from warnings import warn

import pandas as pd
from tqdm import tqdm

from mesa.model import Model


def batch_run(
    model_cls: Type[Model],
    parameters: Mapping[str, Union[Any, Iterable[Any]]],
    # We still retain the Optional[int] because users may set it to None (i.e. use all CPUs)
    number_processes: Optional[int] = 1,
    iterations: int = 1,
    data_collection_period: int = -1,
    max_steps: int = 1000,
    display_progress: bool = True,
) -> List[Dict[str, Any]]:
    """Batch run a mesa model with a set of parameter values.

    Parameters
    ----------
    model_cls : Type[Model]
        The model class to batch-run
    parameters : Mapping[str, Union[Any, Iterable[Any]]],
        Dictionary with model parameters over which to run the model. You can either pass single values or iterables.
    number_processes : int, optional
        Number of processes used, by default 1. Set this to None if you want to use all CPUs.
    iterations : int, optional
        Number of iterations for each parameter combination, by default 1
    data_collection_period : int, optional
        Number of steps after which data gets collected, by default -1 (end of episode)
    max_steps : int, optional
        Maximum number of model steps after which the model halts, by default 1000
    display_progress : bool, optional
        Display batch run process, by default True

    Returns
    -------
    List[Dict[str, Any]]
        [description]
    """

    runs_list = []
    run_id = 0
    for iteration in range(iterations):
        for kwargs in _make_model_kwargs(parameters):
            runs_list.append((run_id, iteration, kwargs))
            run_id += 1

    process_func = partial(
        _model_run_func,
        model_cls,
        max_steps=max_steps,
        data_collection_period=data_collection_period,
    )

    results: List[Dict[str, Any]] = []

    with tqdm(total=len(runs_list), disable=not display_progress) as pbar:
        if number_processes == 1:
            for run in runs_list:
                data = process_func(run)
                results.extend(data)
                pbar.update()
        else:
            with Pool(number_processes) as p:
                for data in p.imap_unordered(process_func, runs_list):
                    results.extend(data)
                    pbar.update()

    return results


def _make_model_kwargs(
    parameters: Mapping[str, Union[Any, Iterable[Any]]]
) -> List[Dict[str, Any]]:
    """Create model kwargs from parameters dictionary.

    Parameters
    ----------
    parameters : Mapping[str, Union[Any, Iterable[Any]]]
        Single or multiple values for each model parameter name

    Returns
    -------
    List[Dict[str, Any]]
        A list of all kwargs combinations.
    """
    parameter_list = []
    for param, values in parameters.items():
        if isinstance(values, str):
            # The values is a single string, so we shouldn't iterate over it.
            all_values = [(param, values)]
        else:
            try:
                all_values = [(param, value) for value in values]
            except TypeError:
                all_values = [(param, values)]
        parameter_list.append(all_values)
    all_kwargs = itertools.product(*parameter_list)
    kwargs_list = [dict(kwargs) for kwargs in all_kwargs]
    return kwargs_list


def _model_run_func(
    model_cls: Type[Model],
    run: Tuple[int, int, Dict[str, Any]],
    max_steps: int,
    data_collection_period: int,
) -> List[Dict[str, Any]]:
    """Run a single model run and collect model and agent data.

    Parameters
    ----------
    model_cls : Type[Model]
        The model class to batch-run
    run: Tuple[int, int, Dict[str, Any]]
        The run id, iteration number, and kwargs for this run
    max_steps : int
        Maximum number of model steps after which the model halts, by default 1000
    data_collection_period : int
        Number of steps after which data gets collected

    Returns
    -------
    List[Dict[str, Any]]
        Return model_data, agent_data from the reporters
    """
    run_id, iteration, kwargs = run
    model = model_cls(**kwargs)
    while model.running and model.schedule.steps <= max_steps:
        model.step()

    data = []

    steps = list(range(0, model.schedule.steps, data_collection_period))
    if not steps or steps[-1] != model.schedule.steps - 1:
        steps.append(model.schedule.steps - 1)

    for step in steps:
        model_data, all_agents_data = _collect_data(model, step)

        # If there are agent_reporters, then create an entry for each agent
        if all_agents_data:
            stepdata = [
                {
                    "RunId": run_id,
                    "iteration": iteration,
                    "Step": step,
                    **kwargs,
                    **model_data,
                    **agent_data,
                }
                for agent_data in all_agents_data
            ]
        # If there is only model data, then create a single entry for the step
        else:
            stepdata = [
                {
                    "RunId": run_id,
                    "iteration": iteration,
                    "Step": step,
                    **kwargs,
                    **model_data,
                }
            ]
        data.extend(stepdata)

    return data


def _collect_data(
    model: Model,
    step: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Collect model and agent data from a model using mesas datacollector."""
    dc = model.datacollector

    model_data = {param: values[step] for param, values in dc.model_vars.items()}

    all_agents_data = []
    raw_agent_data = dc._agent_records.get(step, [])
    for data in raw_agent_data:
        agent_dict = {"AgentID": data[1]}
        agent_dict.update(zip(dc.agent_reporters, data[2:]))
        all_agents_data.append(agent_dict)
    return model_data, all_agents_data


class ParameterError(TypeError):
    MESSAGE = (
        "Parameters must map a name to a value. "
        "These names did not match parameters: {}"
    )

    def __init__(self, bad_names):
        self.bad_names = bad_names

    def __str__(self):
        return self.MESSAGE.format(self.bad_names)


class VariableParameterError(ParameterError):
    MESSAGE = (
        "Variable_parameters must map a name to a sequence of values. "
        "These parameters were given with non-sequence values: {}"
    )


class FixedBatchRunner:
    """This class is instantiated with a model class, and model parameters
    associated with one or more values. It is also instantiated with model and
    agent-level reporters, dictionaries mapping a variable name to a function
    which collects some data from the model or its agents at the end of the run
    and stores it.

    Note that by default, the reporters only collect data at the *end* of the
    run. To get step by step data, simply have a reporter store the model's
    entire DataCollector object.
    """

    def __init__(
        self,
        model_cls,
        parameters_list=None,
        fixed_parameters=None,
        iterations=1,
        max_steps=1000,
        model_reporters=None,
        agent_reporters=None,
        display_progress=True,
    ):
        """Create a new BatchRunner for a given model with the given
        parameters.

        Args:
            model_cls: The class of model to batch-run.
            parameters_list: A list of dictionaries of parameter sets.
                The model will be run with dictionary of parameters.
                For example, given parameters_list of
                    [{"homophily": 3, "density": 0.8, "minority_pc": 0.2},
                    {"homophily": 2, "density": 0.9, "minority_pc": 0.1},
                    {"homophily": 4, "density": 0.6, "minority_pc": 0.5}]
                3 models will be run, one for each provided set of parameters.
            fixed_parameters: Dictionary of parameters that stay same through
                all batch runs. For example, given fixed_parameters of
                    {"constant_parameter": 3},
                every instantiated model will be passed constant_parameter=3
                as a kwarg.
            iterations: The total number of times to run the model for each set
                of parameters.
            max_steps: Upper limit of steps above which each run will be halted
                if it hasn't halted on its own.
            model_reporters: The dictionary of variables to collect on each run
                at the end, with variable names mapped to a function to collect
                them. For example:
                    {"agent_count": lambda m: m.schedule.get_agent_count()}
            agent_reporters: Like model_reporters, but each variable is now
                collected at the level of each agent present in the model at
                the end of the run.
            display_progress: Display progress bar with time estimation?
        """
        self.model_cls = model_cls
        if parameters_list is None:
            parameters_list = []
        self.parameters_list = list(parameters_list)
        self.fixed_parameters = fixed_parameters or {}
        self._include_fixed = len(self.fixed_parameters) > 0
        self.iterations = iterations
        self.max_steps = max_steps

        for params in self.parameters_list:
            if list(params) != list(self.parameters_list[0]):
                msg = "parameter names in parameters_list are not equal across the list"
                raise ValueError(msg)

        self.model_reporters = model_reporters
        self.agent_reporters = agent_reporters

        if self.model_reporters:
            self.model_vars = {}

        if self.agent_reporters:
            self.agent_vars = {}

        self.datacollector_model_reporters = {}
        self.datacollector_agent_reporters = {}

        self.display_progress = display_progress

    def _make_model_args(self):
        """Prepare all combinations of parameter values for `run_all`

        Returns:
            Tuple with the form:
            (total_iterations, all_kwargs, all_param_values)
        """
        total_iterations = self.iterations
        all_kwargs = []
        all_param_values = []

        count = len(self.parameters_list)
        if count:
            for params in self.parameters_list:
                kwargs = params.copy()
                kwargs.update(self.fixed_parameters)
                all_kwargs.append(kwargs)
                all_param_values.append(list(params.values()))

        elif len(self.fixed_parameters):
            count = 1
            kwargs = self.fixed_parameters.copy()
            all_kwargs.append(kwargs)
            all_param_values.append(list(kwargs.values()))

        total_iterations *= count

        return total_iterations, all_kwargs, all_param_values

    def run_all(self):
        """Run the model at all parameter combinations and store results."""
        run_count = count()
        total_iterations, all_kwargs, all_param_values = self._make_model_args()

        with tqdm(total_iterations, disable=not self.display_progress) as pbar:
            for i, kwargs in enumerate(all_kwargs):
                param_values = all_param_values[i]
                for _ in range(self.iterations):
                    self.run_iteration(kwargs, param_values, next(run_count))
                    pbar.update()

    def run_iteration(self, kwargs, param_values, run_count):
        model = self.model_cls(**kwargs)
        results = self.run_model(model)
        if param_values is not None:
            model_key = (*tuple(param_values), run_count)
        else:
            model_key = (run_count,)

        if self.model_reporters:
            self.model_vars[model_key] = self.collect_model_vars(model)
        if self.agent_reporters:
            agent_vars = self.collect_agent_vars(model)
            for agent_id, reports in agent_vars.items():
                agent_key = (*model_key, agent_id)
                self.agent_vars[agent_key] = reports
        # Collects data from datacollector object in model
        if results is not None:
            if results.model_reporters is not None:
                self.datacollector_model_reporters[
                    model_key
                ] = results.get_model_vars_dataframe()
            if results.agent_reporters is not None:
                self.datacollector_agent_reporters[
                    model_key
                ] = results.get_agent_vars_dataframe()

        return (
            getattr(self, "model_vars", None),
            getattr(self, "agent_vars", None),
            getattr(self, "datacollector_model_reporters", None),
            getattr(self, "datacollector_agent_reporters", None),
        )

    def run_model(self, model):
        """Run a model object to completion, or until reaching max steps.

        If your model runs in a non-standard way, this is the method to modify
        in your subclass.
        """
        while model.running and model.schedule.steps < self.max_steps:
            model.step()

        if hasattr(model, "datacollector"):
            return model.datacollector
        else:
            return None

    def collect_model_vars(self, model):
        """Run reporters and collect model-level variables."""
        model_vars = {
            var: reporter(model) for var, reporter in self.model_reporters.items()
        }
        return model_vars

    def collect_agent_vars(self, model):
        """Run reporters and collect agent-level variables."""
        agent_vars = {}
        for agent in model.schedule._agents.values():
            agent_record = {
                var: getattr(agent, reporter)
                for var, reporter in self.agent_reporters.items()
            }
            agent_vars[agent.unique_id] = agent_record
        return agent_vars

    def get_model_vars_dataframe(self):
        """Generate a pandas DataFrame from the model-level variables
        collected.
        """

        return self._prepare_report_table(self.model_vars)

    def get_agent_vars_dataframe(self):
        """Generate a pandas DataFrame from the agent-level variables
        collected.
        """

        return self._prepare_report_table(self.agent_vars, extra_cols=["AgentId"])

    def get_collector_model(self):
        """
        Passes pandas dataframes from datacollector module in dictionary format of model reporters
        :return: dict {(Param1, Param2,...,iteration): <DataCollector Pandas DataFrame>}
        """

        return self.datacollector_model_reporters

    def get_collector_agents(self):
        """
        Passes pandas dataframes from datacollector module in dictionary format of agent reporters
        :return: dict {(Param1, Param2,...,iteration): <DataCollector Pandas DataFrame>}
        """
        return self.datacollector_agent_reporters

    def _prepare_report_table(self, vars_dict, extra_cols=None):
        """
        Creates a dataframe from collected records and sorts it using 'Run'
        column as a key.
        """
        extra_cols = ["Run"] + (extra_cols or [])
        index_cols = []
        if self.parameters_list:
            index_cols = list(self.parameters_list[0].keys())
        index_cols += extra_cols

        records = []
        for param_key, values in vars_dict.items():
            record = dict(zip(index_cols, param_key))
            record.update(values)
            records.append(record)

        df = pd.DataFrame(records)
        rest_cols = set(df.columns) - set(index_cols)
        ordered = df[index_cols + sorted(rest_cols)]
        ordered.sort_values(by="Run", inplace=True)
        if self._include_fixed:
            for param, val in self.fixed_parameters.items():
                # avoid error when val is an iterable
                vallist = [val for i in range(ordered.shape[0])]
                ordered[param] = vallist
        return ordered


class ParameterProduct:
    def __init__(self, variable_parameters):
        self.param_names, self.param_lists = zip(
            *(copy.deepcopy(variable_parameters)).items()
        )
        self._product = product(*self.param_lists)

    def __iter__(self):
        return self

    def __next__(self):
        return dict(zip(self.param_names, next(self._product)))


# Roughly inspired by sklearn.model_selection.ParameterSampler.  Does not handle
# distributions, only lists.
class ParameterSampler:
    def __init__(self, parameter_lists, n, random_state=None):
        self.param_names, self.param_lists = zip(
            *(copy.deepcopy(parameter_lists)).items()
        )
        self.n = n
        if random_state is None:
            self.random_state = random.Random()
        elif isinstance(random_state, int):
            self.random_state = random.Random(random_state)
        else:
            self.random_state = random_state
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.count <= self.n:
            return dict(
                zip(
                    self.param_names,
                    [self.random_state.choice(p_list) for p_list in self.param_lists],
                )
            )
        raise StopIteration()


class BatchRunner(FixedBatchRunner):
    """DEPRECATION WARNING: BatchRunner Class has been replaced batch_run function
    This class is instantiated with a model class, and model parameters
    associated with one or more values. It is also instantiated with model and
    agent-level reporters, dictionaries mapping a variable name to a function
    which collects some data from the model or its agents at the end of the run
    and stores it.

    Note that by default, the reporters only collect data at the *end* of the
    run. To get step by step data, simply have a reporter store the model's
    entire DataCollector object.
    """

    def __init__(
        self,
        model_cls,
        variable_parameters=None,
        fixed_parameters=None,
        iterations=1,
        max_steps=1000,
        model_reporters=None,
        agent_reporters=None,
        display_progress=True,
    ):
        """Create a new BatchRunner for a given model with the given
        parameters.

        Args:
            model_cls: The class of model to batch-run.
            variable_parameters: Dictionary of parameters to lists of values.
                The model will be run with every combo of these parameters.
                For example, given variable_parameters of
                    {"param_1": range(5),
                     "param_2": [1, 5, 10]}
                models will be run with {param_1=1, param_2=1},
                    {param_1=2, param_2=1}, ..., {param_1=4, param_2=10}.
            fixed_parameters: Dictionary of parameters that stay same through
                all batch runs. For example, given fixed_parameters of
                    {"constant_parameter": 3},
                every instantiated model will be passed constant_parameter=3
                as a kwarg.
            iterations: The total number of times to run the model for each
                combination of parameters.
            max_steps: Upper limit of steps above which each run will be halted
                if it hasn't halted on its own.
            model_reporters: The dictionary of variables to collect on each run
                at the end, with variable names mapped to a function to collect
                them. For example:
                    {"agent_count": lambda m: m.schedule.get_agent_count()}
            agent_reporters: Like model_reporters, but each variable is now
                collected at the level of each agent present in the model at
                the end of the run.
            display_progress: Display progress bar with time estimation?
        """
        warn(
            "BatchRunner class has been replaced by batch_run function. Please see documentation.",
            DeprecationWarning,
            2,
        )
        if variable_parameters is None:
            super().__init__(
                model_cls,
                variable_parameters,
                fixed_parameters,
                iterations,
                max_steps,
                model_reporters,
                agent_reporters,
                display_progress,
            )
        else:
            super().__init__(
                model_cls,
                ParameterProduct(variable_parameters),
                fixed_parameters,
                iterations,
                max_steps,
                model_reporters,
                agent_reporters,
                display_progress,
            )


class BatchRunnerMP(BatchRunner):  # pragma: no cover
    """DEPRECATION WARNING: BatchRunner class has been replaced by batch_run
    Child class of BatchRunner, extended with multiprocessing support."""

    def __init__(self, model_cls, nr_processes=None, **kwargs):
        """Create a new BatchRunnerMP for a given model with the given
        parameters.

        model_cls: The class of model to batch-run.
        nr_processes: int
                      the number of separate processes the BatchRunner
                      should start, all running in parallel.
        kwargs: the kwargs required for the parent BatchRunner class
        """
        warn(
            "BatchRunnerMP class has been replaced by batch_run function. Please see documentation.",
            DeprecationWarning,
            2,
        )
        if nr_processes is None:
            # identify the number of processors available on users machine
            available_processors = cpu_count()
            self.processes = available_processors
            print(f"BatchRunner MP will use {self.processes} processors.")
        else:
            self.processes = nr_processes

        super().__init__(model_cls, **kwargs)
        self.pool = Pool(self.processes)

    def _make_model_args_mp(self):
        """Prepare all combinations of parameter values for `run_all`
        Due to multiprocessing requirements of @StaticMethod takes different input, hence the similar function
        Returns:
            List of list with the form:
            [[model_object, dictionary_of_kwargs, max_steps, iterations]]
        """
        total_iterations = self.iterations
        all_kwargs = []

        count = len(self.parameters_list)
        if count:
            for params in self.parameters_list:
                kwargs = params.copy()
                kwargs.update(self.fixed_parameters)
                # run each iterations specific number of times
                for iter in range(self.iterations):
                    kwargs_repeated = kwargs.copy()
                    all_kwargs.append(
                        [self.model_cls, kwargs_repeated, self.max_steps, iter]
                    )

        elif len(self.fixed_parameters):
            count = 1
            kwargs = self.fixed_parameters.copy()
            all_kwargs.append(kwargs)

        total_iterations *= count

        return all_kwargs, total_iterations

    @staticmethod
    def _run_wrappermp(iter_args):
        """
        Based on requirement of Python multiprocessing requires @staticmethod decorator;
        this is primarily to ensure functionality on Windows OS and does not impact MAC or Linux distros

        :param iter_args: List of arguments for model run
            iter_args[0] = model object
            iter_args[1] = key word arguments needed for model object
            iter_args[2] = maximum number of steps for model
            iter_args[3] = number of time to run model for stochastic/random variation with same parameters
        :return:
            tuple of param values which serves as a unique key for model results
            model object
        """

        model_i = iter_args[0]
        kwargs = iter_args[1]
        max_steps = iter_args[2]
        iteration = iter_args[3]

        # instantiate version of model with correct parameters
        model = model_i(**kwargs)
        while model.running and model.schedule.steps < max_steps:
            model.step()

        # add iteration number to dictionary to make unique_key
        kwargs["iteration"] = iteration

        # convert kwargs dict to tuple to  make consistent
        param_values = tuple(kwargs.values())

        return param_values, model

    def _result_prep_mp(self, results):
        """
        Helper Function
        :param results: Takes results dictionary from Processpool and single processor debug run and fixes format to
        make compatible with BatchRunner Output
        :updates model_vars and agents_vars so consistent across all batchrunner
        """
        # Take results and convert to dictionary so dataframe can be called
        for model_key, model in results.items():
            if self.model_reporters:
                self.model_vars[model_key] = self.collect_model_vars(model)
            if self.agent_reporters:
                agent_vars = self.collect_agent_vars(model)
                for agent_id, reports in agent_vars.items():
                    agent_key = (*model_key, agent_id)
                    self.agent_vars[agent_key] = reports
            if hasattr(model, "datacollector"):
                if model.datacollector.model_reporters is not None:
                    self.datacollector_model_reporters[
                        model_key
                    ] = model.datacollector.get_model_vars_dataframe()
                if model.datacollector.agent_reporters is not None:
                    self.datacollector_agent_reporters[
                        model_key
                    ] = model.datacollector.get_agent_vars_dataframe()

        # Make results consistent
        if len(self.datacollector_model_reporters) == 0:
            self.datacollector_model_reporters = None
        if len(self.datacollector_agent_reporters) == 0:
            self.datacollector_agent_reporters = None

    def run_all(self):
        """
        Run the model at all parameter combinations and store results,
        overrides run_all from BatchRunner.
        """

        run_iter_args, total_iterations = self._make_model_args_mp()
        # register the process pool and init a queue
        # store results in ordered dictionary
        results = {}

        if self.processes > 1:
            with tqdm(total_iterations, disable=not self.display_progress) as pbar:
                for params, model in self.pool.imap_unordered(
                    self._run_wrappermp, run_iter_args
                ):
                    results[params] = model
                    pbar.update()

                self._result_prep_mp(results)
        # For debugging model due to difficulty of getting errors during multiprocessing
        else:
            for run in run_iter_args:
                params, model_data = self._run_wrappermp(run)
                results[params] = model_data

            self._result_prep_mp(results)

        # Close multi-processing
        self.pool.close()

        return (
            getattr(self, "model_vars", None),
            getattr(self, "agent_vars", None),
            getattr(self, "datacollector_model_reporters", None),
            getattr(self, "datacollector_agent_reporters", None),
        )
