import unittest

from mesa.space import ContinuousSpace
from test_grid import MockAgent

TEST_AGENTS = [(-20, -20), (-20, -20.05), (65, 18)]
OUTSIDE_POSITIONS = [(70, 10), (30, 20), (100, 10)]
REMOVAL_TEST_AGENTS = [(-20, -20), (-20, -20.05), (65, 18), (0, -11), (20, 20), (31, 41), (55, 32)]


class TestSpaceToroidal(unittest.TestCase):
    '''
    Testing a toroidal continuous space.
    '''

    def setUp(self):
        '''
        Create a test space and populate with Mock Agents.
        '''
        self.space = ContinuousSpace(70, 20, True, -30, -30, 100, 100)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        '''
        Ensure that the agents are all placed properly.
        '''
        for i, pos in enumerate(TEST_AGENTS):
            a = self.agents[i]
            assert a.pos == pos

    def test_agent_matching(self):
        '''
        Ensure that the agents are all placed and indexed properly.
        '''
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]

    def test_distance_calculations(self):
        '''
        Test toroidal distance calculations.
        '''
        pos_1 = (-30, -30)
        pos_2 = (70, 20)
        assert self.space.get_distance(pos_1, pos_2) == 0

        pos_3 = (-30, -20)
        assert self.space.get_distance(pos_1, pos_3) == 10

    def test_heading(self):
        pos_1 = (-30, -30)
        pos_2 = (70, 20)
        self.assertEqual((0, 0), self.space.get_heading(pos_1, pos_2))

        pos_1 = (65, -25)
        pos_2 = (-25, -25)
        self.assertEqual((10, 0), self.space.get_heading(pos_1, pos_2))

    def test_neighborhood_retrieval(self):
        '''
        Test neighborhood retrieval
        '''
        neighbors_1 = self.space.get_neighbors((-20, -20), 1)
        assert len(neighbors_1) == 2

        neighbors_2 = self.space.get_neighbors((40, -10), 10)
        assert len(neighbors_2) == 0

        neighbors_3 = self.space.get_neighbors((-30, -30), 10)
        assert len(neighbors_3) == 1

    def test_bounds(self):
        '''
        Test positions outside of boundary
        '''
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
    '''
    Testing a toroidal continuous space.
    '''

    def setUp(self):
        '''
        Create a test space and populate with Mock Agents.
        '''
        self.space = ContinuousSpace(70, 20, False, -30, -30, 100, 100)
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_agent_positions(self):
        '''
        Ensure that the agents are all placed properly.
        '''
        for i, pos in enumerate(TEST_AGENTS):
            a = self.agents[i]
            assert a.pos == pos

    def test_agent_matching(self):
        '''
        Ensure that the agents are all placed and indexed properly.
        '''
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]

    def test_distance_calculations(self):
        '''
        Test toroidal distance calculations.
        '''

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
        '''
        Test neighborhood retrieval
        '''
        neighbors_1 = self.space.get_neighbors((-20, -20), 1)
        assert len(neighbors_1) == 2

        neighbors_2 = self.space.get_neighbors((40, -10), 10)
        assert len(neighbors_2) == 0

        neighbors_3 = self.space.get_neighbors((-30, -30), 10)
        assert len(neighbors_3) == 0

    def test_bounds(self):
        '''
        Test positions outside of boundary
        '''
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
    '''
    Testing a continuous space for agent mapping during removal.
    '''

    def setUp(self):
        '''
        Create a test space and populate with Mock Agents.
        '''
        self.space = ContinuousSpace(70, 50, False, -30, -30, 100, 100)
        self.agents = []
        for i, pos in enumerate(REMOVAL_TEST_AGENTS):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_remove_first(self):
        '''
        Test removing the first entry
        '''
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
        '''
        Test removing the last entry
        '''
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
        '''
        Test removing a middle entry
        '''
        agent_to_remove = self.agents[3]
        self.space.remove_agent(agent_to_remove)
        for i, agent in self.space._index_to_agent.items():
            assert agent.pos == tuple(self.space._agent_points[i, :])
            assert i == self.space._agent_to_index[agent]
        assert agent_to_remove not in self.space._agent_to_index
        assert agent_to_remove.pos is None
        with self.assertRaises(Exception):
            self.space.remove_agent(agent_to_remove)
