'''
Test the Grid objects.
'''
import unittest

from mesa.space import Grid, SingleGrid, MultiGrid

# Initial agent positions for testing
#
# --- visual aid ----
#   0 0 0
#   1 1 0
#   0 1 0
#   1 0 1
#   0 0 1
# -------------------
TEST_GRID = [
    [0, 1, 0, 1, 0],
    [0, 0, 1, 1, 0],
    [1, 1, 0, 0, 0]
]


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
        width = 3    # width of grid
        height = 5    # height of grid
        self.grid = Grid(width, height, self.torus)
        self.agents = []
        counter = 0
        for x in range(width):
            for y in range(height):
                if TEST_GRID[x][y] == 0:
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
            assert self.grid[x][y] == agent

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

        neighborhood = self.grid.get_neighborhood((1, 4), moore=False)
        assert len(neighborhood) == 3

        neighborhood = self.grid.get_neighborhood((1, 4), moore=True)
        assert len(neighborhood) == 5

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 2

        neighbors = self.grid.get_neighbors((4, 1), moore=False)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((4, 1), moore=True)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 3

        neighbors = self.grid.get_neighbors((1, 3), moore=False, radius=2)
        assert len(neighbors) == 2

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
        assert second[0].pos == (0, 1)
        assert second[1] == 0
        assert second[2] == 1


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

        neighborhood = self.grid.get_neighborhood((1, 4), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 4

        neighbors = self.grid.get_neighbors((1, 4), moore=False)
        assert len(neighbors) == 1

        neighbors = self.grid.get_neighbors((1, 4), moore=True)
        assert len(neighbors) == 3

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 3

        neighbors = self.grid.get_neighbors((1, 3), moore=False, radius=2)
        assert len(neighbors) == 2


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
        width = 3
        height = 5
        self.grid = SingleGrid(width, height, True)
        self.agents = []
        counter = 0
        for x in range(width):
            for y in range(height):
                if TEST_GRID[x][y] == 0:
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

        assert len(self.grid.empties) == 9
        a = MockAgent(100, None)
        with self.assertRaises(Exception):
            self.grid._place_agent((0, 1), a)

        # Place the agent in an empty cell
        self.grid.position_agent(a)
        # Test whether after placing, the empty cells are reduced by 1
        assert a.pos not in self.grid.empties
        assert len(self.grid.empties) == 8
        for i in range(10):
            self.grid.move_to_empty(a)
        assert len(self.grid.empties) == 8

        # Place agents until the grid is full
        empty_cells = len(self.grid.empties)
        for i in range(empty_cells):
            a = MockAgent(101 + i, None)
            self.grid.position_agent(a)
        assert len(self.grid.empties) == 0

        a = MockAgent(110, None)
        with self.assertRaises(Exception):
            self.grid.position_agent(a)
        with self.assertRaises(Exception):
            self.move_to_empty(self.agents[0])


# Number of agents at each position for testing
# Initial agent positions for testing
#
# --- visual aid ----
#   0 0 0
#   2 0 3
#   0 5 0
#   1 1 0
#   0 0 0
# -------------------
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
        width = 3
        height = 5
        self.grid = MultiGrid(width, height, self.torus)
        self.agents = []
        counter = 0
        for x in range(width):
            for y in range(height):
                for i in range(TEST_MULTIGRID[x][y]):
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
            assert agent in self.grid[x][y]

    def test_neighbors(self):
        '''
        Test the toroidal MultiGrid neighborhood methods.
        '''

        neighborhood = self.grid.get_neighborhood((1, 1), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((1, 4), moore=True)
        assert len(neighborhood) == 8

        neighborhood = self.grid.get_neighborhood((0, 0), moore=False)
        assert len(neighborhood) == 4

        neighbors = self.grid.get_neighbors((1, 4), moore=False)
        assert len(neighbors) == 0

        neighbors = self.grid.get_neighbors((1, 4), moore=True)
        assert len(neighbors) == 5

        neighbors = self.grid.get_neighbors((1, 1), moore=False,
                                            include_center=True)
        assert len(neighbors) == 7

        neighbors = self.grid.get_neighbors((1, 3), moore=False, radius=2)
        assert len(neighbors) == 11
