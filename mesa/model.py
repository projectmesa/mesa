"""
The model class for Mesa framework.

Core Objects: Model
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import itertools
import random
from collections import defaultdict

# mypy
from typing import Any

from mesa.agent import Agent, AgentSet
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
        _agents: A defaultdict mapping each agent type to a dict of its instances.
                 This private attribute is used internally to manage agents.

    Properties:
        agents: An AgentSet containing all agents in the model, generated from the _agents attribute.
        agent_types: A list of different agent types present in the model.

    Methods:
        get_agents_of_type: Returns an AgentSet of agents of the specified type.
        run_model: Runs the model's simulation until a defined end condition is reached.
        step: Executes a single step of the model's simulation process.
        next_id: Generates and returns the next unique identifier for an agent.
        reset_randomizer: Resets the model's random number generator with a new or existing seed.
        initialize_data_collector: Sets up the data collector for the model, requiring an initialized scheduler and agents.
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
        self._agents: defaultdict[type, dict] = defaultdict(dict)

        # Warning flags for current experimental features. These make sure a warning is only printed once per model.
        self.agentset_experimental_warning_given = False

    @property
    def agents(self) -> AgentSet:
        """Provides an AgentSet of all agents in the model, combining agents from all types."""
        all_agents = itertools.chain(
            *(agents_by_type.keys() for agents_by_type in self._agents.values())
        )
        return AgentSet(all_agents, self)

    @property
    def agent_types(self) -> list[type]:
        """Return a list of different agent types."""
        return list(self._agents.keys())

    def get_agents_of_type(self, agenttype: type[Agent]) -> AgentSet:
        """Retrieves an AgentSet containing all agents of the specified type."""
        return AgentSet(self._agents[agenttype].keys(), self)

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
