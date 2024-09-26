"""The model class for Mesa framework.

Core Objects: Model
"""

# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import random
import warnings

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
        steps: the number of times `model.step()` has been called.
        random: a seeded random number generator.

    Notes:
        Model.agents returns the AgentSet containing all agents registered with the model. Changing
        the content of the AgentSet directly can result in strange behavior. If you want change the
        composition of this AgentSet, ensure you operate on a copy.

    """

    def __init__(self, *args: Any, seed: float | None = None, **kwargs: Any) -> None:
        """Create a new model.

        Overload this method with the actual code to initialize the model. Always start with super().__init__()
        to initialize the model object properly.

        Args:
            args: arguments to pass onto super
            seed: the seed for the random number generator
            kwargs: keyword arguments to pass onto super
        """
        self.running = True
        self.schedule = None
        self.steps: int = 0

        self._setup_agent_registration()

        self._seed = seed
        if self._seed is None:
            # We explicitly specify the seed here so that we know its value in
            # advance.
            self._seed = random.random()
        self.random = random.Random(self._seed)

        # Wrap the user-defined step method
        self._user_step = self.step
        self.step = self._wrapped_step

    def _wrapped_step(self, *args: Any, **kwargs: Any) -> None:
        """Automatically increments time and steps after calling the user's step method."""
        # Automatically increment time and step counters
        self.steps += 1
        # Call the original user-defined step method
        self._user_step(*args, **kwargs)

    def next_id(self) -> int:  # noqa: D102
        warnings.warn(
            "using model.next_id() is deprecated. Agents track their unique ID automatically",
            DeprecationWarning,
            stacklevel=2,
        )
        return 0

    @property
    def agents(self) -> AgentSet:
        """Provides an AgentSet of all agents in the model, combining agents from all types."""
        return self._all_agents

    @agents.setter
    def agents(self, agents: Any) -> None:
        raise AttributeError(
            "You are trying to set model.agents. In Mesa 3.0 and higher, this attribute is "
            "used by Mesa itself, so you cannot use it directly anymore."
            "Please adjust your code to use a different attribute name for custom agent storage."
        )

    @property
    def agent_types(self) -> list[type]:
        """Return a list of all unique agent types registered with the model."""
        return list(self._agents_by_type.keys())

    @property
    def agents_by_type(self) -> dict[type[Agent], AgentSet]:
        """A dictionary where the keys are agent types and the values are the corresponding AgentSets."""
        return self._agents_by_type

    def get_agents_of_type(self, agenttype: type[Agent]) -> AgentSet:
        """Deprecated: Retrieves an AgentSet containing all agents of the specified type."""
        warnings.warn(
            f"Model.get_agents_of_type() is deprecated, please replace get_agents_of_type({agenttype})"
            f"with the property agents_by_type[{agenttype}].",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.agents_by_type[agenttype]

    def _setup_agent_registration(self):
        """Helper method to initialize the agent registration datastructures."""
        self._agents = {}  # the hard references to all agents in the model
        self._agents_by_type: dict[
            type[Agent], AgentSet
        ] = {}  # a dict with an agentset for each class of agents
        self._all_agents = AgentSet([], self)  # an agenset with all agents

    def register_agent(self, agent):
        """Register the agent with the model.

        Args:
            agent: The agent to register.

        Notes:
            This method is called automatically by ``Agent.__init__``, so there is no need to use this
            if you are subclassing Agent and calling its super in the ``__init__`` method.

        """
        if not hasattr(self, "_agents"):
            self._setup_agent_registration()

            warnings.warn(
                "The Mesa Model class was not initialized. In the future, you need to explicitly initialize "
                "the Model by calling super().__init__() on initialization.",
                FutureWarning,
                stacklevel=2,
            )

        self._agents[agent] = None

        # because AgentSet requires model, we cannot use defaultdict
        # tricks with a function won't work because model then cannot be pickled
        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet(
                [
                    agent,
                ],
                self,
            )

        self._all_agents.add(agent)

    def deregister_agent(self, agent):
        """Deregister the agent with the model.

        Args:
            agent: The agent to deregister.

        Notes:
            This method is called automatically by ``Agent.remove``

        """
        del self._agents[agent]
        self._agents_by_type[type(agent)].remove(agent)
        self._all_agents.remove(agent)

    def run_model(self) -> None:
        """Run the model until the end condition is reached.

        Overload as needed.
        """
        while self.running:
            self.step()

    def step(self) -> None:
        """A single step. Fill in here."""

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
        agenttype_reporters=None,
        tables=None,
    ) -> None:
        """Initialize the data collector for the model.

        Args:
            model_reporters: model reporters to collect
            agent_reporters: agent reporters to collect
            agenttype_reporters: agent type reporters to collect
            tables: tables to collect

        """
        warnings.warn(
            "initialize_data_collector() is deprecated. Please use the DataCollector class directly. "
            "by using `self.datacollector = DataCollector(...)`.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters,
            agenttype_reporters=agenttype_reporters,
            tables=tables,
        )
        # Collect data for the first time during initialization.
        self.datacollector.collect(self)
