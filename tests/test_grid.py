'''
Test the Grid objects.
'''
import unittest

from mesa.space import Grid, SingleGrid, MultiGrid

# Initial agent positions for testing
#              X ---- >
TEST_GRID = [[0, 1, 0, 1, 0],   # Y
             [0, 1, 1, 0, 0],   # |
             [0, 0, 0, 1, 0]]   # V


class MockAgent:
    '''
    Minimalistic agent for testing purposes.
    '''
    def __init__(self, unique_id, pos):
        self.unique_id = unique_id
        self.pos = pos


class TestBaseGrid(unittest.TestCase):
    '''
    Testing a non-toroidal grid.
    '''

    torus = False

    def setUp(self):
        '''
        Create a test non-toroidal grid and populate it with Mock Agents
        '''
        self.grid = Grid(3, 5, self.torus)
        self.agents = []
        counter = 0
        for y in range(3):
            for x in range(5):
                if TEST_GRID[y][x] == 0:
                    continue
                counter += 1
                # Create and place the mock agent
                a = MockAgent(counter, None)
                self.agents.append(a)
                self.grid.place_agent(a, (x, y))

    def test_agent_positions(self):
        '''
        Ensure that the agents are all placed properly.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert self.grid[y][x] == agent

    def test_cell_agent_reporting(self):
        '''
        Ensure that if an agent is in a cell, get_cell_list_contents accurately
        reports that fact.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert agent in self.grid.get_cell_list_contents([(x, y)])

    def test_listfree_cell_agent_reporting(self):
        '''
        Ensure that if an agent is in a cell, get_cell_list_contents accurately
        reports that fact, even when single position is not wrapped in a list.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert agent in self.grid.get_cell_list_contents((x, y))

    def test_iter_cell_agent_reporting(self):
        '''
        Ensure that if an agent is in a cell, iter_cell_list_contents
        accurately reports that fact.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert agent in self.grid.iter_cell_list_contents([(x, y)])

    def test_listfree_iter_cell_agent_reporting(self):
        '''
        Ensure that if an agent is in a cell, iter_cell_list_contents
        accurately reports that fact, even when single position is not
        wrapped in a list.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert agent in self.grid.iter_cell_list_contents((x, y))

    def test_neighbors(self):
        '''
        Test the base neighborhood methods on the non-toroid.
        '''

        neighborhood = self.grid.get_neighborhood((1, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((4, 1), moore=True)
        assert len(neighborhood) == 5

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 2

        neighbors = self.grid.get_neighbors((4, 1), moore=False)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((4, 1), moore=True)
        assert len(neighbors) == 2

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 3

        neighbors = self.grid.get_neighbors((3, 1), moore=False, radius=2)
        assert len(neighbors) == 4

    def test_coord_iter(self):
        ci = self.grid.coord_iter()

        # no agent in first space
        first = next(ci)
        assert first[0] is None
        assert first[1] == 0
        assert first[2] == 0

        # first agent in the second space
        second = next(ci)
        assert second[0].unique_id == 1
        assert second[0].pos == (1, 0)
        assert second[1] == 1
        assert second[2] == 0


class TestBaseGridTorus(TestBaseGrid):
    '''
    Testing the toroidal base grid.
    '''

    torus = True

    def test_neighbors(self):
        '''
        Test the toroidal neighborhood methods.
        '''

        neighborhood = self.grid.get_neighborhood((1, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((4, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 4

        neighbors = self.grid.get_neighbors((4, 1), moore=False)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((4, 1), moore=True)
        assert len(neighbors) == 2

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 3

        neighbors = self.grid.get_neighbors((3, 1), moore=False, radius=2)
        assert len(neighbors) == 4


class TestSingleGrid(unittest.TestCase):
    '''
    Test the SingleGrid object.

    Since it inherits from Grid, all the functionality tested above should
    work here too. Instead, this tests the enforcement.
    '''

    def setUp(self):
        '''
        Create a test non-toroidal grid and populate it with Mock Agents
        '''
        self.grid = SingleGrid(3, 5, True)
        self.agents = []
        counter = 0
        for y in range(3):
            for x in range(5):
                if TEST_GRID[y][x] == 0:
                    continue
                counter += 1
                # Create and place the mock agent
                a = MockAgent(counter, None)
                self.agents.append(a)
                self.grid.place_agent(a, (x, y))

    def test_enforcement(self):
        '''
        Test the SingleGrid empty count and enforcement.
        '''

        assert len(self.grid.empties) == 10
        a = MockAgent(100, None)
        with self.assertRaises(Exception):
            self.grid._place_agent((1, 0), a)

        # Place the agent in an empty cell
        self.grid.position_agent(a)
        assert a.pos not in self.grid.empties
        assert len(self.grid.empties) == 9
        for i in range(10):
            self.grid.move_to_empty(a)
        assert len(self.grid.empties) == 9

        # Place agents until the grid is full
        for i in range(9):
            a = MockAgent(101 + i, None)
            self.grid.position_agent(a)
        assert len(self.grid.empties) == 0

        a = MockAgent(110, None)
        with self.assertRaises(Exception):
            self.grid.position_agent(a)
        with self.assertRaises(Exception):
            self.move_to_empty(self.agents[0])

# Number of agents at each position for testing
TEST_MULTIGRID = [[0, 1, 0, 2, 0],
                  [0, 1, 5, 0, 0],
                  [0, 0, 0, 3, 0]]


class TestMultiGrid(unittest.TestCase):
    '''
    Testing a toroidal MultiGrid
    '''

    torus = True

    def setUp(self):
        '''
        Create a test non-toroidal grid and populate it with Mock Agents
        '''
        self.grid = MultiGrid(3, 5, self.torus)
        self.agents = []
        counter = 0
        for y in range(3):
            for x in range(5):
                for i in range(TEST_MULTIGRID[y][x]):
                    counter += 1
                    # Create and place the mock agent
                    a = MockAgent(counter, None)
                    self.agents.append(a)
                    self.grid.place_agent(a, (x, y))

    def test_agent_positions(self):
        '''
        Ensure that the agents are all placed properly on the MultiGrid.
        '''
        for agent in self.agents:
            x, y = agent.pos
            assert agent in self.grid[y][x]

    def test_neighbors(self):
        '''
        Test the toroidal MultiGrid neighborhood methods.
        '''

        neighborhood = self.grid.get_neighborhood((1, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((4, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 4

        neighbors = self.grid.get_neighbors((4, 1), moore=False)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((4, 1), moore=True)
        assert len(neighbors) == 5

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 7

        neighbors = self.grid.get_neighbors((3, 1), moore=False, radius=2)
        assert len(neighbors) == 11
