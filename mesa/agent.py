"""
The agent class for Mesa framework.

Core Objects: Agent
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import contextlib
import operator
import warnings
import weakref
from collections import defaultdict
from collections.abc import Iterable, Iterator, MutableSet, Sequence
from random import Random

# mypy
from typing import TYPE_CHECKING, Any, Callable

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
        try:
            self.model._agents[type(self)][self] = None
        except AttributeError:
            # model super has not been called
            self.model._agents = defaultdict(dict)
            self.model.agentset_experimental_warning_given = False

            warnings.warn(
                "The Mesa Model class was not initialized. In the future, you need to explicitly initialize the Model by calling super().__init__() on initialization.",
                FutureWarning,
                stacklevel=2,
            )

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        with contextlib.suppress(KeyError):
            self.model._agents[type(self)].pop(self)

    def step(self) -> None:
        """A single step of the agent."""

    def advance(self) -> None:
        pass

    @property
    def random(self) -> Random:
        return self.model.random


class AgentSet(MutableSet, Sequence):
    """
    .. warning::
        The AgentSet is experimental. It may be changed or removed in any and all future releases, including
        patch releases.
        We would love to hear what you think about this new feature. If you have any thoughts, share them with
        us here: https://github.com/projectmesa/mesa/discussions/1919

    A collection class that represents an ordered set of agents within an agent-based model (ABM). This class
    extends both MutableSet and Sequence, providing set-like functionality with order preservation and
    sequence operations.

    Attributes:
        model (Model): The ABM model instance to which this AgentSet belongs.

    Methods:
        __len__, __iter__, __contains__, select, shuffle, sort, _update, do, get, __getitem__,
        add, discard, remove, __getstate__, __setstate__, random

    Note:
        The AgentSet maintains weak references to agents, allowing for efficient management of agent lifecycles
        without preventing garbage collection. It is associated with a specific model instance, enabling
        interactions with the model's environment and other agents.The implementation uses a WeakKeyDictionary to store agents,
        which means that agents not referenced elsewhere in the program may be automatically removed from the AgentSet.
    """

    agentset_experimental_warning_given = False

    def __init__(self, agents: Iterable[Agent], model: Model):
        """
        Initializes the AgentSet with a collection of agents and a reference to the model.

        Args:
            agents (Iterable[Agent]): An iterable of Agent objects to be included in the set.
            model (Model): The ABM model instance to which this AgentSet belongs.
        """
        self.model = model

        if not self.__class__.agentset_experimental_warning_given:
            self.__class__.agentset_experimental_warning_given = True
            warnings.warn(
                "The AgentSet is experimental. It may be changed or removed in any and all future releases, including patch releases.\n"
                "We would love to hear what you think about this new feature. If you have any thoughts, share them with us here: https://github.com/projectmesa/mesa/discussions/1919",
                FutureWarning,
                stacklevel=2,
            )

        self._agents = weakref.WeakKeyDictionary()
        for agent in agents:
            self._agents[agent] = None

    def __len__(self) -> int:
        """Return the number of agents in the AgentSet."""
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        """Provide an iterator over the agents in the AgentSet."""
        return self._agents.keys()

    def __contains__(self, agent: Agent) -> bool:
        """Check if an agent is in the AgentSet. Can be used like `agent in agentset`."""
        return agent in self._agents

    def select(
        self,
        filter_func: Callable[[Agent], bool] | None = None,
        n: int = 0,
        inplace: bool = False,
        agent_type: type[Agent] | None = None,
    ) -> AgentSet:
        """
        Select a subset of agents from the AgentSet based on a filter function and/or quantity limit.

        Args:
            filter_func (Callable[[Agent], bool], optional): A function that takes an Agent and returns True if the
                agent should be included in the result. Defaults to None, meaning no filtering is applied.
            n (int, optional): The number of agents to select. If 0, all matching agents are selected. Defaults to 0.
            inplace (bool, optional): If True, modifies the current AgentSet; otherwise, returns a new AgentSet. Defaults to False.
            agent_type (type[Agent], optional): The class type of the agents to select. Defaults to None, meaning no type filtering is applied.

        Returns:
            AgentSet: A new AgentSet containing the selected agents, unless inplace is True, in which case the current AgentSet is updated.
        """

        def agent_generator():
            count = 0
            for agent in self:
                if filter_func and not filter_func(agent):
                    continue
                if agent_type and not isinstance(agent, agent_type):
                    continue
                yield agent
                count += 1
                # default of n is zero, zo evaluates to False
                if n and count >= n:
                    break

        agents = agent_generator()

        return AgentSet(agents, self.model) if not inplace else self._update(agents)

    def shuffle(self, inplace: bool = False) -> AgentSet:
        """
        Randomly shuffle the order of agents in the AgentSet.

        Args:
            inplace (bool, optional): If True, shuffles the agents in the current AgentSet; otherwise, returns a new shuffled AgentSet. Defaults to False.

        Returns:
            AgentSet: A shuffled AgentSet. Returns the current AgentSet if inplace is True.
        """
        shuffled_agents = list(self)
        self.random.shuffle(shuffled_agents)

        return (
            AgentSet(shuffled_agents, self.model)
            if not inplace
            else self._update(shuffled_agents)
        )

    def sort(
        self,
        key: Callable[[Agent], Any] | str,
        ascending: bool = False,
        inplace: bool = False,
    ) -> AgentSet:
        """
        Sort the agents in the AgentSet based on a specified attribute or custom function.

        Args:
            key (Callable[[Agent], Any] | str): A function or attribute name based on which the agents are sorted.
            ascending (bool, optional): If True, the agents are sorted in ascending order. Defaults to False.
            inplace (bool, optional): If True, sorts the agents in the current AgentSet; otherwise, returns a new sorted AgentSet. Defaults to False.

        Returns:
            AgentSet: A sorted AgentSet. Returns the current AgentSet if inplace is True.
        """
        if isinstance(key, str):
            key = operator.attrgetter(key)

        sorted_agents = sorted(self._agents.keys(), key=key, reverse=not ascending)

        return (
            AgentSet(sorted_agents, self.model)
            if not inplace
            else self._update(sorted_agents)
        )

    def _update(self, agents: Iterable[Agent]):
        """Update the AgentSet with a new set of agents.
        This is a private method primarily used internally by other methods like select, shuffle, and sort.
        """
        _agents = weakref.WeakKeyDictionary()
        for agent in agents:
            _agents[agent] = None

        self._agents = _agents
        return self

    def do(
        self, method_name: str, *args, return_results: bool = False, **kwargs
    ) -> AgentSet | list[Any]:
        """
        Invoke a method on each agent in the AgentSet.

        Args:
            method_name (str): The name of the method to call on each agent.
            return_results (bool, optional): If True, returns the results of the method calls; otherwise, returns the AgentSet itself. Defaults to False, so you can chain method calls.
            *args: Variable length argument list passed to the method being called.
            **kwargs: Arbitrary keyword arguments passed to the method being called.

        Returns:
            AgentSet | list[Any]: The results of the method calls if return_results is True, otherwise the AgentSet itself.
        """
        res = [getattr(agent, method_name)(*args, **kwargs) for agent in self._agents]

        return res if return_results else self

    def get(self, attr_name: str) -> list[Any]:
        """
        Retrieve a specified attribute from each agent in the AgentSet.

        Args:
            attr_name (str): The name of the attribute to retrieve from each agent.

        Returns:
            list[Any]: A list of attribute values from each agent in the set.
        """
        return [getattr(agent, attr_name) for agent in self._agents]

    def __getitem__(self, item: int | slice) -> Agent:
        """
        Retrieve an agent or a slice of agents from the AgentSet.

        Args:
            item (int | slice): The index or slice for selecting agents.

        Returns:
            Agent | list[Agent]: The selected agent or list of agents based on the index or slice provided.
        """
        return list(self._agents.keys())[item]

    def add(self, agent: Agent):
        """
        Add an agent to the AgentSet.

        Args:
            agent (Agent): The agent to add to the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        self._agents[agent] = None

    def discard(self, agent: Agent):
        """
        Remove an agent from the AgentSet if it exists.

        This method does not raise an error if the agent is not present.

        Args:
            agent (Agent): The agent to remove from the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        with contextlib.suppress(KeyError):
            del self._agents[agent]

    def remove(self, agent: Agent):
        """
        Remove an agent from the AgentSet.

        This method raises an error if the agent is not present.

        Args:
            agent (Agent): The agent to remove from the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        del self._agents[agent]

    def __getstate__(self):
        """
        Retrieve the state of the AgentSet for serialization.

        Returns:
            dict: A dictionary representing the state of the AgentSet.
        """
        return {"agents": list(self._agents.keys()), "model": self.model}

    def __setstate__(self, state):
        """
        Set the state of the AgentSet during deserialization.

        Args:
            state (dict): A dictionary representing the state to restore.
        """
        self.model = state["model"]
        self._update(state["agents"])

    @property
    def random(self) -> Random:
        """
        Provide access to the model's random number generator.

        Returns:
            Random: The random number generator associated with the model.
        """
        return self.model.random


# consider adding for performance reasons
# for Sequence: __reversed__, index, and count
# for MutableSet clear, pop, remove, __ior__, __iand__, __ixor__, and __isub__
