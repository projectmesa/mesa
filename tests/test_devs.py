import pytest

from unittest.mock import MagicMock

from mesa.experimental.devs.simulator import ABMSimulator, DEVSimulator, Simulator
from mesa.experimental.devs.eventlist import EventList, SimulationEvent, Priority


from mesa import Model

def test_simulator():
    pass

def test_abms_simulator():
    pass

def test_devs_simulator():
    pass


def test_simulation_event():
    some_test_function = MagicMock()

    time = 10
    event = SimulationEvent(time, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})

    assert event.time == time
    assert event.fn() is some_test_function
    assert event.function_args == []
    assert event.function_kwargs == {}
    assert event.priority == Priority.DEFAULT

    # execute
    event.execute()
    some_test_function.assert_called_once()

    with pytest.raises(Exception):
        SimulationEvent(time, None, priority=Priority.DEFAULT, function_args=[], function_kwargs={})

    # check calling with arguments
    some_test_function = MagicMock()
    event = SimulationEvent(time, some_test_function, priority=Priority.DEFAULT, function_args=['1'], function_kwargs={'x':2})
    event.execute()
    some_test_function.assert_called_once_with('1', x=2)


    # check if we pass over deletion of callable silenty because of weakrefs
    some_test_function = lambda x, y: x + y
    event = SimulationEvent(time, some_test_function, priority=Priority.DEFAULT)
    del some_test_function
    event.execute()

    # cancel
    some_test_function = MagicMock()
    event = SimulationEvent(time, some_test_function, priority=Priority.DEFAULT, function_args=['1'],
                            function_kwargs={'x': 2})
    event.cancel()
    assert event.fn is None
    assert event.function_args == []
    assert event.function_kwargs == {}
    assert event.priority == Priority.DEFAULT
    assert event.CANCELED

    # comparison for sorting
    event1 = SimulationEvent(10, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    event2 = SimulationEvent(10, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    assert event1 < event2  # based on just unique_id as tiebraker

    event1 = SimulationEvent(11, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    event2 = SimulationEvent(10, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    assert event1 > event2

    event1 = SimulationEvent(10, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    event2 = SimulationEvent(10, some_test_function, priority=Priority.HIGH, function_args=[], function_kwargs={})
    assert event1 > event2

def test_eventlist():
    event_list = EventList()

    assert len(event_list._events) == 0
    assert isinstance(event_list._events, list)
    assert event_list.is_empty()

    # add event
    some_test_function = MagicMock()
    event = SimulationEvent(1, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    event_list.add_event(event)
    assert len(event_list) == 1
    assert event in event_list

    # remove event
    event_list.remove(event)
    assert len(event_list) == 1
    assert event.CANCELED

    # peak ahead
    event_list = EventList()
    for i in range(10):
        event = SimulationEvent(i, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
        event_list.add_event(event)
    events = event_list.peak_ahead(2)
    assert len(events) == 2
    assert events[0].time == 0
    assert events[1].time == 1

    events = event_list.peak_ahead(11)
    assert len(events) == 10

    event_list._events[6].cancel()
    events = event_list.peak_ahead(10)
    assert len(events) == 9

    event_list = EventList()
    with pytest.raises(Exception):
        event_list.peak_ahead()

    # pop event
    event_list = EventList()
    for i in range(10):
        event = SimulationEvent(i, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
        event_list.add_event(event)
    event = event_list.pop_event()
    assert event.time == 0

    event_list = EventList()
    event = SimulationEvent(9, some_test_function, priority=Priority.DEFAULT, function_args=[], function_kwargs={})
    event_list.add_event(event)
    event.cancel()
    with pytest.raises(Exception):
        event_list.pop_event()

    # clear
    event_list.clear()
    assert len(event_list) == 0