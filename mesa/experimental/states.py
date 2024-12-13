"""State management system for Mesa agents.

This module provides a flexible state management system for Mesa agents, supporting
both discrete and continuous state changes. It enables agents to maintain multiple
states that can change either explicitly (discrete) or based on time (continuous),
and includes support for composite states derived from other states.

Core Classes:
   State: Base class defining the state interface
   DiscreteState: States with explicit value changes
   ContinuousState: States that change over time
   CompositeState: States computed from other states
   StateAgent: Mesa Agent subclass with state management
"""

from collections.abc import Callable
from typing import Any

from mesa import Agent


class State:
    """Base class for all states."""

    def __init__(self, name: str, initial_value: Any):
        """Create a new state."""
        self.name = name
        self._value = initial_value
        self._last_update_time = 0
        self.model = None  # Set when state is added to agent

    @property
    def value(self) -> Any:
        """Get current state value."""
        raise NotImplementedError

    def update(self, time: float) -> None:
        """Update state to current time."""
        raise NotImplementedError


class DiscreteState(State):
    """A state with discrete values that change explicitly."""

    @property
    def value(self) -> Any:
        """Get the current state value."""
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        """Set the state value."""
        self._value = new_value

    def update(self, time: float) -> None:
        """DiscreteStates only update when value is explicitly changed."""


class ContinuousState(State):
    """A state that changes continuously over time."""

    def __init__(
        self,
        name: str,
        initial_value: float,
        rate_function: Callable[[float, float], float],
    ):
        """Create a new continuous state."""
        super().__init__(name, initial_value)
        self.rate_function = rate_function

    @property
    def value(self) -> float:
        """Calculate and return current value based on elapsed time."""
        current_time = self.model.time
        if current_time > self._last_update_time:
            self.update(current_time)
        return self._value

    def update(self, time: float) -> None:
        """Update state value based on elapsed time."""
        elapsed = time - self._last_update_time
        self._value = self._value + self.rate_function(self._value, elapsed)
        self._last_update_time = time


class CompositeState(State):
    """A state derived from other states."""

    def __init__(
        self,
        name: str,
        dependent_states: list[State],
        computation_function: Callable[..., Any],
    ):
        """Create a new composite state."""
        self.dependent_states = dependent_states
        self.computation_function = computation_function
        super().__init__(name, None)  # Value computed on first access

    @property
    def value(self) -> Any:
        """Compute value based on dependent states."""
        state_values = [state.value for state in self.dependent_states]
        return self.computation_function(*state_values)

    def update(self, time: float) -> None:
        """Update all dependent states."""
        for state in self.dependent_states:
            state.update(time)


class StateAgent(Agent):
    """An agent with integrated state management."""

    def __init__(self, model) -> None:
        """Create a new agent with state management."""
        super().__init__(model)
        self.states = {}  # name -> State mapping

    def add_state(self, state: State) -> None:
        """Add a new state to the agent."""
        state.model = self.model
        self.states[state.name] = state

    def get_state(self, name: str) -> Any:
        """Get the current value of a state."""
        return self.states[name].value

    def set_state(self, name: str, value: Any) -> None:
        """Set value for a discrete state."""
        if isinstance(self.states[name], DiscreteState):
            self.states[name].value = value
        else:
            raise ValueError("Cannot directly set value of non-discrete state")

    def update_states(self) -> None:
        """Update all states to current time."""
        for state in self.states.values():
            state.update(self.model.time)
