"""Backward-compatible simulator wrappers.

These classes provide the legacy Simulator API while delegating to Model's
integrated event scheduling. New code should use Model.run() and Model.schedule()
directly.

Deprecated:
    ABMSimulator and DEVSimulator are deprecated. Use Model.run() and
    Model.schedule() directly instead.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from .eventlist import EventList, Priority, SimulationEvent

if TYPE_CHECKING:
    from mesa import Model


class Simulator:
    """Legacy simulator base class.

    Deprecated:
        Use Model.run() and Model.schedule() directly instead.
    """

    def __init__(self, time_unit: type, start_time: int | float):
        """Initialize a Simulator instance.

        Args:
            time_unit: Type of the simulation time.
            start_time: The start time of the simulator.
        """
        warnings.warn(
            "Simulator classes are deprecated. Use Model.run() and Model.schedule() "
            "directly instead.",
            FutureWarning,
            stacklevel=2,
        )
        self.start_time = start_time
        self.time_unit = time_unit
        self.model: Model | None = None
        self._local_event_list = EventList()

    @property
    def time(self) -> float:
        """Simulator time (deprecated, use model.time)."""
        warnings.warn(
            "simulator.time is deprecated, use model.time instead",
            FutureWarning,
            stacklevel=2,
        )
        return self.model.time if self.model else self.start_time

    @property
    def event_list(self) -> EventList:
        """Return the model's event list or local one if no model."""
        if self.model:
            return self.model._scheduler._event_list
        return self._local_event_list

    def check_time_unit(self, time: int | float) -> bool:
        """Check whether the time is of the correct unit."""
        return True

    def setup(self, model: Model) -> None:
        """Set up the simulator with the model.

        Args:
            model: The model to simulate.
        """
        if model.time != self.start_time:
            raise ValueError(
                f"Model time ({model.time}) does not match simulator start_time ({self.start_time})."
            )

        if not self._local_event_list.is_empty():
            raise ValueError("Events already scheduled. Call setup before scheduling.")

        self.model = model
        model._simulator = self  # Set reference for backward compatibility

    def reset(self) -> None:
        """Reset the simulator."""
        if self.model:
            self.model._scheduler.clear()
            self.model.time = self.start_time
            self.model = None
        self._local_event_list.clear()

    def run_until(self, end_time: int | float) -> None:
        """Run the simulator until the end time.

        Args:
            end_time: The end time for stopping the simulator.
        """
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )
        self.model.run(until=end_time)

    def run_for(self, time_delta: int | float) -> None:
        """Run the simulator for the specified time delta.

        Args:
            time_delta: The time delta to run for.
        """
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )
        self.model.run(duration=time_delta)

    def run_next_event(self) -> None:
        """Execute only the next event."""
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )

        event_list = self.model._scheduler._event_list
        if event_list.is_empty():
            return

        event = event_list.pop_event()
        self.model.time = event.time
        event.execute()

    def schedule_event_now(
        self,
        function: Callable,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event for the current time instant."""
        return self.schedule_event_relative(
            function,
            0.0,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )

    def schedule_event_absolute(
        self,
        function: Callable,
        time: int | float,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event for the specified time instant."""
        if self.model:
            return self.model.schedule(
                function,
                at=time,
                priority=priority,
                args=function_args,
                kwargs=function_kwargs,
            )
        # No model yet, store locally
        event = SimulationEvent(
            time,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self._local_event_list.add_event(event)
        return event

    def schedule_event_relative(
        self,
        function: Callable,
        time_delta: int | float,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event relative to current time."""
        if self.model:
            return self.model.schedule(
                function,
                after=time_delta,
                priority=priority,
                args=function_args,
                kwargs=function_kwargs,
            )
        # No model yet
        current = self.start_time
        event = SimulationEvent(
            current + time_delta,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self._local_event_list.add_event(event)
        return event

    def cancel_event(self, event: SimulationEvent) -> None:
        """Cancel a scheduled event."""
        if self.model:
            self.model.cancel(event)
        else:
            self._local_event_list.remove(event)


class ABMSimulator(Simulator):
    """Legacy ABM simulator with integer time steps.

    Deprecated:
        Use Model.run() and Model.schedule() directly instead.
    """

    def __init__(self):
        """Initialize an ABM simulator."""
        super().__init__(int, 0)

    def check_time_unit(self, time: int | float) -> bool:
        """Check whether the time is an integer."""
        if isinstance(time, int):
            return True
        if isinstance(time, float):
            return time.is_integer()
        return False

    def schedule_event_next_tick(
        self,
        function: Callable,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event for the next tick."""
        return self.schedule_event_relative(
            function,
            1,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )


class DEVSimulator(Simulator):
    """Legacy DEVS simulator with floating-point time.

    Deprecated:
        Use Model.run() and Model.schedule() directly instead.
    """

    def __init__(self):
        """Initialize a DEVS simulator."""
        super().__init__(float, 0.0)

    def check_time_unit(self, time: int | float) -> bool:
        """Check whether the time is numeric."""
        return isinstance(time, (int, float))
