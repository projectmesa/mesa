"""
The agent class for Mesa framework.

Core Objects: Agent
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

from random import Random

# mypy
from typing import TYPE_CHECKING, Any, Callable, Iterator

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

        # Directly register the agent with the model
        if type(self) not in self.model._agents:
            self.model._agents[type(self)] = set()
        self.model._agents[type(self)].add(self)

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        if type(self) in self.model._agents:
            self.model._agents[type(self)].discard(self)

    def step(self) -> None:
        """A single step of the agent."""

    def advance(self) -> None:
        pass

    @property
    def random(self) -> Random:
        return self.model.random


class AgentSet:
    def __init__(self, agents: set[Agent], model: Model):
        self._agents = agents
        self.model = model

    def __len__(self):
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents)

    def __contains__(self, agent: Agent) -> bool:
        """Check if an agent is in the AgentSet."""
        return agent in self._agents

    def select(self, filter_func: Callable[[Agent], bool] | None = None) -> AgentSet:
        if filter_func is None:
            return AgentSet(set(self._agents), self.model)
        return AgentSet(
            {agent for agent in self._agents if filter_func(agent)}, self.model
        )

    def shuffle(self) -> AgentSet:
        shuffled_agents = list(self._agents)
        self.model.random.shuffle(shuffled_agents)
        return AgentSet(set(shuffled_agents), self.model)

    def sort(self, key: Callable[[Agent], Any], reverse: bool = False) -> AgentSet:
        sorted_agents = sorted(self._agents, key=key, reverse=reverse)
        return AgentSet(set(sorted_agents), self.model)

    def do_each(self, method_name: str):
        for agent in self._agents:
            getattr(agent, method_name)()

    # Additional methods like union, intersection, difference, etc., can be added as needed.
