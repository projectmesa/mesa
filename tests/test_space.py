import unittest

import networkx as nx
import numpy as np
import pytest

from mesa.space import ContinuousSpace, NetworkGrid, SingleGrid
from tests.test_grid import MockAgent

TEST_AGENTS = [(-20, -20), (-20, -20.05), (65, 18)]
TEST_AGENTS_GRID = [(1, 1), (10, 0), (10, 10)]
TEST_AGENTS_NETWORK_SINGLE = [0, 1, 5]
TEST_AGENTS_NETWORK_MULTIPLE = [0, 1, 1]
OUTSIDE_POSITIONS = [(70, 10), (30, 20), (100, 10)]
REMOVAL_TEST_AGENTS = [
    (-20, -20),
    (-20, -20.05),
    (65, 18),
    (0, -11),
    (20, 20),
    (31, 41),
    (55, 32),
]
TEST_AGENTS_PERF = 200000


@pytest.mark.skip(reason="a perf test will slow down the CI")
class TestSpacePerformance(unittest.TestCase):
    """
    Testing adding many agents for a continuous space.
    """

    def setUp(self):
        """
        Create a test space and populate with Mock Agents.
        """
        self.space = ContinuousSpace(10, 10, True, -10, -10)

    def test_agents_add_many(self):
        """
        Add many agents
        """
        positions = np.random.rand(TEST_AGENTS_PERF, 2)
        for i in range(TEST_AGENTS_PERF):
            a = MockAgent(i, None)
            pos = [positions[i, 0], positions[i, 1]]
            self.space.place_agent(a, pos)


class TestSpaceToroidal(unittest.TestCase):
    """
    Testing a toroidal continuous space.
    """

    def setUp(self):
        """
        Create a test space and populate with Mock Agents.
        """
        self.space = ContinuousSpace(70, 20, True, -30, -30)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        """
        Ensure that the agents are all placed properly.
        """
        for i, pos in enumerate(TEST_AGENTS):
            a = self.agents[i]
            assert a.pos == pos

    def test_agent_matching(self):
        """
        Ensure that the agents are all placed and indexed properly.
        """
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]

    def test_distance_calculations(self):
        """
        Test toroidal distance calculations.
        """
        pos_1 = (-30, -30)
        pos_2 = (70, 20)
        assert self.space.get_distance(pos_1, pos_2) == 0

        pos_3 = (-30, -20)
        assert self.space.get_distance(pos_1, pos_3) == 10

        pos_4 = (20, -5)
        pos_5 = (20, -15)
        assert self.space.get_distance(pos_4, pos_5) == 10

        pos_6 = (-30, -29)
        pos_7 = (21, -5)
        assert self.space.get_distance(pos_6, pos_7) == np.sqrt(49**2 + 24**2)

    def test_heading(self):
        pos_1 = (-30, -30)
        pos_2 = (70, 20)
        self.assertEqual((0, 0), self.space.get_heading(pos_1, pos_2))

        pos_1 = (65, -25)
        pos_2 = (-25, -25)
        self.assertEqual((10, 0), self.space.get_heading(pos_1, pos_2))

    def test_neighborhood_retrieval(self):
        """
        Test neighborhood retrieval
        """
        neighbors_1 = self.space.get_neighbors((-20, -20), 1)
        assert len(neighbors_1) == 2

        neighbors_2 = self.space.get_neighbors((40, -10), 10)
        assert len(neighbors_2) == 0

        neighbors_3 = self.space.get_neighbors((-30, -30), 10)
        assert len(neighbors_3) == 1

    def test_bounds(self):
        """
        Test positions outside of boundary
        """
        boundary_agents = []
        for i, pos in enumerate(OUTSIDE_POSITIONS):
            a = MockAgent(len(self.agents) + i, None)
            boundary_agents.append(a)
            self.space.place_agent(a, pos)

        for a, pos in zip(boundary_agents, OUTSIDE_POSITIONS):
            adj_pos = self.space.torus_adj(pos)
            assert a.pos == adj_pos

        a = self.agents[0]
        for pos in OUTSIDE_POSITIONS:
            assert self.space.out_of_bounds(pos)
            self.space.move_agent(a, pos)


