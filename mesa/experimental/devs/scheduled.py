"""Scheduled decorator for recurring model methods.

This module provides the @scheduled decorator for marking methods that should
be automatically scheduled to run at regular intervals during simulation.
"""

from __future__ import annotations

from collections.abc import Callable

# Attribute name used to mark scheduled methods
SCHEDULED_ATTR = "_mesa_scheduled_interval"


def scheduled(method: Callable | None = None, *, interval: float = 1.0) -> Callable:
    """Decorator to mark a method as scheduled to run at regular intervals.

    Can be used with or without arguments:

        @scheduled
        def step(self):
            ...

        @scheduled(interval=0.5)
        def fast_update(self):
            ...

    Args:
        method: The method to decorate (when used without parentheses).
        interval: Time interval between executions (default: 1.0).

    Returns:
        The decorated method with scheduling metadata attached.

    Examples:
        class MyModel(Model):
            @scheduled
            def step(self):
                self.agents.shuffle_do("step")

            @scheduled(interval=7.0)
            def weekly_report(self):
                self.collect_weekly_stats()
    """

    def decorator(func: Callable) -> Callable:
        # Store the interval as an attribute on the function
        setattr(func, SCHEDULED_ATTR, interval)
        return func

    # Handle both @scheduled and @scheduled(...) syntax
    if method is not None:
        # Called without parentheses: @scheduled
        return decorator(method)
    else:
        # Called with parentheses: @scheduled(interval=0.5)
        return decorator


def get_scheduled_interval(method: Callable) -> float | None:
    """Get the scheduled interval for a method, or None if not scheduled.

    Args:
        method: The method to check.

    Returns:
        The interval if the method is decorated with @scheduled, else None.
    """
    return getattr(method, SCHEDULED_ATTR, None)


def is_scheduled(method: Callable) -> bool:
    """Check if a method is decorated with @scheduled.

    Args:
        method: The method to check.

    Returns:
        True if the method has the @scheduled decorator.
    """
    return hasattr(method, SCHEDULED_ATTR)
