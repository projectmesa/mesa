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

    # Set when the agent is in several spaces that share a frame
    _mesa_stack = None

    @property
    def position(self) -> np.ndarray:
        """Position of the agent.

        This is a read-only view: assign a new position instead of changing it in
        place, so ``agent.position = agent.position + step`` rather than
        ``agent.position += step``.
        """
        return self.space._positions_ro[self._mesa_index]

    @position.setter
    def position(self, value: np.ndarray) -> None:
        # The agent is in several spaces that share a frame
        if self._mesa_stack is not None:
            self._mesa_stack.frame._write(self._mesa_stack, None, value)
            return

        if not self.space.in_bounds(value):
            if self.space.torus:
                value = self.space.torus_correct(value)
            else:
                raise ValueError(f"point {value} is outside the bounds of the space")

        self.space._agent_positions[self._mesa_index] = value

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
        """Remove and delete the agent from the model and continuous space."""
        super().remove()
        self.space._remove_agent(self)
        self._mesa_index = None
        self.space = None

    def get_neighbors_in_radius(
        self, radius: float | int = 1
    ) -> tuple[list, np.ndarray]:
        """Get neighbors within radius.

        Args:
            radius: radius within which to look for neighbors

        """
        agents, dists = self.space.get_agents_in_radius(self.position, radius=radius)
        logical = np.asarray([agent is not self for agent in agents])
        agents = list(compress(agents, logical))
        return agents, dists[logical]

    def get_nearest_neighbors(self, k: int = 1) -> tuple[list, np.ndarray]:
        """Get neighbors within radius.

        Args:
            k: the number of nearest neighbors to return

        """
        # return includes self, so we need to get k+1
        agents, dists = self.space.get_k_nearest_agents(self.position, k=k + 1)
        logical = np.asarray([agent is not self for agent in agents])
        agents = list(compress(agents, logical))
        return agents, dists[logical]
