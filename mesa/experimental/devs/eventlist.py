import itertools
from enum import IntEnum
from heapq import heapify, heappop, heappush


class InstanceCounterMeta(type):
    """ Metaclass to make instance counter not share count with descendants

    FIXME:: can also be used for agents
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._ids = itertools.count(1)


class Priority(IntEnum):
    LOW = 1
    HIGH = 10
    DEFAULT = 5


class SimEvent(metaclass=InstanceCounterMeta):
    # fixme:: how do we want to handle function?
    # should be a callable, possibly on an object
    # also we want only weakrefs to agents

    def __init__(self, time, function, priority=Priority.DEFAULT, function_args=None, function_kwargs=None):
        super().__init__()
        self.time = time
        self.priority = priority
        self.fn = function
        self.unique_id = next(self._ids)
        self.function_args = function_args if function_args else []
        self.function_kwargs = function_kwargs if function_kwargs else {}

        if self.fn is None:
            raise Exception()

    def execute(self):
        self.fn(*self.function_args, **self.function_kwargs)

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


class EventList:
    def __init__(self):
        super().__init__()
        self._event_list: list[SimEvent] = []
        heapify(self._event_list)

    def add_event(self, event: SimEvent):
        heappush(self._event_list, (event.time, event.priority, event.unique_id, event))

    def peek_ahead(self, n: int = 1) -> list[SimEvent]:
        # look n events ahead, or delta time ahead
        if self.is_empty():
            raise IndexError("event list is empty")
        return [entry[3] for entry in self._event_list[0:n]]

    def pop(self) -> SimEvent:
        # return next event
        return heappop(self._event_list)[3]

    def is_empty(self) -> bool:
        return len(self) == 0

    def __contains__(self, event: SimEvent) -> bool:
        return (event.time, event.priority, event.unique_id, event) in self._event_list

    def __len__(self) -> int:
        return len(self._event_list)

    def remove(self, event):
        self._event_list.remove((event.time, event.priority, event.unique_id, event))

    def clear(self):
        self._event_list.clear()
