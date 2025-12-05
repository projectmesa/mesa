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
        """Initialize a Simulator instance."""
        warnings.warn(
            "Simulator classes are deprecated. Use Model.run() and Model.schedule() "
            "directly instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.start_time = start_time
        self.time_unit = time_unit
        self.model: Model | None = None
        self.event_list = EventList()

    @property
    def time(self) -> float:
        """Simulator time (deprecated, use model.time)."""
        warnings.warn(
            "simulator.time is deprecated, use model.time instead",
            FutureWarning,
            stacklevel=2,
        )
        return self.model.time if self.model else self.start_time

    def check_time_unit(self, time: int | float) -> bool:
        """Check whether the time is of the correct unit."""
        return True

    def setup(self, model: Model) -> None:
        """Set up the simulator with the model.

        Args:
            model: The model to simulate.

        Raises:
            ValueError: If model time doesn't match start_time or events already scheduled.
        """
        if model.time != self.start_time:
            raise ValueError(
                f"Model time ({model.time}) does not match simulator start_time ({self.start_time})."
            )
        if not self.event_list.is_empty():
            raise ValueError("Events already scheduled. Call setup before scheduling.")

        self.model = model
        model._simulator = self  # For backward compatibility

    def reset(self) -> None:
        """Reset the simulator."""
        self.event_list.clear()
        if self.model is not None:
            self.model._simulator = None  # Clear backward compatibility reference
            self.model.time = self.start_time
            self.model = None

    def run_until(self, end_time: int | float) -> None:
        """Run the simulator until the end time."""
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )

        while True:
            try:
                event = self.event_list.pop_event()
            except IndexError:
                self.model.time = end_time
                break

            if event.time <= end_time:
                self.model.time = event.time
                event.execute()
            else:
                self.model.time = end_time
                self.event_list.add_event(event)
                break

    def run_for(self, time_delta: int | float) -> None:
        """Run the simulator for the specified time delta."""
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )
        end_time = self.model.time + time_delta
        self.run_until(end_time)

    def run_next_event(self) -> None:
        """Execute only the next event."""
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )

        try:
            event = self.event_list.pop_event()
        except IndexError:
            return

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
        current_time = self.model.time if self.model else self.start_time
        if current_time > time:
            raise ValueError("trying to schedule an event in the past")

        if not self.check_time_unit(time):
            raise ValueError(
                f"time unit mismatch: {time} is not of time unit {self.time_unit}"
            )

        event = SimulationEvent(
            time,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self.event_list.add_event(event)
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
        current_time = self.model.time if self.model else self.start_time
        event_time = current_time + time_delta

        if not self.check_time_unit(event_time):
            raise ValueError(
                f"time unit mismatch: {event_time} is not of time unit {self.time_unit}"
            )

        event = SimulationEvent(
            event_time,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self.event_list.add_event(event)
        return event

    def cancel_event(self, event: SimulationEvent) -> None:
        """Cancel a scheduled event."""
        self.event_list.remove(event)


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

    def setup(self, model: Model) -> None:
        """Set up the simulator with automatic step scheduling."""
        super().setup(model)
        # Schedule first step with high priority
        if hasattr(model, "step"):
            self.schedule_event_next_tick(model.step, priority=Priority.HIGH)

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

    def run_until(self, end_time: int) -> None:
        """Run the simulator up to and including the specified end time."""
        if self.model is None:
            raise RuntimeError(
                "Simulator not set up. Call simulator.setup(model) first."
            )

        while True:
            try:
                event = self.event_list.pop_event()
            except IndexError:
                self.model.time = float(end_time)
                break

            if event.time <= end_time:
                self.model.time = float(event.time)

                # Check if this is a step event and reschedule
                fn = event.fn() if event.fn else None
                if fn == self.model.step:
                    self.schedule_event_next_tick(
                        self.model.step, priority=Priority.HIGH
                    )

                event.execute()
            else:
                self.model.time = float(end_time)
                self.event_list.add_event(event)
                break


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
        return isinstance(time, int | float)
