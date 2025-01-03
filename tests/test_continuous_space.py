"""Tests for continuous space."""

import numpy as np

from mesa import Model
from mesa.experimental.continuous_space import ContinuousSpace, ContinuousSpaceAgent


def test_continuous_space():
    """Test ContinuousSpace class."""
    model = Model(seed=42)

    dimensions = np.asarray([[0, 1], [-1, 0]])
    space = ContinuousSpace(dimensions, torus=False, random=model.random)

    # check some default fields
    assert space.ndims == 2
    assert np.all(space.size == [1, 1])
    assert np.all(space.center == [0.5, -0.5])
    assert len(space.agents) == 0

    # check in_bounds
    assert space.in_bounds([0.5, -0.5])
    assert not space.in_bounds([-0.5, -0.5])
    assert not space.in_bounds([1.5, -0.5])
    assert not space.in_bounds([0.5, 0.5])
    assert not space.in_bounds([0.5, -1.5])

    # check torus correction
    space = ContinuousSpace(dimensions, torus=True, random=model.random)
    assert np.all(space.torus_correct([-0.5, 0.5]) == [0.5, -0.5])
    assert np.all(space.torus_correct([0.5, -0.5]) == [0.5, -0.5])
    assert np.all(space.torus_correct([0.5, -0.5]) == [0.5, -0.5])
    assert np.all(space.torus_correct([1.5, -0.5]) == [0.5, -0.5])
    assert np.all(space.torus_correct([0.5, -1.5]) == [0.5, -0.5])

    # check 3d
    dimensions = np.asarray([[0, 2], [-2, 0], [-2, 2]])
    space = ContinuousSpace(dimensions, torus=False, random=model.random)

    # check some default fields
    assert space.ndims == 3
    assert np.all(space.size == [2, 2, 4])
    assert np.all(space.center == [1, -1, 0])

    # check in_bounds
    assert space.in_bounds([1, -1, 0])
    assert not space.in_bounds([-0.5, -1, 0])
    assert not space.in_bounds([2.5, -1, 0])
    assert not space.in_bounds([1, 0.5, 0])
    assert not space.in_bounds([1, -2.5, 0])
    assert not space.in_bounds([1, -1, -3])
    assert not space.in_bounds([1, -1, 3])
    assert not space.in_bounds([-0.5, -1, 3])
    assert not space.in_bounds([1, 0.5, 3])


def test_continuous_agent():
    """Test ContinuousSpaceAgent class."""
    model = Model(seed=42)

    dimensions = np.asarray([[0, 1], [0, 1]])
    space = ContinuousSpace(dimensions, torus=False, random=model.random)

    for _ in range(10):
        agent = ContinuousSpaceAgent(space, model)
        agent.position = [agent.random.random(), agent.random.random()]

    assert space.agent_positions.shape == (10, 2)
    for agent in space.agents:
        a = agent.position
        b = space._agent_positions[space._get_index_for_agent(agent)]
        assert np.all(a == b)

    # add more agents, triggering a resizeing of the array
    for _ in range(100):
        agent = ContinuousSpaceAgent(space, model)
        agent.position = [agent.random.random(), agent.random.random()]

    assert space.agent_positions.shape == (110, 2)
    for agent in space.agents:
        a = agent.position
        b = space._agent_positions[space._get_index_for_agent(agent)]
        assert np.all(a == b)

    # remove all agents and check if the view is updated throughout correctly
    for i, agent in enumerate(space.agents):
        agent.remove()
        assert space.agent_positions.shape == (110 - 1 - i, 2)


