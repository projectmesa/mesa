"""Event scheduling and model execution.

This module provides the Scheduler class which handles event scheduling
and model execution. It is used internally by Model via composition.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from . import EventList, Priority, SimulationEvent

if TYPE_CHECKING:
    from mesa import Model


class Scheduler:
    """Handles event scheduling and model execution.

    This class manages the event list and provides methods for scheduling
    events and running the model. It is used internally by Model.

    Attributes:
        model: The model this scheduler is attached to.
    """

    def __init__(self, model: Model) -> None:
        """Initialize the scheduler.

        Args:
            model: The model instance to schedule events for.
        """
        self._model = model
        self._event_list = EventList()

    # -------------------------------------------------------------------------
    # Event Scheduling
    # -------------------------------------------------------------------------

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

        Raises:
            ValueError: If neither `at` nor `after` is specified, or both are.

        Examples:
            model.schedule(callback, at=50.0)
            model.schedule(callback, after=10.0)
            model.schedule(callback, at=50.0, priority=Priority.HIGH)
        """
        if (at is None) == (after is None):
            raise ValueError("Specify exactly one of 'at' or 'after'")

        if at is not None:
            event_time = at
            if event_time < self._model.time:
                raise ValueError(
                    f"Cannot schedule event in the past "
                    f"(at={at}, current time={self._model.time})"
                )
        else:
            event_time = self._model.time + after

        event = SimulationEvent(
            event_time,
            callback,
            priority=priority,
            function_args=args,
            function_kwargs=kwargs,
        )
        self._event_list.add_event(event)
        return event

    def cancel(self, event: SimulationEvent) -> None:
        """Cancel a scheduled event.

        Args:
            event: The event to cancel.
        """
        self._event_list.remove(event)

    # -------------------------------------------------------------------------
    # Model Execution
    # -------------------------------------------------------------------------

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

        Raises:
            ValueError: If no termination criterion is specified.

        Examples:
            model.run(until=100)
            model.run(duration=50)
            model.run(steps=100)
            model.run(condition=lambda m: m.running)
        """
        end_time = self._determine_end_time(until, duration, steps, condition)

        # Check if model has a custom step method (not just base Model.step)
        has_custom_step = (
            hasattr(self._model, "_uses_legacy_step") and self._model._uses_legacy_step
        )

        # Schedule initial step if model uses step-based execution
        if has_custom_step and self._event_list.is_empty():
            self._schedule_next_step()

        # Main simulation loop
        while self._model.running:
            if condition is not None and not condition(self._model):
                break

            if self._event_list.is_empty():
                self._model.time = end_time
                break

            # Peek at next event
            try:
                next_events = self._event_list.peak_ahead(1)
                if not next_events:
                    break
                next_event = next_events[0]
            except IndexError:
                break

            # Check if next event is within our time horizon
            if next_event.time > end_time:
                self._model.time = end_time
                break

            # Execute the event
            event = self._event_list.pop_event()
            self._model.time = event.time

            # Check if this is a step event
            fn = event.fn() if event.fn else None
            is_step = (
                fn == self._model._user_step
                if hasattr(self._model, "_user_step")
                else False
            )

            event.execute()

            # Reschedule step for next tick if this was a step
            if is_step and has_custom_step:
                self._model.steps += 1
                self._schedule_next_step()

    def _determine_end_time(
        self,
        until: float | None,
        duration: float | None,
        steps: int | None,
        condition: Callable[[Model], bool] | None,
    ) -> float:
        """Determine the end time based on provided arguments."""
        if until is not None:
            return until
        elif duration is not None:
            return self._model.time + duration
        elif steps is not None:
            return self._model.time + steps
        elif condition is not None:
            return float("inf")
        else:
            raise ValueError(
                "Specify at least one of: 'until', 'duration', 'steps', or 'condition'"
            )

    def _schedule_next_step(self) -> None:
        """Schedule the next step event."""
        if hasattr(self._model, "_user_step"):
            next_time = self._model.time + 1.0
            event = SimulationEvent(
                next_time,
                self._model._user_step,
                priority=Priority.HIGH,
            )
            self._event_list.add_event(event)

    def clear(self) -> None:
        """Clear all scheduled events."""
        self._event_list.clear()

    @property
    def is_empty(self) -> bool:
        """Check if there are no scheduled events."""
        return self._event_list.is_empty()

    def peek(self, n: int = 1) -> list[SimulationEvent]:
        """Look at the next n events without removing them."""
        return self._event_list.peak_ahead(n)
