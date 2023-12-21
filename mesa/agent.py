"""
The agent class for Mesa framework.

Core Objects: Agent
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import operator
import weakref
from collections.abc import MutableSet, Sequence
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


class AgentSet(MutableSet, Sequence):
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

    def select(self, filter_func: Callable[[Agent], bool] | None = None, n: int = 0, inplace: bool = False) -> AgentSet:
        """select agents from AgentSet

        Args:
            filter_func (Callable[[Agent]]): function to filter agents. Function should return True if agent is to be
                                             included, false otherwise
            n (int, optional): number of agents to return. Defaults to 0, meaning all agents are returned
            inplace (bool, optional): updates agentset inplace if True, else return new Agentset. Defaults to False.


        """
        if filter_func is not None:
            agents = [agent for agent in self._agents.keys() if filter_func(agent)]
        else:
            agents = list(self._agents.keys())

        if n:
            agents = agents[:n]

        return AgentSet(agents, self.model) if not inplace else self._update(agents)

    def shuffle(self, inplace: bool = False) -> AgentSet:
        shuffled_agents = list(self)
        self.random.shuffle(shuffled_agents)

        return AgentSet(shuffled_agents, self.model) if not inplace else self._update(shuffled_agents)

    def sort(self, key: Callable[[Agent], Any]|str, reverse: bool = False, inplace: bool = False) -> AgentSet:
        if isinstance(key, str):
            key = operator.attrgetter(key)

        sorted_agents = sorted(self._agents.keys(), key=key, reverse=reverse)

        return AgentSet(sorted_agents, self.model) if not inplace else self._update(sorted_agents)

    def _update(self, agents: Iterable[Agent]):
        _agents = weakref.WeakKeyDictionary()
        for agent in agents:
            _agents[agent] = None

        self._agents = _agents
        return self

    def do(self, method_name: str, *args, return_results: bool = False, **kwargs) -> AgentSet | list[Any]:
        """invoke method on each agent

        Args:
            method_name (str): name of the method to call on each agent
            return_results (bool): whether to return the result from the method call or
                                   return the AgentSet itself. Defaults to False, so you can
                                   continue method chaining

        Additional arguments and keyword arguments will be passed to the method being called

        """
        res = [getattr(agent, method_name)(*args, **kwargs) for agent in self._agents]

        return res if return_results else self

    def get(self, attr_name: str) -> list[Any]:
        """get attribute value on each agent

        Args:
            attr_name (str): name of the attribute to get from eahc agent in the set

        """
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
        self.model = state['model']
        self._update(state['agents'])

    @property
    def random(self) -> Random:
        return self.model.random


# consider adding for performance reasons
# for Sequence: __reversed__, index, and count
# for MutableSet clear, pop, remove, __ior__, __iand__, __ixor__, and __isub__