class TestSpaceNonToroidal(unittest.TestCase):
    """
    Testing a toroidal continuous space.
    """

    def setUp(self):
        """
        Create a test space and populate with Mock Agents.
        """
        self.space = ContinuousSpace(70, 20, False, -30, -30)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        """
        Ensure that the agents are all placed properly.
        """
        for i, pos in enumerate(TEST_AGENTS):
            a = self.agents[i]
            assert a.pos == pos

    def test_agent_matching(self):
        """
        Ensure that the agents are all placed and indexed properly.
        """
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]

    def test_distance_calculations(self):
        """
        Test toroidal distance calculations.
        """

        pos_2 = (70, 20)
        pos_3 = (-30, -20)
        assert self.space.get_distance(pos_2, pos_3) == 107.70329614269008

    def test_heading(self):
        pos_1 = (-30, -30)
        pos_2 = (70, 20)
        self.assertEqual((100, 50), self.space.get_heading(pos_1, pos_2))

        pos_1 = (65, -25)
        pos_2 = (-25, -25)
        self.assertEqual((-90, 0), self.space.get_heading(pos_1, pos_2))

    def test_neighborhood_retrieval(self):
        """
        Test neighborhood retrieval
        """
        neighbors_1 = self.space.get_neighbors((-20, -20), 1)
        assert len(neighbors_1) == 2

        neighbors_2 = self.space.get_neighbors((40, -10), 10)
        assert len(neighbors_2) == 0

        neighbors_3 = self.space.get_neighbors((-30, -30), 10)
        assert len(neighbors_3) == 0

    def test_bounds(self):
        """
        Test positions outside of boundary
        """
        for i, pos in enumerate(OUTSIDE_POSITIONS):
            a = MockAgent(len(self.agents) + i, None)
            with self.assertRaises(Exception):
                self.space.place_agent(a, pos)

        a = self.agents[0]
        for pos in OUTSIDE_POSITIONS:
            assert self.space.out_of_bounds(pos)
            with self.assertRaises(Exception):
                self.space.move_agent(a, pos)


class TestSpaceAgentMapping(unittest.TestCase):
    """
    Testing a continuous space for agent mapping during removal.
    """

    def setUp(self):
        """
        Create a test space and populate with Mock Agents.
        """
        self.space = ContinuousSpace(70, 50, False, -30, -30)
        self.agents = []
        for i, pos in enumerate(REMOVAL_TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_remove_first(self):
        """
        Test removing the first entry
        """
        agent_to_remove = self.agents[0]
        self.space.remove_agent(agent_to_remove)
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]
        assert agent_to_remove not in self.space._agent_to_index
        assert agent_to_remove.pos is None
        with self.assertRaises(Exception):
            self.space.remove_agent(agent_to_remove)

    def test_remove_last(self):
        """
        Test removing the last entry
        """
        agent_to_remove = self.agents[-1]
        self.space.remove_agent(agent_to_remove)
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]
        assert agent_to_remove not in self.space._agent_to_index
        assert agent_to_remove.pos is None
        with self.assertRaises(Exception):
            self.space.remove_agent(agent_to_remove)

    def test_remove_middle(self):
        """
        Test removing a middle entry
        """
        agent_to_remove = self.agents[3]
        self.space.remove_agent(agent_to_remove)
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]
        assert agent_to_remove not in self.space._agent_to_index
        assert agent_to_remove.pos is None
        with self.assertRaises(Exception):
            self.space.remove_agent(agent_to_remove)


class TestSingleGrid(unittest.TestCase):
    def setUp(self):
        self.space = SingleGrid(50, 50, False)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS_GRID):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        """
        Ensure that the agents are all placed properly.
        """
        for i, pos in enumerate(TEST_AGENTS_GRID):
            a = self.agents[i]
            assert a.pos == pos

    def test_remove_agent(self):
        for i, pos in enumerate(TEST_AGENTS_GRID):
            a = self.agents[i]
            assert a.pos == pos
            assert self.space[pos[0]][pos[1]] == a
            self.space.remove_agent(a)
            assert a.pos is None
            assert self.space[pos[0]][pos[1]] is None

    def test_empty_cells(self):
        if self.space.exists_empty_cells():
            pytest.deprecated_call(self.space.find_empty)
            for i, pos in enumerate(list(self.space.empties)):
                a = MockAgent(-i, pos)
                self.space.position_agent(a, x=pos[0], y=pos[1])
        assert self.space.find_empty() is None
        with self.assertRaises(Exception):
            self.space.move_to_empty(a)

    def move_agent(self):
        agent_number = 0
        initial_pos = TEST_AGENTS_GRID[agent_number]
        final_pos = (7, 7)

        _agent = self.agents[agent_number]

        assert _agent.pos == initial_pos
        assert self.space[initial_pos[0]][initial_pos[1]] == _agent
        assert self.space[final_pos[0]][final_pos[1]] is None
        self.space.move_agent(_agent, final_pos)
        assert _agent.pos == final_pos
        assert self.space[initial_pos[0]][initial_pos[1]] is None
        assert self.space[final_pos[0]][final_pos[1]] == _agent


