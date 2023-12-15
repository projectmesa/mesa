import inspect
import itertools
from functools import partial
from multiprocessing import Pool
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

from tqdm.auto import tqdm

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


def local_sensitivity_analysis(
    model_cls: Type[Model],
    custom_ranges: Optional[Dict[str, Tuple[Any, Any]]] = None,
    variation_percent: float = 0.25,
    variation_steps: int = 1,
    variation_type: str = "relative",
    num_replications: int = 25,
    max_steps: int = 1000,
    data_collection_period: int = -1,
    display_progress: bool = True,
) -> List[Dict[str, Any]]:
    """
    Conducts a local sensitivity analysis on a Mesa agent-based model, examining the effects of parameter
    variations on model behavior. It supports both absolute and relative variations, and can handle custom
    parameter ranges. The function also includes a default run with the model's baseline parameters for comparison.

    Parameters
    ----------
    model_cls : Type[Model]
        The Mesa model class to be analyzed. Must be a subclass of mesa.Model.

    custom_ranges : Optional[Dict[str, Tuple[Any, Any]]], optional
        Custom parameter range tuples (min, max) for each parameter. Overrides default ranges calculated using
        variation_percent and variation_type.

    variation_percent : float, optional
        Percentage of the baseline parameter value used to calculate variation range. Represents fixed variation
        for 'absolute' type and percentage variation for 'relative' type.

    variation_steps : int, optional
        Number of incremental steps to vary each parameter above and below its baseline value, defining the
        granularity of the sensitivity analysis.

    variation_type : str, optional
        Specifies the variation method: 'absolute' for fixed amount variations or 'relative' for percentage-based
        variations of the parameter value.

    num_replications : int, optional
        Number of repetitions for each parameter configuration to address model stochasticity.

    max_steps : int, optional
        Maximum simulation steps for each parameter configuration run.

    data_collection_period : int, optional
        Interval of simulation steps for data collection. A value of -1 indicates end-of-simulation data collection.

    display_progress : bool, optional
        Enables a progress bar during the execution of the batch runs.

    Returns
    -------
    List[Dict[str, Any]]
        A collection of dictionaries, each representing the results from a single model run. Includes parameter
        values and collected data.

    Notes
    -----
    - Designed primarily for numeric parameters. Non-numeric parameters remain at their default values.
    - Automatically calculates step sizes for parameter variations based on the parameter type and specified range.
    - Custom ranges are recommended for parameters with extreme baseline values to prevent unrealistic values.
    - Includes a default run with baseline parameters to serve as a reference point for assessing the impact of
      parameter variations.
    """

    # Validate the variation type
    if variation_type not in ["absolute", "relative"]:
        raise ValueError("variation_type must be 'absolute' or 'relative'")

    # Retrieve default parameter values from the model's constructor
    base_params = {
        k: v.default
        for k, v in inspect.signature(model_cls.__init__).parameters.items()
        if v.default is not inspect.Parameter.empty
    }

    # Generate parameter variations including a default run
    parameter_variations = {'default_run': 'default'}  # Initialize with a default run entry
    for param, default_value in base_params.items():
        # Skip non-numeric parameters
        if not isinstance(default_value, (int, float)):
            continue

        # Initialize a set to hold the variation steps for the parameter
        steps = set()

        # Calculate variations based on the specified variation type
        if variation_type == "absolute":
            for step in range(-variation_steps, variation_steps + 1):
                variation = 1 + step * (variation_percent / variation_steps)
                new_value = default_value * variation
                steps.add(new_value)
        elif variation_type == "relative":
            for step in range(-variation_steps, variation_steps + 1):
                variation_amount = default_value * (variation_percent * step)
                new_value = default_value + variation_amount
                steps.add(new_value)

        # Sort and store the calculated steps for the parameter
        parameter_variations[param] = sorted(steps)

    # Print the configurations being run
    for param, values in parameter_variations.items():
        print(f"Running {param}: {values}")

    # Prepare parameters for batch_run, including the default run
    parameters = {param: list(values) if param != 'default_run' else base_params
                  for param, values in parameter_variations.items()}

    # Execute batch run using the Mesa batch_run function
    return batch_run(
        model_cls=model_cls,
        parameters=parameters,
        number_processes=None,  # Use all CPUs
        iterations=num_replications,
        max_steps=max_steps,
        data_collection_period=data_collection_period,
        display_progress=display_progress,
    )
