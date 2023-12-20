"""
The agent class for Mesa framework.

Core Objects: Agent
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import weakref
from collections.abc import MutableSet
from random import Random

# mypy
from typing import TYPE_CHECKING, Any, Callable, Iterator, Iterable

if TYPE_CHECKING:
    # We ensure that these are not imported during runtime to prevent cyclic
    # dependency.
    from mesa.model import Model
    from mesa.space import Position


class Agent:
    """
    Base class for a model agent in Mesa.

    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): A reference to the model instance.
        self.pos: Position | None = None
    """

    def __init__(self, unique_id: int, model: Model) -> None:
        """
        Create a new agent.

        Args:
            unique_id (int): A unique identifier for this agent.
            model (Model): The model instance in which the agent exists.
        """
        self.unique_id = unique_id
        self.model = model
        self.pos: Position | None = None

        # register agent
        self.model._agents[type(self)][self] = None

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        try:
            # remove agent
            self.model._agents[type(self)].pop(self)
        except KeyError:
            pass

    def step(self) -> None:
        """A single step of the agent."""

    def advance(self) -> None:
        pass

    @property
    def random(self) -> Random:
        return self.model.random


class AgentSet(MutableSet):
    """Ordered set of agents"""

    def __init__(self, agents: Iterable[Agent], model: Model):
        self._agents = weakref.WeakKeyDictionary()
        for agent in agents:
            self._agents[agent] = None

        self.model = model

    def __len__(self) -> int:
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        return self._agents.keys()

    def __contains__(self, agent: Agent) -> bool:
        """Check if an agent is in the AgentSet."""
        return agent in self._agents

    def select(self, filter_func: Callable[[Agent], bool] | None = None, inplace: bool = False) -> AgentSet:
        if filter_func is None:
            return self if inplace else AgentSet(iter(self), self.model)

        agents = [agent for agent in self._agents.keys() if filter_func(agent)]

        if inplace:
            self._reorder(agents)
            return self
        else:
            return AgentSet(
                agents,
                self.model
            )

    def shuffle(self, inplace: bool = False)-> AgentSet:
        shuffled_agents = list(self)
        self.model.random.shuffle(shuffled_agents)

        if inplace:
            self._reorder(shuffled_agents)
            return self
        else:
            return AgentSet(shuffled_agents, self.model)

    def sort(self, key: Callable[[Agent], Any], reverse: bool = False, inplace: bool = False)-> AgentSet:
        sorted_agents = sorted(self._agents.keys(), key=key, reverse=reverse)

        if inplace:
            self._reorder(sorted_agents)
            return self
        else:
            return AgentSet(sorted_agents, self.model)

    def _reorder(self, agents: Iterable[Agent]):
        _agents = weakref.WeakKeyDictionary()
        for agent in agents:
            _agents[agent] = None

        self._agents = _agents

    def do_each(self, method_name: str, *args, **kwargs) -> list[Any]:
        """invoke method on each agent"""
        return [getattr(agent, method_name)(*args, **kwargs) for agent in self._agents]

    def get_each(self, attr_name: str) -> list[Any]:
        """get attribute value on each agent"""
        return [getattr(agent, attr_name) for agent in self._agents]

    def __getitem__(self, item: int | slice) -> Agent:
        return list(self._agents.keys())[item]

    def add(self, agent: Agent):
        # abstract method from MutableSet
        self._agents[agent] = None

    def discard(self, agent: Agent):
        # abstract method from MutableSet
        # discard should not raise an error when
        # item is not in set
        try:
            del self._agents[agent]
        except KeyError:
            pass

    def remove(self, agent: Agent):
        # remove should raise an error when
        # item is not in set
        del self._agents[agent]

    def __getstate__(self):
        return dict(agents=list(self._agents.keys()), model=self.model)

    def __setstate__(self, state):
        self.model = model
        self._reorder(agents)