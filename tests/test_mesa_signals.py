"""Tests for mesa_signals."""

from unittest.mock import Mock

import pytest

from mesa import Agent, Model
from mesa.experimental.mesa_signals import (
    All,
    Computable,
    Computed,
    HasObservables,
    Observable,
    ObservableList,
)


def test_observables():
    """Test Observable."""

    class MyAgent(Agent, HasObservables):
        some_attribute = Observable()

        def __init__(self, model, value):
            super().__init__(model)
            some_attribute = value  # noqa: F841

    handler = Mock()

    model = Model(seed=42)
    agent = MyAgent(model, 10)
    agent.observe("some_attribute", "change", handler)

    agent.some_attribute = 10
    handler.assert_called_once()


def test_HasObservables():
    """Test Observable."""

    class MyAgent(Agent, HasObservables):
        some_attribute = Observable()
        some_other_attribute = Observable()

        def __init__(self, model, value):
            super().__init__(model)
            some_attribute = value  # noqa: F841
            some_other_attribute = 5  # noqa: F841

    handler = Mock()

    model = Model(seed=42)
    agent = MyAgent(model, 10)
    agent.observe("some_attribute", "change", handler)

    subscribers = {entry() for entry in agent.subscribers["some_attribute"]["change"]}
    assert handler in subscribers

    agent.unobserve("some_attribute", "change", handler)
    subscribers = {entry() for entry in agent.subscribers["some_attribute"]["change"]}
    assert handler not in subscribers

    subscribers = {
        entry() for entry in agent.subscribers["some_other_attribute"]["change"]
    }
    assert len(subscribers) == 0

    # testing All()
    agent.observe(All(), "change", handler)

    for attr in ["some_attribute", "some_other_attribute"]:
        subscribers = {entry() for entry in agent.subscribers[attr]["change"]}
        assert handler in subscribers

    agent.unobserve(All(), "change", handler)
    for attr in ["some_attribute", "some_other_attribute"]:
        subscribers = {entry() for entry in agent.subscribers[attr]["change"]}
        assert handler not in subscribers
        assert len(subscribers) == 0

    # testing for clear_all_subscriptions
    nr_observers = 3
    handlers = [Mock() for _ in range(nr_observers)]
    for handler in handlers:
        agent.observe("some_attribute", "change", handler)
        agent.observe("some_other_attribute", "change", handler)

    subscribers = {entry() for entry in agent.subscribers["some_attribute"]["change"]}
    assert len(subscribers) == nr_observers

    agent.clear_all_subscriptions("some_attribute")
    subscribers = {entry() for entry in agent.subscribers["some_attribute"]["change"]}
    assert len(subscribers) == 0

    subscribers = {
        entry() for entry in agent.subscribers["some_other_attribute"]["change"]
    }
    assert len(subscribers) == 3

    agent.clear_all_subscriptions(All())
    subscribers = {entry() for entry in agent.subscribers["some_attribute"]["change"]}
    assert len(subscribers) == 0

    subscribers = {
        entry() for entry in agent.subscribers["some_other_attribute"]["change"]
    }
    assert len(subscribers) == 0

    # fixme unobserve all observables

    # test raises
    with pytest.raises(ValueError):
        agent.observe("some_attribute", "unknonw_signal", handler)

    with pytest.raises(ValueError):
        agent.observe("unknonw_attribute", "change", handler)


def test_ObservableList():
    """Test ObservableList."""
    # fixme, this does not test the emmited signals yet

    class MyAgent(Agent, HasObservables):
        my_list = ObservableList()

        def __init__(self, model,):
            super().__init__(model)
            self.my_list = []

    model = Model(seed=42)
    agent = MyAgent(model)

    assert len(agent.my_list) == 0

    # add
    agent.my_list.append(1)
    assert len(agent.my_list) == 1

    # remove
    agent.my_list.remove(1)
    assert len(agent.my_list) == 0

    # overwrite the existing list
    a_list = [1,2,3,4,5]
    agent.my_list = a_list
    assert len(agent.my_list) == len(a_list)
    agent.my_list = a_list
    assert len(agent.my_list) == len(a_list)

    # pop
    index = 4
    entry = agent.my_list.pop(index)
    assert entry == a_list.pop(index)
    assert len(agent.my_list) == len(a_list)

    # insert
    agent.my_list.insert(0, 5)


    # overwrite
    agent.my_list[0] = 10
    assert agent.my_list[0] == 10

    # combine two lists
    a_list = [1,2,3,4,5]
    agent.my_list = a_list
    assert len(agent.my_list) == len(a_list)
    agent.my_list += a_list
    assert len(agent.my_list) == 2*len(a_list)


    assert 5 in agent.my_list

    assert agent.my_list.index(5) == 4



def test_Computable():
    """Test Computable and Computed."""

    class MyAgent(Agent, HasObservables):
        some_attribute = Computable()
        some_other_attribute = Observable()

        def __init__(self, model, value):
            super().__init__(model)
            some_attribute = Computed(lambda x: x, self)  # noqa: F841
