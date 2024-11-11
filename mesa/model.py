"""The model class for Mesa framework.

Core Objects: Model
"""

# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import random
import sys
import warnings
from collections.abc import Sequence

# mypy
from typing import Any

import numpy as np

from mesa.agent import Agent, AgentSet
from mesa.datacollection import DataCollector

SeedLike = int | np.integer | Sequence[int] | np.random.SeedSequence
RNGLike = np.random.Generator | np.random.BitGenerator


class Model:
    """Base class for models in the Mesa ABM library.

    This class serves as a foundational structure for creating agent-based models.
    It includes the basic attributes and methods necessary for initializing and
    running a simulation model.

    Attributes:
        running: A boolean indicating if the model should continue running.
        schedule: An object to manage the order and execution of agent steps.
        steps: the number of times `model.step()` has been called.
        random: a seeded python.random number generator.
        rng : a seeded numpy.random.Generator

    Notes:
        Model.agents returns the AgentSet containing all agents registered with the model. Changing
        the content of the AgentSet directly can result in strange behavior. If you want change the
        composition of this AgentSet, ensure you operate on a copy.

    """

    def __init__(
        self,
        *args: Any,
        seed: float | None = None,
        rng: RNGLike | SeedLike | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a new model.

        Overload this method with the actual code to initialize the model. Always start with super().__init__()
        to initialize the model object properly.

        Args:
            args: arguments to pass onto super
            seed: the seed for the random number generator
            rng : Pseudorandom number generator state. When `rng` is None, a new `numpy.random.Generator` is created
                  using entropy from the operating system. Types other than `numpy.random.Generator` are passed to
                  `numpy.random.default_rng` to instantiate a `Generator`.
            kwargs: keyword arguments to pass onto super

        Notes:
            you have to pass either seed or rng, but not both.

        """
        super().__init__(*args, **kwargs)
        self.running = True
        self.steps: int = 0

        if (seed is not None) and (rng is not None):
            raise ValueError("you have to pass either rng or seed, not both")
        elif seed is None:
            self.rng: np.random.Generator = np.random.default_rng(rng)
            self._rng = (
                self.rng.bit_generator.state
            )  # this allows for reproducing the rng

            try:
                self.random = random.Random(rng)
            except TypeError:
                seed = int(self.rng.integers(np.iinfo(np.int32).max))
                self.random = random.Random(seed)
            self._seed = seed  # this allows for reproducing stdlib.random
        elif rng is None:
            self.random = random.Random(seed)
            self._seed = seed  # this allows for reproducing stdlib.random

            try:
                self.rng: np.random.Generator = np.random.default_rng(rng)
            except TypeError:
                rng = self.random.randint(0, sys.maxsize)
                self.rng: np.random.Generator = np.random.default_rng(rng)
            self._rng = self.rng.bit_generator.state

        # Wrap the user-defined step method
        self._user_step = self.step
        self.step = self._wrapped_step

        # setup agent registration data structures
        self._setup_agent_registration()

    def _wrapped_step(self, *args: Any, **kwargs: Any) -> None:
        """Automatically increments time and steps after calling the user's step method."""
        # Automatically increment time and step counters
        self.steps += 1
        # Call the original user-defined step method
        self._user_step(*args, **kwargs)

    def next_id(self) -> int:  # noqa: D102
        warnings.warn(
            "using model.next_id() is deprecated and will be removed in Mesa 3.1. Agents track their unique ID automatically",
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
            f"Model.get_agents_of_type() is deprecated and will be removed in Mesa 3.1."
            f"Please replace get_agents_of_type({agenttype}) with the property agents_by_type[{agenttype}].",
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
        self._all_agents = AgentSet(
            [], random=self.random
        )  # an agenset with all agents

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
                random=self.random,
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

    def reset_rng(self, rng: RNGLike | SeedLike | None = None) -> None:
        """Reset the model random number generator.

        Args:
            rng: A new seed for the RNG; if None, reset using the current seed
        """
        self.rng = np.random.default_rng(rng)
        self._rng = self.rng.bit_generator.state

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
            "initialize_data_collector() is deprecated and will be removed in Mesa 3.1. Please use the DataCollector class directly. "
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

    def remove_all_agents(self):
        """Remove all agents from the model.

        Notes:
            This method calls agent.remove for all agents in the model. If you need to remove agents from
            e.g., a SingleGrid, you can either explicitly implement your own agent.remove method or clean this up
            near where you are calling this method.

        """
        # we need to wrap keys in a list to avoid a RunTimeError: dictionary changed size during iteration
        for agent in list(self._agents.keys()):
            agent.remove()
