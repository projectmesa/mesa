"""Continuous space agents."""

from __future__ import annotations

from typing import Protocol, overload

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
        return self.space._agent_positions[self._mesa_index]

    @position.setter
    def position(self, value: np.ndarray) -> None:
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
        self._mesa_index = self.space._get_index_for_agent(self)
        self.position[:] = np.NaN

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        super().remove()
        self.space._remove_agent(self)
        self._mesa_index = None
        self.space = None

    @overload
    def get_neighbors_in_radius(
        self, radius: int = 1, include_distance: bool = False
    ) -> list[ContinuousSpaceAgent]: ...

    @overload
    def get_neighbors_in_radius(
        self, radius=1, include_distance: bool = True
    ) -> list[tuple[ContinuousSpaceAgent, float]]: ...

    def get_neighbors_in_radius(self, radius=1, include_distance=False):
        """Get neighbors within radius.

        Args:
            radius: radius within which to look for neighbors
            include_distance: include the distance information for each neighbor

        """
        distances = self.space.calculate_distances(self.position)
        indices = np.where(distances <= radius)[0]

        if include_distance:
            # don't forget to remove our self
            agents = [
                (self.space._index_to_agent[index], distances[index])
                for index in indices
                if index != self._mesa_index
            ]
        else:
            # don't forget to remove our self
            agents = [
                self.space._index_to_agent[index]
                for index in indices
                if index != self._mesa_index
            ]
        return agents

    @overload
    def get_nearest_neighbors(
        self, k: int = 1, include_distance: bool = False
    ) -> list[ContinuousSpaceAgent]: ...

    @overload
    def get_nearest_neighbors(
        self, k=1, include_distance: bool = True
    ) -> list[tuple[ContinuousSpaceAgent, float]]: ...

    def get_nearest_neighbors(self, k=1, include_distance=False):
        """Get neighbors within radius.

        Args:
            k: the number of nearest neighbors to return
            include_distance: include the distance information for each neighbor

        """
        distances = self.space.calculate_distances(self.position)

        k += 1  # the distance calculation includes self, with a distance of 0, so we remove this later
        indices = np.argpartition(distances, k)[:k]

        # don't forget to remove our self
        if include_distance:
            # don't forget to remove our self
            agents = [
                (self.space._index_to_agent[index], distances[index])
                for index in indices
                if index != self._mesa_index
            ]
        else:
            # don't forget to remove our self
            agents = [
                self.space._index_to_agent[index]
                for index in indices
                if index != self._mesa_index
            ]
        return agents
