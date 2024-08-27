"""
The model class for Mesa framework.

Core Objects: Model
"""

# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import random
import warnings
from collections import defaultdict

# mypy
from typing import Any

from mesa.agent import Agent, AgentSet
from mesa.datacollection import DataCollector

TimeT = float | int


class Model:
    """Base class for models in the Mesa ABM library.

    This class serves as a foundational structure for creating agent-based models.
    It includes the basic attributes and methods necessary for initializing and
    running a simulation model.

    Attributes:
        running: A boolean indicating if the model should continue running.
        schedule: An object to manage the order and execution of agent steps.
        current_id: A counter for assigning unique IDs to agents.
        agents_by_type: A defaultdict mapping each agent type to a dict of its instances.
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
            obj._seed = random.random()
        obj.random = random.Random(obj._seed)

        # TODO: Remove these 2 lines just before Mesa 3.0
        obj._steps = 0
        obj._time = 0
        return obj

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a new model. Overload this method with the actual code to
        start the model. Always start with super().__init__() to initialize the
        model object properly.
        """

        self.running = True
        self.schedule = None
        self.current_id = 0

        self._setup_agent_registration()

        self._steps: int = 0
        self._time: TimeT = 0  # the model's clock

    def _setup_agent_registration(self):
        def hack():
            return AgentSet([], self)

        self.agents_by_type: defaultdict[type, AgentSet] = defaultdict(hack)
        self._agents = {}
        self.all_agents = AgentSet([], self)

    @property
    def agents(self) -> AgentSet:
        """Provides an AgentSet of all agents in the model, combining agents from all types."""
        return self.all_agents

    @agents.setter
    def agents(self, agents: Any) -> None:
        raise AttributeError(
            "You are trying to set model.agents. In Mesa 3.0 and higher, this attribute will be "
            "used by Mesa itself, so you cannot use it directly anymore."
            "Please adjust your code to use a different attribute name for custom agent storage."
        )

    @property
    def agent_types(self) -> list[type]:
        """Return a list of different agent types."""
        return list(self.agents_by_type.keys())

    def get_agents_of_type(self, agenttype: type[Agent]) -> AgentSet:
        """Retrieves an AgentSet containing all agents of the specified type."""
        return self.agents_by_type[agenttype]

    def register_agent(self, agent):
        """Register the agent with the model

        Args:
            agent: The agent to register.

        Notes:
            This method is called automatically by ``Agent.__init__``, so there is no need to use this
            if you are subclassing Agent and calling its super in the ``__init__`` method.


        """
        if not hasattr(self, "_all_agents"):
            self._setup_agent_registration()

            warnings.warn(
                "The Mesa Model class was not initialized. In the future, you need to explicitly initialize "
                "the Model by calling super().__init__() on initialization.",
                FutureWarning,
                stacklevel=2,
            )

        self._agents[agent] = None
        self.agents_by_type[type(agent)].add(agent)
        self.all_agents.add(agent)

    def deregister_agent(self, agent):
        """Deregister the agent with the model

        Notes::
        This method is called automatically by ``Agent.remove``

        """
        del self._agents[agent]
        self.agents_by_type[type(agent)].remove(agent)
        self.all_agents.remove(agent)


    def run_model(self) -> None:
        """Run the model until the end condition is reached. Overload as
        needed.
        """
        while self.running:
            self.step()

    def step(self) -> None:
        """A single step. Fill in here."""

    def _advance_time(self, deltat: TimeT = 1):
        """Increment the model's steps counter and clock."""
        self._steps += 1
        self._time += deltat

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
