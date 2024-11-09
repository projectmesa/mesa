"""Tests for mesa_signals."""

from unittest.mock import Mock

import pytest

from mesa import Agent, Model
from mesa.experimental.mesa_signals import (
    All,
    HasObservables,
    Observable,
)


def test_observables():
    """Test Observable."""

    class MyAgent(Agent, HasObservables):
        some_attribute = Observable()

        def __init__(self, model, value):
            super().__init__(model)
            some_attribute = value

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
            some_attribute = value
            some_other_attribute = 5

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
