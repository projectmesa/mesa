"""
The model class for Mesa framework.

Core Objects: Model
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import random
import numpy as np

from mesa.datacollection import DataCollector

# mypy
from typing import Any


class Model:
    """Base class for models."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create a new model object and instantiate its RNGs automatically."""
        obj = object.__new__(cls)
        obj._seed = kwargs.get("seed", None)
        obj.random = random.Random(obj._seed)
        obj.np_rng = np.random.default_rng(np.random.MT19937())
        obj._set_jumped_state_np_rng()
        return obj

    def _set_jumped_state_np_rng(self) -> None:
        py_rng_state = self.random.getstate()
        np_key = np.asarray(py_rng_state[1][:-1], dtype=np.uint32)
        np_pos = py_rng_state[1][-1]
        np_rng_state = {
            "bit_generator": "MT19937",
            "state": {"key": np_key, "pos": np_pos},
        }
        self.np_rng.bit_generator.state = np_rng_state
        jumped_bit_generator = self.np_rng.bit_generator.jumped(1)
        self.np_rng = np.random.default_rng(jumped_bit_generator)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a new model. Overload this method with the actual code to
        start the model.

        Attributes:
            schedule: schedule object
            running: a bool indicating if the model should continue running
        """

        self.running = True
        self.schedule = None
        self.current_id = 0

    def run_model(self) -> None:
        """Run the model until the end condition is reached. Overload as
        needed.
        """
        while self.running:
            self.step()

    def step(self) -> None:
        """A single step. Fill in here."""
        pass

    def next_id(self) -> int:
        """Return the next unique ID for agents, increment current_id"""
        self.current_id += 1
        return self.current_id

    def reset_randomizer(self, seed: int | None = None) -> None:
        """Reset the model random number generators.

        Args:
            seed: A new seed for the RNGs; if None, reset using the current seed
        """

        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed
        self._set_jumped_state_np_rng()

    def initialize_data_collector(
        self, model_reporters=None, agent_reporters=None, tables=None
    ) -> None:
        if not hasattr(self, "schedule") or self.schedule is None:
            raise RuntimeError(
                "You must initialize the scheduler (self.schedule) before initializing the data collector."
            )
        if self.schedule.get_agent_count() == 0:
            raise RuntimeError(
                "You must add agents to the scheduler before initializing the data collector."
            )
        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters,
            tables=tables,
        )
        # Collect data for the first time during initialization.
        self.datacollector.collect(self)
