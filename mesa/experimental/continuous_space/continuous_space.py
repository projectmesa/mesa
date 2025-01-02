"""A Continyous Space class."""

import warnings
from collections.abc import Sequence
from random import Random

import numpy as np
from scipy.spatial.distance import cdist

from mesa.agent import Agent, AgentSet


class ContinuousSpace:
    """Continuous space where each agent can have an arbitrary position."""

    def __init__(
        self,
        dimensions: Sequence[Sequence[float]],
        torus: bool = False,
        random: Random | None = None,
        n_agents: int = 100,
    ) -> None:
        """Create a new continuous space."""
        if random is None:
            warnings.warn(
                "Random number generator not specified, this can make models non-reproducible. Please pass a random number generator explicitly",
                UserWarning,
                stacklevel=2,
            )
            random = Random()
        self.random = random

        self.dimensions: np.array = np.asarray(dimensions)
        self.ndims: int = self.dimensions.shape[0]
        self.size: np.array = self.dimensions[:, 1] - self.dimensions[:, 0]
        self.center: np.array = np.sum(self.dimensions, axis=1) / 2

        self.torus: bool = torus

        self._agent_positions: np.array = np.zeros(
            (n_agents, self.dimensions.shape[0]), dtype=float
        )
        self._agents: np.array = np.zeros((n_agents,), dtype=object)
        self._positions_in_use: np.array = np.zeros(
            (n_agents,), dtype=bool
        )  # effectively a mask over _agent_positions

        self._index_to_agent: dict[int, Agent] = {}
        self._agent_to_index: dict[Agent, int | None] = {}

    @property
    def agents(self) -> AgentSet:
        """Return an AgentSet with the agents in the space."""
        return AgentSet(self._agents[self._positions_in_use], random=self.random)

    @property
    def agent_positions(self) -> np.ndarray:
        """Return the positions of the agents in the space."""
        return self._agent_positions[self._positions_in_use]

    def _get_index_for_agent(self, agent: Agent) -> int:
        """Helper method to get the index for the agent.

        This method manages the numpy array with the agent positions and ensuring it is
        enlarged if and when needed.

        """
        try:
            return self._agent_to_index[agent]
        except KeyError:
            indices = np.where(~self._positions_in_use)[0]

            if indices.size > 0:
                index = indices[0]
            else:
                # we are out of space
                fraction = 0.2  # we add 20%  Fixme
                n = int(round(fraction * self._agent_positions.shape[0]))
                self._agent_positions = np.vstack(
                    [
                        self._agent_positions,
                        np.zeros(
                            (n, self.dimensions.shape[0]),
                        ),
                    ]
                )
                self._positions_in_use = np.hstack(
                    [self._positions_in_use, np.zeros((n,), dtype=bool)]
                )
                self._agents = np.hstack([self._agents, np.zeros((n,), dtype=object)])
                index = np.where(~self._positions_in_use)[0][0]

        self._positions_in_use[index] = True
        self._agents[index] = agent
        self._agent_to_index[agent] = index
        self._index_to_agent[index] = agent

        return index

    def _remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the space."""
        index = self._get_index_for_agent(agent)
        self._agent_to_index.pop(agent, None)
        self._index_to_agent.pop(index, None)
        self._positions_in_use[index] = False
        self._agents[index] = None

    def calculate_difference_vector(
        self, point: np.ndarray, indices=None
    ) -> np.ndarray:
        """Calculate the difference vector between the point and all agents"""
        point = np.asanyarray(point)
        positions = (
            self._agent_positions[indices]
            if indices is not None
            else self.agent_positions
        )

        if self.torus:
            delta = np.abs(point[np.newaxis, :] - positions)
            delta = np.minimum(
                delta, self.size - delta
            )  # fixme, should be based on size or maxima?
        else:
            delta = point[np.newaxis, :] - positions

        return delta

    def calculate_distances(self, point, indices=None) -> tuple[np.ndarray, np.ndarray]:
        """Calculate the distance between the point and all agents."""
        point = np.asanyarray(point)
        positions = (
            self._agent_positions[indices]
            if indices is not None
            else self.agent_positions
        )
        agents = (
            self._agents[indices]
            if indices is not None
            else self._agents[self._positions_in_use]
        )

        if self.torus:
            delta = np.abs(point[np.newaxis, :] - positions)
            delta = np.minimum(
                delta, self.size - delta
            )  # fixme, should be based on size or maxima?
            dists = np.linalg.norm(delta, axis=1)
        else:
            dists = cdist(point[np.newaxis, :], positions)[:, 0]
        return dists, agents

    def in_bounds(self, point) -> bool:
        """Check if point is inside the bounds of the space."""
        return bool(
            ((point >= self.dimensions[:, 0]) & (point <= self.dimensions[:, 1])).all()
        )

    def torus_correct(self, point) -> np.ndarray:
        """Apply a torus correction to the point."""
        return self.dimensions[:, 0] + np.mod(point - self.dimensions[:, 0], self.size)