def test_distances():
    """Test ContinuousSpace.distance method."""
    # non torus
    model = Model(seed=42)
    dimensions = np.asarray([[0, 1], [0, 1]])
    space = ContinuousSpace(dimensions, torus=False, random=model.random)

    agent = ContinuousSpaceAgent(space, model)
    agent.position = [0.1, 0.1]

    distances, agents = space.calculate_distances([0.1, 0.9])
    assert np.all(
        distances
        == [
            0.8,
        ]
    )
    assert np.all(
        agents
        == [
            agent,
        ]
    )

    distances, agents = space.calculate_distances([0.9, 0.1])
    assert np.all(
        distances
        == [
            0.8,
        ]
    )
    assert np.all(
        agents
        == [
            agent,
        ]
    )

    # torus
    model = Model(seed=42)
    dimensions = np.asarray([[0, 1], [0, 1]])
    space = ContinuousSpace(dimensions, torus=True, random=model.random)

    agent = ContinuousSpaceAgent(space, model)
    agent.position = [0.1, 0.1]

    distances, agents = space.calculate_distances([0.1, 0.9])
    assert np.all(
        np.isclose(
            distances,
            [
                0.2,
            ],
        )
    )
    assert np.all(
        agents
        == [
            agent,
        ]
    )

    distances, agents = space.calculate_distances([0.9, 0.1])
    assert np.all(
        np.isclose(
            distances,
            [
                0.2,
            ],
        )
    )
    assert np.all(
        agents
        == [
            agent,
        ]
    )

    distances, agents = space.calculate_distances([0.9, 0.9])
    assert np.all(
        np.isclose(
            distances,
            [
                0.2 * 2**0.5,
            ],
        )
    )
    assert np.all(
        agents
        == [
            agent,
        ]
    )


# class TestSpaceToroidal(unittest.TestCase):
#     """Testing a toroidal continuous space."""
#
#     def setUp(self):
#         """Create a test space and populate with Mock Agents."""
#         self.space = ContinuousSpace(70, 20, True, -30, -30)
#         self.agents = []
#         for i, pos in enumerate(TEST_AGENTS):
#             a = MockAgent(i)
#             self.agents.append(a)
#             self.space.place_agent(a, pos)
#
#     def test_agent_positions(self):
#         """Ensure that the agents are all placed properly."""
#         for i, pos in enumerate(TEST_AGENTS):
#             a = self.agents[i]
#             assert a.pos == pos
#
#     def test_agent_matching(self):
#         """Ensure that the agents are all placed and indexed properly."""
#         for i, agent in self.space._index_to_agent.items():
#             assert agent.pos == tuple(self.space._agent_points[i, :])
#             assert i == self.space._agent_to_index[agent]
#
#     def test_distance_calculations(self):
#         """Test toroidal distance calculations."""
#         pos_1 = (-30, -30)
#         pos_2 = (70, 20)
#         assert self.space.get_distance(pos_1, pos_2) == 0
#
#         pos_3 = (-30, -20)
#         assert self.space.get_distance(pos_1, pos_3) == 10
#
#         pos_4 = (20, -5)
#         pos_5 = (20, -15)
#         assert self.space.get_distance(pos_4, pos_5) == 10
#
#         pos_6 = (-30, -29)
#         pos_7 = (21, -5)
#         assert self.space.get_distance(pos_6, pos_7) == np.sqrt(49**2 + 24**2)
#
#     def test_heading(self):
#         pos_1 = (-30, -30)
#         pos_2 = (70, 20)
#         self.assertEqual((0, 0), self.space.get_heading(pos_1, pos_2))
#
#         pos_1 = (65, -25)
#         pos_2 = (-25, -25)
#         self.assertEqual((10, 0), self.space.get_heading(pos_1, pos_2))
#
#     def test_neighborhood_retrieval(self):
#         """Test neighborhood retrieval."""
#         neighbors_1 = self.space.get_neighbors((-20, -20), 1)
#         assert len(neighbors_1) == 2
#
#         neighbors_2 = self.space.get_neighbors((40, -10), 10)
#         assert len(neighbors_2) == 0
#
#         neighbors_3 = self.space.get_neighbors((-30, -30), 10)
#         assert len(neighbors_3) == 1
#
