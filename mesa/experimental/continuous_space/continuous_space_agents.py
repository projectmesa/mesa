"""Continuous space agents."""

from __future__ import annotations

from typing import Protocol, overload

import numpy as np

from mesa.agent import Agent
from mesa.experimental.continuous_space import ContinuousSpace

from line_profiler_pycharm import profile

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

    @property
    def pos(self):
        # just here for compatability with solara_viz.
        return self.position

    @pos.setter
    def pos(self, value):
        # just here for compatability solara_viz.
        pass

    def __init__(self, space: ContinuousSpace, model):
        """Initialize a continuous space agent.

        Args:
            space: the continuous space in which the agent is located
            model: the model to which the agent belongs

        """
        super().__init__(model)
        self.space: ContinuousSpace = space
        self._mesa_index = self.space._get_index_for_agent(self)
        self.position[:] = np.nan

    def remove(self) -> None:
        """Remove and delete the agent from the model."""
        super().remove()
        self.space._remove_agent(self)
        self._mesa_index = None
        self.space = None

    @overload
    def get_neighbors_in_radius(
        self, radius: int = 1, include_distance: bool = False
    ) -> np.ndarray[ContinuousSpaceAgent]: ...

    @overload
    def get_neighbors_in_radius(
        self, radius=1, include_distance: bool = True
    ) -> tuple[np.ndarray[ContinuousSpaceAgent], np.ndarray[float]]: ...

    def get_neighbors_in_radius(self, radius=1, include_distance=False):
        """Get neighbors within radius.

        Args:
            radius: radius within which to look for neighbors
            include_distance: include the distance information for each neighbor

        """
        dists, agents = self.space.calculate_distances(self.position)
        indices = np.where(dists <= radius)[0]
        indices = indices[indices != self._mesa_index]

        if include_distance:
            return agents[indices], dists[indices]
        else:
            return agents[indices]

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
        dists, agents = self.space.calculate_distances(self.position)

        k += 1  # the distance calculation includes self, with a distance of 0, so we remove this later
        indices = np.argpartition(dists, k)[:k]
        indices = indices[indices != self._mesa_index]

        if include_distance:
            return agents[indices], dists[indices]
        else:
            return agents[indices]
