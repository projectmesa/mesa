import itertools
from enum import IntEnum
from heapq import heapify, heappop, heappush
from weakref import ref, WeakMethod

from types import MethodType

class InstanceCounterMeta(type):
    """ Metaclass to make instance counter not share count with descendants

    FIXME:: can also be used for agents
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._ids = itertools.count(1)


class Priority(IntEnum):
    LOW = 10
    DEFAULT = 5
    HIGH = 1



class SimulationEvent(metaclass=InstanceCounterMeta):
    # fixme:: how do we want to handle function?
    # should be a callable, possibly on an object
    # also we want only weakrefs to agents

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
    def __init__(self):
        super().__init__()
        self._event_list: list[tuple] = []
        heapify(self._event_list)

    def add_event(self, event: SimulationEvent):
        heappush(self._event_list, event.to_tuple())

    def peek_ahead(self, n: int = 1) -> list[SimulationEvent]:
        # look n events ahead, or delta time ahead
        if self.is_empty():
            raise IndexError("event list is empty")
        return [entry[3] for entry in self._event_list[0:n]]

    def pop(self) -> SimulationEvent:
        try:
            return heappop(self._event_list)[3]
        except IndexError:
            raise Exception("event list is empty")


    def is_empty(self) -> bool:
        return len(self) == 0

    def __contains__(self, event: SimulationEvent) -> bool:
        return event.to_tuple() in self._event_list

    def __len__(self) -> int:
        return len(self._event_list)

    def remove(self, event):
        self._event_list.remove(event.to_tuple)

    def clear(self):
        self._event_list.clear()
