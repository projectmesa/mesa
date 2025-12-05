"""Event scheduling and model execution.

This module provides the Scheduler class which handles event scheduling
and model execution, and the @scheduled decorator for marking recurring methods.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from .eventlist import EventList, Priority, SimulationEvent

if TYPE_CHECKING:
    from mesa import Model


# Attribute name used to mark scheduled methods
_SCHEDULED_ATTR = "_mesa_scheduled_interval"


def scheduled(interval: float = 1.0):
    """Decorator to mark a method as scheduled for recurring execution.

    Args:
        interval: Time interval between executions (default: 1.0).

    Returns:
        Decorated method with scheduling metadata.

    Examples:
        class MyModel(Model):
            @scheduled()  # Called every 1.0 time units
            def step(self):
                self.agents.shuffle_do("step")

            @scheduled(interval=7.0)  # Called every 7.0 time units
            def weekly_update(self):
                self.collect_stats()

            @scheduled(interval=0.1)  # Called every 0.1 time units
            def fast_process(self):
                self.update_physics()
    """

    def decorator(method: Callable) -> Callable:
        setattr(method, _SCHEDULED_ATTR, interval)
        return method

    return decorator


def get_scheduled_methods(obj: object) -> dict[str, float]:
    """Find all methods decorated with @scheduled on an object.

    Args:
        obj: Object to inspect for scheduled methods.

    Returns:
        Dictionary mapping method names to their intervals.
    """
    scheduled_methods = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            method = getattr(obj, name)
            if callable(method) and hasattr(method, _SCHEDULED_ATTR):
                interval = getattr(method, _SCHEDULED_ATTR)
                scheduled_methods[name] = interval
        except AttributeError:
            continue
    return scheduled_methods


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
        self._recurring_events: dict[str, SimulationEvent] = {}

    def start_recurring(
        self, scheduled_methods: dict[str, float] | None = None
    ) -> None:
        """Start all recurring methods.

        Args:
            scheduled_methods: Dictionary mapping method names to intervals.
                If None, scans the model for @scheduled decorated methods.
        """
        if scheduled_methods is None:
            scheduled_methods = get_scheduled_methods(self._model)

        for method_name, interval in scheduled_methods.items():
            method = getattr(self._model, method_name)
            self._schedule_recurring(method_name, method, interval)

    def _schedule_recurring(self, name: str, method: Callable, interval: float) -> None:
        """Schedule a recurring method execution.

        Args:
            name: Name of the method (for tracking).
            method: The method to call.
            interval: Time interval between calls.
        """

        # Create a wrapper that reschedules after execution
        def recurring_wrapper():
            method()
            # Reschedule for next interval
            next_time = self._model.time + interval
            event = SimulationEvent(
                next_time, recurring_wrapper, priority=Priority.DEFAULT
            )
            self._event_list.add_event(event)
            self._recurring_events[name] = event

        # Schedule first execution
        first_time = self._model.time + interval
        event = SimulationEvent(
            first_time, recurring_wrapper, priority=Priority.DEFAULT
        )
        self._event_list.add_event(event)
        self._recurring_events[name] = event

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
            steps: Run for this many steps (calls to step method, if exists).
            condition: Run while this condition returns True.

        Raises:
            ValueError: If no termination criterion is specified.
        """
        end_time = self._determine_end_time(until, duration, steps, condition)

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
            event.execute()

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
            # For backward compat: steps means number of step() calls
            # Each step is at interval 1.0 by default
            return self._model.time + steps
        elif condition is not None:
            return float("inf")
        else:
            raise ValueError(
                "Specify at least one of: 'until', 'duration', 'steps', or 'condition'"
            )

    def clear(self) -> None:
        """Clear all scheduled events."""
        self._event_list.clear()
        self._recurring_events.clear()

    @property
    def is_empty(self) -> bool:
        """Check if there are no scheduled events."""
        return self._event_list.is_empty()

    def peek(self, n: int = 1) -> list[SimulationEvent]:
        """Look at the next n events without removing them."""
        return self._event_list.peak_ahead(n)
