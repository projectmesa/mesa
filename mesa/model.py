"""The model class for Mesa framework.

Core Objects: Model
"""

from __future__ import annotations

import random
import sys
import warnings
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np

from mesa.agent import Agent, AgentSet
from mesa.experimental.devs.eventlist import Priority, SimulationEvent
from mesa.experimental.devs.scheduled import is_scheduled
from mesa.experimental.devs.scheduler import Scheduler

SeedLike = int | np.integer | Sequence[int] | np.random.SeedSequence
RNGLike = np.random.Generator | np.random.BitGenerator


class Model:
    """Base class for models in the Mesa ABM library.

    Attributes:
        running: A boolean indicating if the model should continue running.
        steps: The number of times `model.step()` has been called.
        time: The current simulation time.
        random: A seeded python.random number generator.
        rng: A seeded numpy.random.Generator.
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
            rng: Pseudorandom number generator state.
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

        # Set up legacy step wrapper if step exists but isn't @scheduled
        self._setup_step_handling()

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

    def _setup_step_handling(self) -> None:
        """Set up step method handling based on whether @scheduled is used."""
        # Check if subclass has overridden step
        step_method = getattr(self.__class__, "step", None)
        base_step = getattr(Model, "step", None)

        # If step is overridden and NOT decorated with @scheduled, use legacy mode
        if step_method is not None and step_method is not base_step:
            if not is_scheduled(step_method):
                # Legacy mode: wrap step to auto-increment time/steps
                self._user_step = self.step
                self._uses_legacy_step = True

                def wrapped_step(*args: Any, **kwargs: Any) -> None:
                    self.steps += 1
                    self.time += 1.0
                    self._user_step(*args, **kwargs)

                self.step = wrapped_step

                warnings.warn(
                    "Defining step() without @scheduled decorator is deprecated. "
                    "Add @scheduled decorator to your step method, or use "
                    "model.run() with explicit scheduling. "
                    "See the migration guide for details.",
                    PendingDeprecationWarning,
                    stacklevel=3,
                )
            else:
                self._uses_legacy_step = False
        else:
            self._uses_legacy_step = False

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
        # For legacy models, use simple loop
        if self._uses_legacy_step:
            if steps is not None:
                for _ in range(steps):
                    if not self.running:
                        break
                    if condition is not None and not condition(self):
                        break
                    self.step()
            elif until is not None:
                while self.time < until and self.running:
                    if condition is not None and not condition(self):
                        break
                    self.step()
            elif duration is not None:
                end_time = self.time + duration
                while self.time < end_time and self.running:
                    if condition is not None and not condition(self):
                        break
                    self.step()
            elif condition is not None:
                while self.running and condition(self):
                    self.step()
            else:
                raise ValueError(
                    "Specify at least one of: 'until', 'duration', 'steps', or 'condition'"
                )
        else:
            # New event-driven mode
            self._scheduler.run(
                until=until, duration=duration, steps=steps, condition=condition
            )

    def step(self) -> None:
        """A single step of the model. Override this in subclasses."""

    def run_model(self) -> None:
        """Run the model until running is False.

        Deprecated:
            Use model.run(condition=lambda m: m.running) instead.
        """
        warnings.warn(
            "run_model() is deprecated. Use model.run(condition=lambda m: m.running) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
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
        """Register the agent with the model."""
        self._agents[agent] = None
        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet([agent], random=self.random)
        self._all_agents.add(agent)

    def deregister_agent(self, agent: Agent) -> None:
        """Deregister the agent with the model."""
        del self._agents[agent]
        self._agents_by_type[type(agent)].remove(agent)
        self._all_agents.remove(agent)

    def remove_all_agents(self) -> None:
        """Remove all agents from the model."""
        for agent in list(self._agents.keys()):
            agent.remove()

    # Random Number Generator Management

    def reset_randomizer(self, seed: int | None = None) -> None:
        """Reset the model random number generator."""
        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed

    def reset_rng(self, rng: RNGLike | SeedLike | None = None) -> None:
        """Reset the numpy random number generator."""
        self.rng = np.random.default_rng(rng)
        self._rng = self.rng.bit_generator.state
