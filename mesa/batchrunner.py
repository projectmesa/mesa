# -*- coding: utf-8 -*-
"""
Batchrunner
===========

A single class to manage a batch run or parameter sweep of a given model.

"""
import collections
import copy
from itertools import product, count
import pandas as pd
from tqdm import tqdm


def combinations(*items):
    """
    A small fix to handle dictionary type parameters in cartesian product.
    """
    prepared = [(item,) if isinstance(item, collections.Mapping) else item
                for item in items]
    yield from (param for param in product(*prepared))


class VariableParameterError(TypeError):
    MESSAGE = ('variable_parameters must map a name to a sequence of values. '
            'These parameters were given with non-sequence values: {}')

    def __init__(self, bad_names):
        self.bad_names = bad_names

    def __str__(self):
        return self.MESSAGE.format(self.bad_names)


class BatchRunner:
    """ This class is instantiated with a model class, and model parameters
    associated with one or more values. It is also instantiated with model and
    agent-level reporters, dictionaries mapping a variable name to a function
    which collects some data from the model or its agents at the end of the run
    and stores it.

    Note that by default, the reporters only collect data at the *end* of the
    run. To get step by step data, simply have a reporter store the model's
    entire DataCollector object.

    """
    def __init__(self, model_cls, variable_parameters=None,
            fixed_parameters=None, iterations=1, max_steps=1000,
            model_reporters=None, agent_reporters=None, display_progress=True):
        """ Create a new BatchRunner for a given model with the given
        parameters.

        Args:
            model_cls: The class of model to batch-run.
            variable_parameters: Dictionary of parameters to lists of values.
                The model will be run with every combination of these paramters.
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
            max_steps: The upper limit of steps above which each run will be halted
                if it hasn't halted on its own.
            model_reporters: The dictionary of variables to collect on each run at
                the end, with variable names mapped to a function to collect
                them. For example:
                    {"agent_count": lambda m: m.schedule.get_agent_count()}
            agent_reporters: Like model_reporters, but each variable is now
                collected at the level of each agent present in the model at
                the end of the run.
            display_progress: Display progresss bar with time estimation?

        """
        self.model_cls = model_cls
        self.variable_parameters = self._process_parameters(variable_parameters)
        self.fixed_parameters = fixed_parameters or {}
        self.iterations = iterations
        self.max_steps = max_steps

        self.model_reporters = model_reporters
        self.agent_reporters = agent_reporters

        if self.model_reporters:
            self.model_vars = {}

        if self.agent_reporters:
            self.agent_vars = {}

        self.display_progress = display_progress

    def _process_parameters(self, params):
        params = copy.deepcopy(params)
        bad_names = []
        for name, values in params.items():
            if (isinstance(values, str) or
                    not hasattr(values, "__iter__")):
                bad_names.append(name)
        if bad_names:
            raise VariableParameterError(bad_names)
        return params

    def run_all(self):
        """ Run the model at all parameter combinations and store results. """
        param_names, param_ranges = zip(*self.variable_parameters.items())
        run_count = count()
        total_iterations = self.iterations
        for param_range in param_ranges:
            total_iterations *= len(param_range)
        with tqdm(total_iterations, disable=not self.display_progress) as pbar:
            for param_values in product(*param_ranges):
                kwargs = dict(zip(param_names, param_values))
                kwargs.update(self.fixed_parameters)
                model = self.model_cls(**kwargs)

                for _ in range(self.iterations):
                    self.run_model(model)
                    # Collect and store results:
                    model_key = param_values + (next(run_count),)
                    if self.model_reporters:
                        self.model_vars[model_key] = self.collect_model_vars(model)
                    if self.agent_reporters:
                        agent_vars = self.collect_agent_vars(model)
                        for agent_id, reports in agent_vars.items():
                            agent_key = model_key + (agent_id,)
                            self.agent_vars[agent_key] = reports
                    pbar.update()

    def run_model(self, model):
        """ Run a model object to completion, or until reaching max steps.

        If your model runs in a non-standard way, this is the method to modify
        in your subclass.

        """
        while model.running and model.schedule.steps < self.max_steps:
            model.step()

    def collect_model_vars(self, model):
        """ Run reporters and collect model-level variables. """
        model_vars = {}
        for var, reporter in self.model_reporters.items():
            model_vars[var] = reporter(model)
        return model_vars

    def collect_agent_vars(self, model):
        """ Run reporters and collect agent-level variables. """
        agent_vars = {}
        for agent in model.schedule.agents:
            agent_record = {}
            for var, reporter in self.agent_reporters.items():
                agent_record[var] = reporter(agent)
            agent_vars[agent.unique_id] = agent_record
        return agent_vars

    def get_model_vars_dataframe(self):
        """ Generate a pandas DataFrame from the model-level variables
        collected.

        """
        return self._prepare_report_table(self.model_vars)

    def get_agent_vars_dataframe(self):
        """ Generate a pandas DataFrame from the agent-level variables
        collected.

        """
        return self._prepare_report_table(self.agent_vars,
                extra_cols=['AgentId'])

    def _prepare_report_table(self, vars_dict, extra_cols=None):
        """
        Creates a dataframe from collected records and sorts it using 'Run'
        column as a key.
        """
        extra_cols = ['Run'] + (extra_cols or [])
        index_cols = list(self.variable_parameters.keys()) + extra_cols

        records = []
        for param_key, values in vars_dict.items():
            record = dict(zip(index_cols, param_key))
            record.update(values)
            records.append(record)

        df = pd.DataFrame(records)
        rest_cols = set(df.columns) - set(index_cols)
        ordered = df[index_cols + list(sorted(rest_cols))]
        ordered.sort_values(by='Run', inplace=True)
        return ordered
