import itertools
from enum import IntEnum
from heapq import heapify, heappop, heappush
from typing import Any, Callable


class Priority(IntEnum):
    LOW = 10
    DEFAULT = 5
    HIGH = 1


class SimulationEvent:
    """A simulation event

    the callable is wrapped using weakrefs, so there is no need to explicitly cancel event if e.g., an agent
    is removed from the simulation.

    Attributes:
        time (float): The simulation time of the event
        function  (Callable): The function to execute for this event
        priority (Priority): The priority of the event
        unique_id (int) the unique identifier of the event
        function_args (list[Any]): Argument for the function
        function_kwargs (Dict[str, Any]): Keyword arguments for the function

    """

    _ids = itertools.count(1)

    @property
    def CANCELED(self) -> bool:
        return self._canceled

    def __init__(
        self,
        time: int | float,
        function: Callable,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self.time = time
        self.priority = priority.value
        self._canceled = False

        if isinstance(function, MethodType):
            function = WeakMethod(function)
        else:
            function = ref(function)

        self.fn = function
        self.unique_id = next(self._ids)
        self.function_args = function_args if function_args else []
        self.function_kwargs = function_kwargs if function_kwargs else {}

        if self.fn is None:
            raise Exception()

    def execute(self):
        """execute this event"""
        fn = self.fn()
        if fn is not None:
            fn(*self.function_args, **self.function_kwargs)

    def cancel(self) -> None:
        """cancel this event"""
        self._canceled = True
        self.fn = None
        self.function_args = []
        self.function_kwargs = {}

    def __lt__(self, other):
        # Define a total ordering for events to be used by the heapq
        return (self.time, self.priority, self.unique_id) < (
            other.time,
            other.priority,
            other.unique_id,
        )


class EventList:
    """An event list

    This is a heap queue sorted list of events. Events are allways removed from the left. The events are sorted
    based on their time stamp, their priority, and their unique_id, guaranteeing a complete ordering.

    """

    def __init__(self):
        self._events: list[SimulationEvent] = []
        heapify(self._events)

    def add_event(self, event: SimulationEvent):
        """Add the event to the event list

        Args:
            event (SimulationEvent): The event to be added

        """

        heappush(self._events, event)

    def peek_ahead(self, n: int = 1) -> list[SimulationEvent]:
        """Look at the first n non-canceled event in the event list

        Args:
            n (int): The number of events to look ahead

        Returns:
            list[SimulationEvent]

        Raises:
            IndexError: If the eventlist is empty

        Notes:
            this method can return a list shorted then n if the number of non-canceled events on the event list
            is less than n.

        """
        # look n events ahead
        if self.is_empty():
            raise IndexError("event list is empty")

        peek: list[SimulationEvent] = []
        for event in self._events:
            if not event.CANCELED:
                peek.append(event)
            if len(peek) >= n:
                return peek
        return peek

    def pop_event(self) -> SimulationEvent:
        """pop the first element from the event list"""
        while self._events:
            event = heappop(self._events)
            if not event.CANCELED:
                return event
        raise IndexError("Event list is empty")

    def is_empty(self) -> bool:
        return len(self) == 0

    def __contains__(self, event: SimulationEvent) -> bool:
        return event in self._events

    def __len__(self) -> int:
        return len(self._events)

    def remove(self, event: SimulationEvent) -> None:
        """remove an event from the event list"""
        # we cannot simply remove items from _eventlist because this breaks
        # heap structure invariant. So, we use a form of lazy deletion.
        # SimEvents have a CANCELED flag that we set to True, while poping and peak_ahead
        # silently ignore canceled events
        event.cancel()

    def clear(self):
        self._events.clear()
