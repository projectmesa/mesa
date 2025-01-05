"""Continuous space agents."""

from __future__ import annotations

from itertools import compress
from typing import Protocol

import numpy as np

from mesa.agent import Agent
from mesa.experimental.continuous_space import ContinuousSpace


class HasPositionProtocol(Protocol):
    """Protocol for continuous space position holders."""

    position: np.ndarray


class ContinuousSpaceAgent(Agent):
    """A continuous space agent.

    Attributes:
        space (ContinuousSpace): the continuous space in which the agent is located
        position (np.ndarray): the position of the agent

    """

    __slots__ = ["_mesa_index", "space"]

    @property
    def position(self) -> np.ndarray:
        """Position of the agent."""
        return self.space.agent_positions[self.space._agent_to_index[self]]

    @position.setter
    def position(self, value: np.ndarray) -> None:
        if not self.space.in_bounds(value):
            if self.space.torus:
                value = self.space.torus_correct(value)
            else:
                raise ValueError(f"point {value} is outside the bounds of the space")

        self.space.agent_positions[self.space._agent_to_index[self]] = value

    @property
    def pos(self):  # noqa: D102
        # just here for compatibility with solara_viz.
        return self.position

    @pos.setter
    def pos(self, value):
        # just here for compatibility solara_viz.
        pass

    def __init__(self, space: ContinuousSpace, model):
        """Initialize a continuous space agent.

        Args:
            space: the continuous space in which the agent is located
            model: the model to which the agent belongs

        """
        super().__init__(model)
        self.space: ContinuousSpace = space
        self.space._add_agent(self)
        # self.position[:] = np.nan

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        super().remove()
        self.space._remove_agent(self)
        self._mesa_index = None
        self.space = None

    def get_neighbors_in_radius(self, radius: float = 1) -> tuple[list, np.ndarray]:
        """Get neighbors within radius.

        Args:
            radius: radius within which to look for neighbors

        """
        dists, agents = self.space.get_agents_in_radius(self.position, radius=radius)

        if dists.size == 0:
            return dists, agents

        logical = np.asarray([True if agent is not self else False for agent in agents])
        agents = list(compress(agents, logical))
        return agents, dists[logical]

    def get_nearest_neighbors(self, k: int = 1) -> tuple[list, np.ndarray]:
        """Get neighbors within radius.

        Args:
            k: the number of nearest neighbors to return

        """
        dists, agents = self.space.get_k_nearest_agents(self.position, k=k)
        logical = np.asarray([True if agent is not self else False for agent in agents])
        agents = list(compress(agents, logical))
        return agents, dists[logical]
