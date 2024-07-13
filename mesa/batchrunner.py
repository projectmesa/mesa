"""
This module provides a function for running batch simulations of agent-based models using the Mesa framework.
"""

import itertools
from collections.abc import Iterable, Mapping
from functools import partial
from multiprocessing import Pool
from typing import Any

from tqdm.auto import tqdm

from mesa import Model
from mesa.datacollection import DataCollector


def batch_run(
    model_cls: type[Model],
    parameters: Mapping[str, Any | Iterable[Any]],
    num_processes: int | None = 1,
    iterations: int = 1,
    data_collection_period: int = -1,
    max_steps: int = 1000,
    display_progress: bool = True,
) -> list[dict[str, Any]]:
    """
    Run a batch simulation of an agent-based model using the Mesa framework.

    Parameters
    ----------
    model_cls : type[Model]
        The model class to batch-run.
    parameters : Mapping[str, Any | Iterable[Any]]
        A dictionary with model parameters over which to run the model. You can either pass single values or iterables.
    num_processes : int, optional
        The number of processes to use for running the simulations. By default, 1. Set this to None to use all available CPUs.
    iterations : int, optional
        The number of iterations for each parameter combination. By default, 1.
    data_collection_period : int, optional
        The number of steps after which data gets collected. By default, -1 (end of episode).
    max_steps : int, optional
        The maximum number of model steps after which the model halts. By default, 1000.
    display_progress : bool, optional
        Whether to display the batch run progress. By default, True.

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries containing the results of the batch simulations.
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
        if num_processes == 1:
            for run in runs_list:
                data = process_func(run)
                results.extend(data)
                pbar.update()
        else:
            with Pool(num_processes) as p:
                for data in p.imap_unordered(process_func, runs_list):
                    results.extend(data)
                    pbar.update()

    return results


def _make_model_kwargs(
    parameters: Mapping[str, Any | Iterable[Any]],
) -> list[dict[str, Any]]:
    """
    Create model kwargs from parameters dictionary.

    Parameters
    ----------
    parameters : Mapping[str, Any | Iterable[Any]]
        Single or multiple values for each model parameter name.

    Returns
    -------
    list[dict[str, Any]]
        A list of all kwargs combinations.
    """
    parameter_list = []
    for param, values in parameters.items():
        if isinstance(values, str):
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
    """
    Run a single model run and collect model and agent data.

    Parameters
    ----------
    model_cls : type[Model]
        The model class to batch-run.
    run: tuple[int, int, dict[str, Any]]
        The run id, iteration number, and kwargs for this run.
    max_steps : int
        The maximum number of model steps after which the model halts.
    data_collection_period : int
        The number of steps after which data gets collected.

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries containing the model and agent data for this run.
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
        model_data, all_agents_data = _collect_data(model.datacollector, step)

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
    datacollector: DataCollector,
    step: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Collect model and agent data from a model using Mesa's datacollector.

    Parameters
    ----------
    datacollector : DataCollector
        The datacollector object for the model.
    step : int
        The current step of the simulation.

    Returns
    -------
    tuple[dict[str, Any], list[dict[str, Any]]]
        A tuple containing the model data and a list of agent data dictionaries.
    """
    model_data = {
        param: values[step] for param, values in datacollector.model_vars.items()
    }

    all_agents_data = []
    raw_agent_data = datacollector._agent_records.get(step, [])
    for data in raw_agent_data:
        agent_dict = {"AgentID": data[1]}
        agent_dict.update(zip(datacollector.agent_reporters, data[2:]))
        all_agents_data.append(agent_dict)
    return model_data, all_agents_data
