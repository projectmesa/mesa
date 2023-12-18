"""
The model class for Mesa framework.

Core Objects: Model
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import random
from collections import defaultdict

# mypy
from typing import Any, Callable

from mesa.datacollection import DataCollector


class Model:
    """Base class for models in the Mesa ABM library.

    This class serves as a foundational structure for creating agent-based models.
    It includes the basic attributes and methods necessary for initializing and
    running a simulation model.

    Attributes:
        running: A boolean indicating if the model should continue running.
        schedule: An object to manage the order and execution of agent steps.
        current_id: A counter for assigning unique IDs to agents.
        agents: A defaultdict mapping each agent type to a dict of its instances.
                Agent instances are saved in the nested dict keys, with the values being None.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create a new model object and instantiate its RNG automatically."""
        obj = object.__new__(cls)
        obj._seed = kwargs.get("seed")
        if obj._seed is None:
            # We explicitly specify the seed here so that we know its value in
            # advance.
            obj._seed = random.random()  # noqa: S311
        obj.random = random.Random(obj._seed)
        return obj

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a new model. Overload this method with the actual code to
        start the model. Always start with super().__init__() to initialize the
        model object properly.
        """

        self.running = True
        self.schedule = None
        self.current_id = 0
        self.agents: defaultdict[type, dict] = defaultdict(dict)

    @property
    def agent_types(self) -> list:
        """Return a list of different agent types."""
        return list(self.agents.keys())

    def run_model(self) -> None:
        """Run the model until the end condition is reached. Overload as
        needed.
        """
        while self.running:
            self.step()

    def step(self) -> None:
        """A single step. Fill in here."""

    def next_id(self) -> int:
        """Return the next unique ID for agents, increment current_id"""
        self.current_id += 1
        return self.current_id

    def reset_randomizer(self, seed: int | None = None) -> None:
        """Reset the model random number generator.

        Args:
            seed: A new seed for the RNG; if None, reset using the current seed
        """

        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed

    def initialize_data_collector(
        self,
        model_reporters=None,
        agent_reporters=None,
        tables=None,
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

    def select_agents(
        self,
        n: int | None = None,
        sort: list[str] | None = None,
        direction: list[str] | None = None,
        filter_func: Callable[[Any], bool] | None = None,
        agent_type: type[Any] | list[type[Any]] | None = None,
        up_to: bool = True,
    ) -> list[Any]:
        """
        Select agents based on various criteria including type, attributes, and custom filters.

        Args:
            n: Number of agents to select.
            sort: Attributes to sort by.
            direction: Sort direction for each attribute in `sort`.
            filter_func: A callable to further filter agents.
            agent_type: Type(s) of agents to include.
            up_to: If True, allows returning up to `n` agents.

        Returns:
            A list of selected agents.
        """

        # If agent_type is specified, fetch only those agents; otherwise, fetch all
        if agent_type:
            if not isinstance(agent_type, list):
                agent_type = [agent_type]
            agent_type_set = set(agent_type)
            agents_iter = (
                agent
                for type_key, agents in self.agents.items()
                if type_key in agent_type_set
                for agent in agents
            )
        else:
            agents_iter = (agent for agents in self.agents.values() for agent in agents)

        # Apply functional filter if provided
        if filter_func:
            agents_iter = filter(filter_func, agents_iter)

        # Convert to list if sorting is needed or n is specified
        if sort and direction or n is not None:
            agents_iter = list(agents_iter)
            # If n is specified, shuffle the agents to avoid bias
            self.random.shuffle(agents_iter)

        # If only a specific number of agents is needed without sorting, limit early
        if n is not None and not (sort and direction):
            agents_iter = (
                agents_iter[: min(n, len(agents_iter))] if up_to else agents_iter[:n]
            )

        # Sort agents if needed
        if sort and direction:

            def sort_key(agent):
                return tuple(
                    getattr(agent, attr)
                    if dir.lower() == "lowest"
                    else -getattr(agent, attr)
                    for attr, dir in zip(sort, direction)
                )

            agents_iter.sort(key=sort_key)

        # Select the desired number of agents after sorting
        if n is not None and sort and direction:
            return agents_iter[: min(n, len(agents_iter))] if up_to else agents_iter[:n]

        return list(agents_iter)
