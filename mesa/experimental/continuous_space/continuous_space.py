"""A Continous Space class."""


import warnings
from collections.abc import Sequence
from random import Random

import numpy as np
from scipy.spatial.distance import cdist

from mesa.agent import Agent, AgentSet


class ContinuousSpace:
    """Continuous space where each agent can have an arbitrary position.

    """

    def __init__(
        self,
        dimensions: Sequence[Sequence[float]],
        torus: bool = False,
        random: Random | None = None,
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

        self.dimensions = np.asarray(dimensions)
        self.ndims = self.dimensions.shape[0]
        self.size = self.dimensions[:, 1] - self.dimensions[:, 0]
        self.center = np.sum(self.dimensions, axis=1) / 2

        self.torus = torus


        n = 100
        self._agent_positions = np.zeros((n, self.dimensions.shape[0]))
        self._positions_in_use = np.zeros((n,), dtype=bool)  # effectively a mask over _agent_positions
        self._index_to_agent: dict[int, Agent] = {}
        self._agent_to_index: dict[Agent, int | None] = {}

    @property
    def agents(self) -> AgentSet:
        """Return an AgentSet with the agents in the space."""
        return AgentSet(list(self._agent_to_index), random=self.random)

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
            indices = np.where(self._positions_in_use == False)[0]

            if indices.size:
                index = indices[0]
            else:
                # we are out of space
                fraction = 0.2  # we add 20%
                n = int(round(fraction * self._agent_positions.shape[0]))
                self._agent_positions = np.vstack([self._agent_positions,
                                                  np.zeros((n, self.dimensions.shape[0]),)]
                                                  )
                self._positions_in_use = np.hstack([self._positions_in_use,
                                                    np.zeros((n,), dtype=bool)])
                index = np.where(self._positions_in_use == False)[0][0]

        self._positions_in_use[index] = True
        self._agent_to_index[agent] = index
        self._index_to_agent[index] = agent

        return index

    def _remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the space."""
        index = self._get_index_for_agent(agent)
        self._agent_to_index.pop(agent, None)
        self._index_to_agent.pop(index, None)
        self._positions_in_use[index] = False

    def calculate_distances(self, point):
        """Calculate the distance between the point and all agents."""
        if self.torus:
            delta = np.abs(point[np.newaxis, :] - self._agent_positions)
            delta = np.minimum(delta, 1 - delta)
            dists = np.linalg.norm(delta, axis=1)
        else:
            dists = cdist(point[np.newaxis, :], self._agent_positions)
        return dists

    def in_bounds(self, point) -> bool:
        """Check if point is inside the bounds of the space."""
        return ((point >= self.dimensions[:, 0]) & (point <= self.dimensions[:, 1])).all()

    def torus_correct(self, point) -> np.ndarray:
        """Apply a torus correction to the point."""
        return self.dimensions[:, 0] + np.mod(point - self.dimensions[:, 0], self.size)
