"""
Batchrunner
===========

A single class to manage a batch run or parameter sweep of a given model.

"""
import itertools
import multiprocessing as mp
from functools import partial
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

from tqdm import tqdm

from mesa.model import Model

ParameterName = str
ParameterValue = Any
ModelParameters = Dict[ParameterName, ParameterValue]
ModelData = Any


def batch_run(
    model_cls: Type[Model],
    parameters: Dict[ParameterName, Union[ParameterValue, Iterable[ParameterValue]]],
    nr_processes: Optional[int] = 1,
    iterations: int = 1,
    max_steps: int = 1000,
    display_progress: bool = True,
) -> Dict[Tuple[ParameterValue], ModelData]:
    """Batch run a model."""

    kwargs_list = _make_model_kwargs(parameters)
    process_func = partial(
        _model_run_func, model_cls, max_steps=max_steps, reporter=None
    )

    total_iterations = len(kwargs_list) * iterations

    results = {}

    with tqdm(total_iterations, disable=not display_progress) as pbar:
        if nr_processes == 1:
            for kwargs in kwargs_list:
                params, data = process_func(kwargs)
                results[params] = data
                pbar.update()

        else:
            with mp.Pool(nr_processes) as p:
                for params, data in p.imap_unordered(process_func, kwargs_list):
                    results[params] = data
                    pbar.update()

    print(results)

    return results


def _make_model_kwargs(
    parameters: Dict[ParameterName, Union[ParameterValue, Iterable[ParameterValue]]]
) -> List[ModelParameters]:
    """Create model kwargs from parameters dictionary."""
    parameter_list = []
    for param, values in parameters.items():
        try:
            all_values = [(param, value) for value in values]
        except TypeError:
            all_values = [(param, values)]
        parameter_list.append(all_values)
    all_kwargs = itertools.product(*parameter_list)
    kwargs_list = [dict(kwargs) for kwargs in all_kwargs]
    return kwargs_list


def _model_run_func(
    model_cls: Type[Model], kwargs: ModelParameters, max_steps: int, reporter: Any
) -> Tuple[Tuple[ParameterValue], Any]:
    """Run a single model run."""
    model = model_cls(**kwargs)
    while model.running and model.schedule.steps < max_steps:
        model.step()

    params = tuple(kwargs.values())
    data = _collect_data(model, reporter)

    return params, data


def _collect_data(model: Model, reporter: Any) -> int:
    "stub that just returns the model hash, but should handle the reporters"
    return hash(model)