class TestSingleNetworkGrid(unittest.TestCase):
    GRAPH_SIZE = 10

    def setUp(self):
        """
        Create a test network grid and populate with Mock Agents.
        """
        G = nx.cycle_graph(TestSingleNetworkGrid.GRAPH_SIZE)  # noqa: N806
        self.space = NetworkGrid(G)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS_NETWORK_SINGLE):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        """
        Ensure that the agents are all placed properly.
        """
        for i, pos in enumerate(TEST_AGENTS_NETWORK_SINGLE):
            a = self.agents[i]
            assert a.pos == pos

    def test_get_neighbors(self):
        assert len(self.space.get_neighbors(0, include_center=True)) == 3
        assert len(self.space.get_neighbors(0, include_center=False)) == 2
        assert len(self.space.get_neighbors(2, include_center=True, radius=3)) == 7
        assert len(self.space.get_neighbors(2, include_center=False, radius=3)) == 6

    def test_move_agent(self):
        initial_pos = 1
        agent_number = 1
        final_pos = TestSingleNetworkGrid.GRAPH_SIZE - 1

        _agent = self.agents[agent_number]

        assert _agent.pos == initial_pos
        assert _agent in self.space.G.nodes[initial_pos]["agent"]
        assert _agent not in self.space.G.nodes[final_pos]["agent"]
        self.space.move_agent(_agent, final_pos)
        assert _agent.pos == final_pos
        assert _agent not in self.space.G.nodes[initial_pos]["agent"]
        assert _agent in self.space.G.nodes[final_pos]["agent"]

    def test_remove_agent(self):
        for i, pos in enumerate(TEST_AGENTS_NETWORK_SINGLE):
            a = self.agents[i]
            assert a.pos == pos
            assert a in self.space.G.nodes[pos]["agent"]
            self.space.remove_agent(a)
            assert a.pos is None
            assert a not in self.space.G.nodes[pos]["agent"]

    def test_is_cell_empty(self):
        assert not self.space.is_cell_empty(0)
        assert self.space.is_cell_empty(TestSingleNetworkGrid.GRAPH_SIZE - 1)

    def test_get_cell_list_contents(self):
        assert self.space.get_cell_list_contents([0]) == [self.agents[0]]
        assert self.space.get_cell_list_contents(
            list(range(TestSingleNetworkGrid.GRAPH_SIZE))
        ) == [self.agents[0], self.agents[1], self.agents[2]]

    def test_get_all_cell_contents(self):
        assert self.space.get_all_cell_contents() == [
            self.agents[0],
            self.agents[1],
            self.agents[2],
        ]


class TestMultipleNetworkGrid(unittest.TestCase):
    GRAPH_SIZE = 3

    def setUp(self):
        """
        Create a test network grid and populate with Mock Agents.
        """
        G = nx.complete_graph(TestMultipleNetworkGrid.GRAPH_SIZE)  # noqa: N806
        self.space = NetworkGrid(G)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS_NETWORK_MULTIPLE):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        """
        Ensure that the agents are all placed properly.
        """
        for i, pos in enumerate(TEST_AGENTS_NETWORK_MULTIPLE):
            a = self.agents[i]
            assert a.pos == pos

    def test_get_neighbors(self):
        assert (
            len(self.space.get_neighbors(0, include_center=True))
            == TestMultipleNetworkGrid.GRAPH_SIZE
        )
        assert (
            len(self.space.get_neighbors(0, include_center=False))
            == TestMultipleNetworkGrid.GRAPH_SIZE - 1
        )

    def test_move_agent(self):
        initial_pos = 1
        agent_number = 1
        final_pos = 0

        _agent = self.agents[agent_number]

        assert _agent.pos == initial_pos
        assert _agent in self.space.G.nodes[initial_pos]["agent"]
        assert _agent not in self.space.G.nodes[final_pos]["agent"]
        assert len(self.space.G.nodes[initial_pos]["agent"]) == 2
        assert len(self.space.G.nodes[final_pos]["agent"]) == 1

        self.space.move_agent(_agent, final_pos)

        assert _agent.pos == final_pos
        assert _agent not in self.space.G.nodes[initial_pos]["agent"]
        assert _agent in self.space.G.nodes[final_pos]["agent"]
        assert len(self.space.G.nodes[initial_pos]["agent"]) == 1
        assert len(self.space.G.nodes[final_pos]["agent"]) == 2

    def test_is_cell_empty(self):
        assert not self.space.is_cell_empty(0)
        assert not self.space.is_cell_empty(1)
        assert self.space.is_cell_empty(2)

    def test_get_cell_list_contents(self):
        assert self.space.get_cell_list_contents([0]) == [self.agents[0]]
        assert self.space.get_cell_list_contents([1]) == [
            self.agents[1],
            self.agents[2],
        ]
        assert self.space.get_cell_list_contents(
            list(range(TestMultipleNetworkGrid.GRAPH_SIZE))
        ) == [self.agents[0], self.agents[1], self.agents[2]]

    def test_get_all_cell_contents(self):
        assert self.space.get_all_cell_contents() == [
            self.agents[0],
            self.agents[1],
            self.agents[2],
        ]


if __name__ == "__main__":
    unittest.main()
