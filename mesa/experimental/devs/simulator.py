from .eventlist import EventList, SimEvent, Priority

import numbers

class Simulator:

    def __init__(self, time_unit, start_time):
        # should model run in a separate thread
        # and we can then interact with start, stop, run_until, and step?
        self.event_list = EventList()
        self.time = start_time
        self.time_unit = time_unit  # FIXME currently not used
        self.model = None

    def check_time_unit(self, time):
        ...

    def setup(self, model):
        self.event_list.clear()
        self.model = model
        model.setup()

    def reset(self):
        raise NotImplementedError

    def run(self, until=None):
        # run indefinitely? or until is reached

        endtime = self.time + until
        while self.time < endtime:
            self.step()

    def step(self):
        event = self.event_list.pop()
        self.time = event.time
        event.execute()

    def schedule_event_now(self, function, priority=Priority.DEFAULT, function_args=None, function_kwargs=None) -> SimEvent:
        event = SimEvent(self.time, function, priority=priority, function_args=function_args, function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def schedule_event_absolute(self, function, time, priority=Priority.DEFAULT, function_args=None, function_kwargs=None) -> SimEvent:
        event = SimEvent(time, function, priority=priority, function_args=function_args, function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def schedule_event_relative(self, function, time_delta, priority=Priority.DEFAULT, function_args=None, function_kwargs=None) -> SimEvent:
        event = SimEvent(self.time + time_delta, function, priority=priority, function_args=function_args, function_kwargs=function_kwargs)
        self._schedule_event(event)
        return event

    def cancel_event(self, event):
        self.event_list.remove(event)

    def _schedule_event(self, event):
        if not self.check_time_unit(event.time):
            raise ValueError(f"time unit mismatch {event.time} is not of time unit {self.time_unit}")

        # check timeunit of events
        self.event_list.add_event(event)


class ABMSimulator(Simulator):
    def __init__(self):
        super().__init__(int, 0)


    def check_time_unit(self, time):
        if isinstance(time, int):
            return True
        if isinstance(time, float):
            return time.is_integer()

    def schedule_event_next_tick(self, function, priority=Priority.DEFAULT, function_args=None, function_kwargs=None) -> SimEvent:
        self.schedule_event_relative(function, 1, priority=priority, function_args=function_args, function_kwargs=function_kwargs)

    def step(self):
        event = self.event_list.pop()

        if event.fn == self.model.step:
            self.schedule_event_next_tick(self.model.step, priority=Priority.DEFAULT)

        self.time = event.time
        event.execute()

class DEVSimulator(Simulator):
    def __init__(self):
        super().__init__(float, 0.0)

    def check_time_unit(self, time):
        return isinstance(time, numbers.Number)

