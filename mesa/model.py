"""The model class for Mesa framework.

Core Objects: Model
"""

from __future__ import annotations

import random
import sys
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from mesa.agent import Agent, AgentSet
from mesa.experimental.devs.eventlist import Priority, SimulationEvent
from mesa.experimental.devs.scheduler import Scheduler

SeedLike = int | np.integer | Sequence[int] | np.random.SeedSequence
RNGLike = np.random.Generator | np.random.BitGenerator


class Model:
    """Base class for models in the Mesa ABM library.

    This class serves as a foundational structure for creating agent-based models.
    It includes the basic attributes and methods necessary for initializing and
    running a simulation model.

    Attributes:
        running: A boolean indicating if the model should continue running.
        steps: The number of times `model.step()` has been called.
        time: The current simulation time.
        random: A seeded python.random number generator.
        rng: A seeded numpy.random.Generator.

    Notes:
        Model.agents returns the AgentSet containing all agents registered with
        the model. Changing the content of the AgentSet directly can result in
        strange behavior. If you want to change the composition of this AgentSet,
        ensure you operate on a copy.
    """

    def __init__(
        self,
        *args: Any,
        seed: float | None = None,
        rng: RNGLike | SeedLike | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a new model.

        Args:
            args: Arguments to pass onto super.
            seed: The seed for the random number generator.
            rng: Pseudorandom number generator state. When `rng` is None, a new
                `numpy.random.Generator` is created using entropy from the OS.
            kwargs: Keyword arguments to pass onto super.

        Notes:
            You have to pass either seed or rng, but not both.
        """
        super().__init__(*args, **kwargs)
        self.running: bool = True
        self.steps: int = 0
        self.time: float = 0.0

        # Initialize scheduler for event management
        self._scheduler = Scheduler(self)

        # Random number generator setup
        self._init_random(seed, rng)

        # Agent registration data structures
        self._agents = {}
        self._agents_by_type: dict[type[Agent], AgentSet] = {}
        self._all_agents = AgentSet([], random=self.random)

    def _init_random(self, seed: float | None, rng: RNGLike | SeedLike | None) -> None:
        """Initialize random number generators."""
        if (seed is not None) and (rng is not None):
            raise ValueError("you have to pass either rng or seed, not both")
        elif seed is None:
            self.rng: np.random.Generator = np.random.default_rng(rng)
            self._rng = self.rng.bit_generator.state
            try:
                self.random = random.Random(rng)
            except TypeError:
                seed = int(self.rng.integers(np.iinfo(np.int32).max))
                self.random = random.Random(seed)
            self._seed = seed
        else:
            self.random = random.Random(seed)
            self._seed = seed
            try:
                self.rng = np.random.default_rng(seed)
            except TypeError:
                rng = self.random.randint(0, sys.maxsize)
                self.rng = np.random.default_rng(rng)
            self._rng = self.rng.bit_generator.state

    # Event Scheduling API (delegates to Scheduler)
    def schedule(
        self,
        callback: Callable,
        *,
        at: float | None = None,
        after: float | None = None,
        priority: Priority = Priority.DEFAULT,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule an event to be executed at a specific time.

        Args:
            callback: The callable to execute for this event.
            at: Absolute time at which to execute the event.
            after: Time delta from now at which to execute the event.
            priority: Priority level for simultaneous events.
            args: Positional arguments for the callback.
            kwargs: Keyword arguments for the callback.

        Returns:
            SimulationEvent: The scheduled event (can be used to cancel).

        Examples:
            model.schedule(callback, at=50.0)
            model.schedule(callback, after=10.0)
            model.schedule(callback, at=50.0, priority=Priority.HIGH)
        """
        return self._scheduler.schedule(
            callback, at=at, after=after, priority=priority, args=args, kwargs=kwargs
        )

    def cancel(self, event: SimulationEvent) -> None:
        """Cancel a scheduled event.

        Args:
            event: The event to cancel.
        """
        self._scheduler.cancel(event)

    # Running API (delegates to Scheduler)
    def run(
        self,
        *,
        until: float | None = None,
        duration: float | None = None,
        steps: int | None = None,
        condition: Callable[[Model], bool] | None = None,
    ) -> None:
        """Run the model.

        Args:
            until: Run until simulation time reaches this value.
            duration: Run for this many time units from current time.
            steps: Run for this many steps (each step = 1.0 time units).
            condition: Run while this condition returns True.

        Examples:
            model.run(until=100)
            model.run(duration=50)
            model.run(steps=100)
            model.run(condition=lambda m: m.running)
        """
        self._scheduler.run(
            until=until, duration=duration, steps=steps, condition=condition
        )

    def step(self) -> None:
        """A single step of the model. Override this in subclasses."""

    def run_model(self) -> None:
        """Run the model until running is False.

        Deprecated: Use run(condition=lambda m: m.running) instead.
        """
        self.run(condition=lambda m: m.running)

    # Agent Management
    @property
    def agents(self) -> AgentSet:
        """Provides an AgentSet of all agents in the model."""
        return self._all_agents

    @agents.setter
    def agents(self, agents: Any) -> None:
        raise AttributeError(
            "You are trying to set model.agents. In Mesa 3.0 and higher, "
            "this attribute is used by Mesa itself, so you cannot use it "
            "directly anymore. Please use a different attribute name."
        )

    @property
    def agent_types(self) -> list[type]:
        """Return a list of all unique agent types registered with the model."""
        return list(self._agents_by_type.keys())

    @property
    def agents_by_type(self) -> dict[type[Agent], AgentSet]:
        """A dictionary where keys are agent types and values are AgentSets."""
        return self._agents_by_type

    def register_agent(self, agent: Agent) -> None:
        """Register the agent with the model.

        Args:
            agent: The agent to register.

        Notes:
            This method is called automatically by Agent.__init__.
        """
        self._agents[agent] = None
        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet([agent], random=self.random)
        self._all_agents.add(agent)

    def deregister_agent(self, agent: Agent) -> None:
        """Deregister the agent with the model.

        Args:
            agent: The agent to deregister.

        Notes:
            This method is called automatically by Agent.remove().
        """
        del self._agents[agent]
        self._agents_by_type[type(agent)].remove(agent)
        self._all_agents.remove(agent)

    def remove_all_agents(self) -> None:
        """Remove all agents from the model."""
        for agent in list(self._agents.keys()):
            agent.remove()

    # Random Number Generator Management
    def reset_randomizer(self, seed: int | None = None) -> None:
        """Reset the model random number generator.

        Args:
            seed: A new seed for the RNG; if None, reset using the current seed.
        """
        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed

    def reset_rng(self, rng: RNGLike | SeedLike | None = None) -> None:
        """Reset the numpy random number generator.

        Args:
            rng: A new seed for the RNG; if None, reset using the current seed.
        """
        self.rng = np.random.default_rng(rng)
        self._rng = self.rng.bit_generator.state
