from typing import List, Any, Dict, Callable

from .eventlist import EventList, SimulationEvent, Priority

import numbers


class Simulator:
    # FIXME add replication support
    # FIXME add experimentation support

    def __init__(self, time_unit: type, start_time: int | float):
        # should model run in a separate thread,
        # and we can then interact with start, stop, run_until, and step?
        self.event_list = EventList()
        self.time = start_time
        self.time_unit = time_unit
        self.model = None

    def check_time_unit(self, time):
        ...

    def setup(self, model):
        self.event_list.clear()
        self.model = model
        model.setup()

    def reset(self):
        raise NotImplementedError

    def run(self, until: int | float | None = None):
        # run indefinitely? or until is reached

        end_time = self.time + until
        while self.time < end_time:
            self.step()

    def step(self):
        event = self.event_list.pop()
        self.time = event.time
        event.execute()

    def schedule_event_now(self, function: Callable, priority: Priority = Priority.DEFAULT,
                           function_args: List[Any] | None = None,
                           function_kwargs: Dict[str, Any] | None = None) -> SimulationEvent:
        event = SimulationEvent(self.time, function, priority=priority, function_args=function_args,
                                function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def schedule_event_absolute(self,
                                function: Callable, time: int | float,
                                priority: Priority = Priority.DEFAULT,
                                function_args: List[Any] | None = None,
                                function_kwargs: Dict[str, Any] | None = None) -> SimulationEvent:
        event = SimulationEvent(time, function, priority=priority, function_args=function_args,
                                function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def schedule_event_relative(self, function: Callable,
                                time_delta: int | float,
                                priority: Priority = Priority.DEFAULT,
                                function_args: List[Any] | None = None,
                                function_kwargs: Dict[str, Any] | None = None) -> SimulationEvent:
        event = SimulationEvent(self.time + time_delta, function, priority=priority, function_args=function_args,
                                function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def cancel_event(self, event: SimulationEvent) -> None:
        self.event_list.remove(event)

    def _schedule_event(self, event: SimulationEvent):
        if not self.check_time_unit(event.time):
            raise ValueError(f"time unit mismatch {event.time} is not of time unit {self.time_unit}")

        # check timeunit of events
        self.event_list.add_event(event)


class ABMSimulator(Simulator):
    """This simulator uses incremental time progression, while allowing for additional event scheduling.

    The basic time unit of this simulator is an integer. It schedules `model.step` for each tick with the
    highest priority. This implies that by default, `model.step` is the first event executed at a specific tick.
    In addition, discrete event scheduling, using integers as the time unit is fully supported, paving the way
    for hybrid ABM-DEVS simulations.

    """

    def __init__(self):
        super().__init__(int, 0)

    def setup(self, model):
        super().setup(model)
        self.schedule_event_now(self.model.step, priority=Priority.HIGH)

    def check_time_unit(self, time) -> bool:
        if isinstance(time, int):
            return True
        if isinstance(time, float):
            return time.is_integer()
        else:
            return False

    def schedule_event_next_tick(self,
                                 function: Callable,
                                 priority: Priority = Priority.DEFAULT,
                                 function_args: List[Any] | None = None,
                                 function_kwargs: Dict[str, Any] | None = None) -> SimulationEvent:
        """Schedule a SimulationEvent for the next tick

        Args
            function (Callable): the callable to execute
            priority (Priority): the priority of the event
            function_args (List[Any]): List of arguments to pass to the callable
            function_kwargs (Dict[str, Any]): List of keyword arguments to pass to the callable

        """
        return self.schedule_event_relative(function, 1,
                                            priority=priority,
                                            function_args=function_args,
                                            function_kwargs=function_kwargs)

    def step(self):
        """get the next event from the event list and execute it.

        Note
            if the event to execute is `model.step`, this method automatically also
            schedules a new `model.step` event for the next time tick. This ensures
            incremental time progression.

        """
        event = self.event_list.pop()

        if event.fn() == self.model.step:
            self.schedule_event_next_tick(self.model.step, priority=Priority.HIGH)

        self.time = event.time
        event.execute()


class DEVSimulator(Simulator):
    def __init__(self):
        super().__init__(float, 0.0)

    def check_time_unit(self, time) -> bool:
        return isinstance(time, numbers.Number)
