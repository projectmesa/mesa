"""A Continuous Space class."""

import warnings
from collections.abc import Sequence
from itertools import compress
from random import Random

import numpy as np
from scipy.spatial.distance import cdist

from mesa.agent import Agent, AgentSet

from typing import Iterable, Sequence
from numpy.typing import ArrayLike

class ContinuousSpace:
    """Continuous space where each agent can have an arbitrary position."""

    @property
    def x_min(self):  # noqa: D102
        # compatibility with solara_viz
        return self.dimensions[0, 0]

    @property
    def x_max(self):  # noqa: D102
        # compatibility with solara_viz
        return self.dimensions[0, 1]

    @property
    def y_min(self):  # noqa: D102
        # compatibility with solara_viz
        return self.dimensions[1, 0]

    @property
    def y_max(self):  # noqa: D102
        # compatibility with solara_viz
        return self.dimensions[1, 1]

    @property
    def width(self):  # noqa: D102
        # compatibility with solara_viz
        return self.size[0]

    @property
    def height(self):  # noqa: D102
        # compatibility with solara_viz
        return self.size[1]

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

        self._agent_positions: np.array = np.empty(
            (n_agents, self.dimensions.shape[0]), dtype=float
        )
        # self._agents: np.array = np.zeros((n_agents,), dtype=object)

        self.active_agents = []
        self.agent_positions: (
            np.array
        )  # a view on _agent_positions containing all active positions

        self._n_agents = 0

        self._index_to_agent: dict[int, Agent] = {}
        self._agent_to_index: dict[Agent, int | None] = {}

    @property
    def agents(self) -> AgentSet:
        """Return an AgentSet with the agents in the space."""
        return AgentSet(self.active_agents, random=self.random)

    def _add_agent(self, agent: Agent) -> int:
        """Helper method to get the index for the agent.

        This method manages the numpy array with the agent positions and ensuring it is
        enlarged if and when needed.

        """
        index = self._n_agents
        self._n_agents += 1

        if self._agent_positions.shape[0] <= index:
            # we are out of space
            fraction = 0.2  # we add 20%  Fixme
            n = int(round(fraction * self._n_agents))
            self._agent_positions = np.vstack(
                [
                    self._agent_positions,
                    np.empty(
                        (n, self.dimensions.shape[0]),
                    ),
                ]
            )

        self._agent_to_index[agent] = index
        self._index_to_agent[index] = agent

        # we want to maintain a view rather than a copy on the active agents and positions
        # this is essential for the performance of the rest of this code
        self.active_agents.append(agent)
        self.agent_positions = self._agent_positions[0 : self._n_agents]

        return index

    def _remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the space."""
        index = self._agent_to_index[agent]
        self._agent_to_index.pop(agent, None)
        self._index_to_agent.pop(index, None)
        del self.active_agents[index]

        # we update all indices
        for agent in self.active_agents[index::]:
            old_index = self._agent_to_index[agent]
            self._agent_to_index[agent] = old_index - 1
            self._index_to_agent[old_index - 1] = agent

        # we move all data below the removed agent one row up
        self._agent_positions[index : self._n_agents - 1] = self._agent_positions[
            index + 1 : self._n_agents
        ]
        self._n_agents -= 1
        self.agent_positions = self._agent_positions[0 : self._n_agents]

    def calculate_difference_vector(self, point: np.ndarray, agents=None) -> np.ndarray:
        """Calculate the difference vector between the point and all agents."""
        point = np.asanyarray(point)
        positions = (
            self.agent_positions
            if agents is None
            else self._agent_positions[[self._agent_to_index[a] for a in agents]]
        )

        delta = positions - point

        if self.torus:
            inverse_delta = delta - np.sign(delta) * self.size

            # we need to use the lowest absolute value from delta and inverse delta
            logical = np.abs(delta) < np.abs(inverse_delta)

            out = np.zeros(delta.shape)
            out[logical] = delta[logical]
            out[~logical] = inverse_delta[~logical]

            delta = out

        return delta

    def calculate_distances(self, point:ArrayLike, agents:Iterable[Agent]|None=None) -> tuple[np.ndarray, list]:
        """Calculate the distance between the point and all agents."""
        point = np.asanyarray(point)

        if agents is None:
            positions = self.agent_positions
            agents = self.active_agents
        else:
            positions = self._agent_positions[[self._agent_to_index[a] for a in agents]]
            agents = np.asarray(agents)

        if self.torus:
            delta = np.abs(point - positions)
            delta = np.minimum(delta, self.size - delta, out=delta)

            # + is much faster than np.sum or array.sum
            dists = delta[:, 0] ** 2
            for i in range(1, self.ndims):
                dists += delta[:, i] ** 2
            dists = np.sqrt(dists)
        else:
            dists = cdist(point[np.newaxis, :], positions)[0, :]
        return dists, agents

    def get_agents_in_radius(self, point:ArrayLike, radius:float|int=1) -> tuple[list, np.ndarray]:
        """Return the agents and their distances within a radius for the point."""
        distances, agents = self.calculate_distances(point)
        logical = distances <= radius
        agents = list(compress(agents, logical))
        return (
            agents,
            distances[logical],
        )

    def get_k_nearest_agents(self, point:ArrayLike, k:int=1) -> tuple[list, np.ndarray]:
        """Return the k nearest agents and their distances to the point.

        Notes:
            This method returns exactly k agents, ignoring ties

        """
        dists, agents = self.calculate_distances(point)

        indices = np.argpartition(dists, k)[:k]
        agents = [agents[i] for i in indices]
        return agents, dists[indices]

    def in_bounds(self, point) -> bool:
        """Check if point is inside the bounds of the space."""
        return bool(
            ((point >= self.dimensions[:, 0]) & (point <= self.dimensions[:, 1])).all()
        )

    def torus_correct(self, point) -> np.ndarray:
        """Apply a torus correction to the point."""
        return self.dimensions[:, 0] + np.mod(point - self.dimensions[:, 0], self.size)
