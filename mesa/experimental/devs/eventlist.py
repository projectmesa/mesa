import itertools
from enum import IntEnum
from heapq import heapify, heappop, heappush
from weakref import ref, WeakMethod

from types import MethodType


class InstanceCounterMeta(type):
    """ Metaclass to make instance counter not share count with descendants

    TODO:: can also be used for agents.unique_id
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._ids = itertools.count(1)


class Priority(IntEnum):
    LOW = 10
    DEFAULT = 5
    HIGH = 1


class SimulationEvent(metaclass=InstanceCounterMeta):
    """A simulation event

    Attributes:
        time (float): The simulation time of the event
        priority (Priority): The priority of the event
        fn  (Callable): The function to execute for this event
        unique_id (int) the unique identifier of the event
        function_args (list[Any]): Argument for the function
        function_kwargs (Dict[str, Any]): Keyword arguments for the function

    """

    @property
    def CANCELED(self) -> bool:
        return self._canceled

    @CANCELED.setter
    def CANCELED(self, bool: bool) -> None:
        self._canceled = bool
        self.fn = None
        self.function_args = []
        self.function_kwargs = {}

    def __init__(self, time, function, priority: Priority = Priority.DEFAULT, function_args=None, function_kwargs=None):
        super().__init__()
        self.time = time
        self.priority = priority.value

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
        fn = self.fn()
        if fn is not None:
            fn(*self.function_args, **self.function_kwargs)

    def __cmp__(self, other):
        if self.time < other.time:
            return -1
        if self.time > other.time:
            return 1

        if self.priority > other.priority:
            return -1
        if self.priority < other.priority:
            return 1

        if self.unique_id < other.unique_id:
            return -1
        if self.unique_id > other.unique_id:
            return 1

        # theoretically this should be impossible unless it is the
        # exact same event
        return 0

    def to_tuple(self):
        return self.time, self.priority, self.unique_id, self


class EventList:
    """An event list

    This is a heap queue sorted list of events. Events are allways removed from the left. The events are sorted
    based on their time stamp, their priority, and their unique_id, guaranteeing a complete ordering.

    """

    def __init__(self):
        super().__init__()
        self._event_list: list[tuple] = []
        heapify(self._event_list)

    def add_event(self, event: SimulationEvent):
        """Add the event to the event list

        Args:
            event (SimulationEvent): The event to be added

        """

        heappush(self._event_list, event.to_tuple())

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
        for entry in self._event_list:
            sim_event: SimulationEvent = entry[3]
            if not sim_event.CANCELED:
                peek.append(sim_event)
            if len(peek) >= n:
                return peek
        return peek

    def pop(self) -> SimulationEvent:
        """pop the first element from the event list

        """

        try:
            while True:
                sim_event = heappop(self._event_list)[3]
                if not sim_event.CANCELED:
                    return sim_event
        except IndexError:
            raise Exception("event list is empty")

    def is_empty(self) -> bool:
        return len(self) == 0

    def __contains__(self, event: SimulationEvent) -> bool:
        return event.to_tuple() in self._event_list

    def __len__(self) -> int:
        return len(self._event_list)

    def remove(self, event: SimulationEvent) -> None:
        """remove an event from the event list"""
        # we cannot simply remove items from _eventlist because this breaks
        # heap structure invariant. So, we use a form of lazy deletion.
        # SimEvents have a CANCELED flag that we set to True, while poping and peak_ahead
        # silently ignore canceled events
        event.CANCELED = True

    def clear(self):
        self._event_list.clear()
