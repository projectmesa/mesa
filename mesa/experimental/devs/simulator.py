from __future__ import annotations

import numbers
from typing import Any, Callable

from mesa import Model

from .eventlist import EventList, Priority, SimulationEvent


class Simulator:
    """The Simulator controls the time advancement of the model.

    The simulator uses next event time progression to advance the simulation time, and execute the next event

    Attributes:
        event_list (EventList): The list of events to execute
        time (float | int): The current simulation time
        time_unit (type) : The unit of the simulation time
        model (Model): The model to simulate


    """

    # TODO: add replication support
    # TODO: add experimentation support

    def __init__(self, time_unit: type, start_time: int | float):
        # should model run in a separate thread,
        # and we can then interact with start, stop, run_until, and step?
        self.event_list = EventList()
        self.start_time = start_time
        self.time_unit = time_unit

        self.time = self.start_time
        self.model = None

    def check_time_unit(self, time: int | float) -> bool: ...

    def setup(self, model: Model) -> None:
        """Set up the simulator with the model to simulate

        Args:
            model (Model): The model to simulate

        """
        self.event_list.clear()
        self.model = model

    def reset(self):
        """Reset the simulator by clearing the event list and removing the model to simulate"""
        self.event_list.clear()
        self.model = None
        self.time = self.start_time

    def run_until(self, end_time: int | float) -> None:
        while True:
            try:
                event = self.event_list.pop_event()
            except IndexError:  # event list is empty
                self.time = end_time
                break

            if event.time <= end_time:
                self.time = event.time
                event.execute()
            else:
                self.time = end_time
                self._schedule_event(event)  # reschedule event
                break

    def run_for(self, time_delta: int | float):
        """run the simulator for the specified time delta

        Args:
            time_delta (float| int): The time delta. The simulator is run from the current time to the current time
                                     plus the time delta

        """
        end_time = self.time + time_delta
        self.run_until(end_time)

    def schedule_event_now(
        self,
        function: Callable,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event for the current time instant

        Args:
            function (Callable): The callable to execute for this event
            priority (Priority): the priority of the event, optional
            function_args (List[Any]): list of arguments for function
            function_kwargs (Dict[str, Any]):  dict of keyword arguments for function

        Returns:
            SimulationEvent: the simulation event that is scheduled

        """
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
        """Schedule event for the specified time instant

        Args:
            function (Callable): The callable to execute for this event
            time (int | float): the time for which to schedule the event
            priority (Priority): the priority of the event, optional
            function_args (List[Any]): list of arguments for function
            function_kwargs (Dict[str, Any]):  dict of keyword arguments for function

        Returns:
            SimulationEvent: the simulation event that is scheduled

        """
        if self.time > time:
            raise ValueError("trying to schedule an event in the past")

        event = SimulationEvent(
            time,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self._schedule_event(event)
        return event

    def schedule_event_relative(
        self,
        function: Callable,
        time_delta: int | float,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule event for the current time plus the time delta

        Args:
            function (Callable): The callable to execute for this event
            time_delta (int | float): the time delta
            priority (Priority): the priority of the event, optional
            function_args (List[Any]): list of arguments for function
            function_kwargs (Dict[str, Any]):  dict of keyword arguments for function

        Returns:
            SimulationEvent: the simulation event that is scheduled

        """
        event = SimulationEvent(
            self.time + time_delta,
            function,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )
        self._schedule_event(event)
        return event

    def cancel_event(self, event: SimulationEvent) -> None:
        """remove the event from the event list

        Args:
            event (SimulationEvent): The simulation event to remove

        """

        self.event_list.remove(event)

    def _schedule_event(self, event: SimulationEvent):
        if not self.check_time_unit(event.time):
            raise ValueError(
                f"time unit mismatch {event.time} is not of time unit {self.time_unit}"
            )

        # check timeunit of events
        self.event_list.add_event(event)


class ABMSimulator(Simulator):
    """This simulator uses incremental time progression, while allowing for additional event scheduling.

    The basic time unit of this simulator is an integer. It schedules `model.step` for each tick with the
    highest priority. This implies that by default, `model.step` is the first event executed at a specific tick.
    In addition, discrete event scheduling, using integer as the time unit is fully supported, paving the way
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

    def schedule_event_next_tick(
        self,
        function: Callable,
        priority: Priority = Priority.DEFAULT,
        function_args: list[Any] | None = None,
        function_kwargs: dict[str, Any] | None = None,
    ) -> SimulationEvent:
        """Schedule a SimulationEvent for the next tick

        Args
            function (Callable): the callable to execute
            priority (Priority): the priority of the event
            function_args (List[Any]): List of arguments to pass to the callable
            function_kwargs (Dict[str, Any]): List of keyword arguments to pass to the callable

        """
        return self.schedule_event_relative(
            function,
            1,
            priority=priority,
            function_args=function_args,
            function_kwargs=function_kwargs,
        )

    def run_until(self, end_time: int) -> None:
        """run the simulator up to and included the specified end time

        Args:
            end_time (float| int): The end_time delta. The simulator is until the specified end time

        """
        while True:
            try:
                event = self.event_list.pop_event()
            except IndexError:
                self.time = end_time
                break

            if event.time <= end_time:
                self.time = event.time
                if event.fn() == self.model.step:
                    self.schedule_event_next_tick(
                        self.model.step, priority=Priority.HIGH
                    )

                event.execute()
            else:
                self.time = end_time
                self._schedule_event(event)
                break

    def run_for(self, time_delta: int):
        """run the simulator for the specified time delta

        Args:
            time_delta (float| int): The time delta. The simulator is run from the current time to the current time
                                     plus the time delta

        """
        end_time = self.time + time_delta - 1
        self.run_until(end_time)


class DEVSimulator(Simulator):
    """A simulator where the unit of time is a float. Can be used for full-blown discrete event simulating using
    event scheduling.

    """

    def __init__(self):
        super().__init__(float, 0.0)

    def check_time_unit(self, time) -> bool:
        return isinstance(time, numbers.Number)
