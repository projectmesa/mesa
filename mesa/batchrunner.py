import inspect
import itertools
from collections.abc import Iterable, Mapping
from functools import partial
from multiprocessing import Pool
from typing import Any

from tqdm.auto import tqdm

from mesa.model import Model


def batch_run(
    model_cls: type[Model],
    parameters: Mapping[str, Any | Iterable[Any]],
    # We still retain the Optional[int] because users may set it to None (i.e. use all CPUs)
    number_processes: int | None = 1,
    iterations: int = 1,
    data_collection_period: int = -1,
    max_steps: int = 1000,
    display_progress: bool = True,
) -> list[dict[str, Any]]:
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

    results: list[dict[str, Any]] = []

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
    parameters: Mapping[str, Any | Iterable[Any]],
) -> list[dict[str, Any]]:
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
    model_cls: type[Model],
    run: tuple[int, int, dict[str, Any]],
    max_steps: int,
    data_collection_period: int,
) -> list[dict[str, Any]]:
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
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
        common_range: List[float] = [0.8, 1.25],
        specific_ranges: Optional[Dict[str, List[float]]] = None,
        ignore_parameters: Optional[List[str]] = None,
        relative_range: bool = True,
        iterations: int = 10,
        **kwargs
) -> List[Dict[str, Any]]:
    """
    Performs a sensitivity analysis on a given Mesa agent-based model class,
    exploring how changes in model parameters affect the model's behavior.
    This function allows for both relative and absolute variations in parameter values.

    Parameters
    ----------
    model_cls : Type[Model]
        The Mesa model class to be analyzed. Must be a subclass of mesa.Model.

    common_range : List[float], default=[0.8, 1.25]
        A list of multipliers (for relative range) or values (for absolute range)
        to be applied to each numeric parameter, unless overridden by specific_ranges.

    specific_ranges : Optional[Dict[str, List[float]]], default=None
        A dictionary mapping parameter names to lists of multipliers or values.
        These specific ranges override the common_range for the respective parameters.

    ignore_parameters : Optional[List[str]], default=None
        A list of parameter names to be excluded from the sensitivity analysis.

    relative_range : bool, default=True
        Determines whether the values in common_range and specific_ranges are
        treated as relative multipliers (True) or absolute values (False).
        Relative multipliers are multiplied by the default parameter value,
        while absolute values are used as-is.

    iterations : int, default=10
        The number of iterations to run for each parameter value. Is passed directly
        to the Mesa batch_run function.

    **kwargs
        Additional keyword arguments to be passed directly to the Mesa batch_run function.
        These can include 'iterations', 'max_steps', 'data_collection_period', etc.

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries, each representing the results of one model run.
        Each dictionary includes the parameter values used for that run and the
        data collected during the simulation.

    Notes
    -----
    - Only numeric parameters (integers and floats) are varied. Non-numeric parameters
      are ignored and set to their default values.
    - All input arguments of the Model should have default values.
    - For integer parameters, resulting values from relative variations are rounded
      to the nearest integer, and duplicate values are eliminated.
    - The function includes a default run (using the model's baseline parameters)
      for comparison with varied parameter runs.
    """
    # Check if all parameters of the model have default values
    model_parameters = inspect.signature(model_cls.__init__).parameters
    for name, param in model_parameters.items():
        if param.default is inspect.Parameter.empty and name != 'self':
            raise ValueError(f"All model parameters must have default values. "
                             f"The parameter '{name}' does not have a default value.")

    # Retrieve default parameter values from the model's constructor and check for missing defaults
    base_params = {}
    for k, v in inspect.signature(model_cls.__init__).parameters.items():
        if k == 'self' or k in (ignore_parameters or []):
            continue
        if v.default is inspect.Parameter.empty:
            raise ValueError(f"Input parameter '{k}' of {model_cls.__name__} does not have a default value, which is required for this local sensitivity analysis function.")
        base_params[k] = v.default

    # Filter out non-numeric parameters
    numeric_params = {k: v for k, v in base_params.items() if isinstance(v, (int, float))}

    # Generate parameter variations
    parameter_variations = {'default': base_params}  # Special entry for default run
    for param, default_value in numeric_params.items():
        # Apply specific range if available, otherwise use common range
        ranges = specific_ranges.get(param, common_range)

        if relative_range:
            # Relative range: multiply the default value by each value in the range
            varied_values = {default_value * multiplier for multiplier in ranges}
        else:
            # Absolute range: use the values directly
            varied_values = set(ranges)

        # Round integers and remove duplicates
        if isinstance(default_value, int):
            varied_values = {round(val) for val in varied_values}

        parameter_variations[param] = sorted(varied_values)

    # Prepare parameters for batch_run
    parameters = {param: values for param, values in parameter_variations.items()}

    # Execute batch run using the Mesa batch_run function
    return batch_run(
        model_cls=model_cls,
        parameters=parameters,
        iterations=iterations,
        **kwargs
    )
