from __future__ import annotations

from typing import Protocol

import numpy as np

from mesa.agent import Agent
from mesa.experimental.continuous_space.continuous_space import ContinuousSpace


class HasPositionProtocol(Protocol):
    """Protocol for continuous space position holders."""

    position: np.ndarray


class ContinuousSpaceAgent(Agent):
    __slots__ = ["_mesa_index", "space"]

    @property
    def position(self) -> np.ndarray:
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
        super().__init__(model)
        self.space: ContinuousSpace = space
        self._mesa_index = self.space._get_index_for_agent(self)
        self.position[:] = np.NaN

    def remove(self) -> None:
        super().remove()
        self.space._remove_agent(self)
        self._mesa_index = None
        self.space = None

    def get_neigbors_in_radius(self, radius=1):
        distances = self.space.calculate_distances(self.position)
        indices = np.where(distances < radius)[0]

        # don't forget to remove our self
        agents = [
            self.space._index_to_agent[index]
            for index in indices
            if index != self._mesa_index
        ]
        return agents

    def get_nearest_neighbors(self, k=1):
        distances = self.space.calculate_distances(self.position)

        k += 1  # the distance calculation includes self, with a distance of 0, so we remove this later
        indices = np.argpartition(distances, k)[:k]

        # don't forget to remove our self
        agents = [
            self.space._index_to_agent[index]
            for index in indices
            if index != self._mesa_index
        ]
        return agents
