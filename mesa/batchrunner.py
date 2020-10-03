"""
Batchrunner
===========

A single class to manage a batch run or parameter sweep of a given model.

"""
import itertools
import multiprocessing as mp
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Type

from tqdm import tqdm

from mesa.model import Model


@dataclass
class BatchRunner:
    """Create a new BatchRunner for a given model with the given parameters.

    Args:
        model_cls: The class of model to batch-run.
        parameters: Dictionary of parameters to lists of values.
            The model will be run with every combo of these paramters.
            For example, given variable_parameters of
                {"param_1": range(5),
                "param_2": [1, 5, 10]}
            models will be run with {param_1=1, param_2=1},
                {param_1=2, param_2=1}, ..., {param_1=4, param_2=10}.
        iterations: The total number of times to run the model for each
            combination of parameters.
        max_steps: Upper limit of steps above which each run will be halted
            if it hasn't halted on its own.
        display_progress: Display progress bar with time estimation?
    """

    model_cls: Type[Model]
    parameters: Dict[str, Any]
    nr_processes: int = 1
    iterations: int = 1
    max_steps: int = 1000
    display_progress: bool = True

    def __post_init__(self) -> None:
        """Special method of data classes."""
        self.kwargs_list = self._make_model_kwargs()
        self.data: Dict[Tuple[Any], Any] = {}

    def _make_model_kwargs(self) -> List[Dict[str, Any]]:
        """Create model kwargs from parameters dict."""
        parameter_list = []
        for param, values in self.parameters.items():
            try:
                all_values = [(param, value) for value in values]
            except TypeError:
                all_values = [(param, values)]
            parameter_list.append(all_values)
        all_kwargs = itertools.product(*parameter_list)
        kwargs_list = [dict(kwargs) for kwargs in all_kwargs]
        return kwargs_list

    @staticmethod
    def run_model(
        args: Tuple[Type[Model], Dict[str, Any], int, int]
    ) -> Tuple[Any, Model]:
        model_cls, kwargs, max_steps, iteration = args
        # instantiate version of model with correct parameters
        model = model_cls(**kwargs)
        while model.running and model.schedule.steps < max_steps:
            model.step()

        params = tuple(kwargs.values()) + (iteration,)
        return params, model

    def collect_data(self, model: Model, params: Tuple[Any]) -> None:
        "stub that just stores the model hash, but should handle the reporters"
        self.data[params] = hash(model)

    def run_all(self) -> None:
        total_iterations = len(self.kwargs_list) * self.iterations
        iter_args = [
            (self.model_cls, kwargs, self.max_steps, iteration)
            for kwargs in self.kwargs_list
            for iteration in range(1, self.iterations + 1)
        ]

        with tqdm(total_iterations, disable=not self.display_progress) as pbar:
            if self.nr_processes == 1:
                for args in iter_args:
                    params, model = self.run_model(args)
                    self.collect_data(model, params)
                    pbar.update()

            else:
                with mp.Pool(self.nr_processes) as p:
                    for params, model in p.imap_unordered(self.run_model, iter_args):
                        self.collect_data(model, params)
                        pbar.update()

        print(self.data.items())
