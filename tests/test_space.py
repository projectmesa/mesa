import unittest

import networkx as nx
import numpy as np
import pytest

from mesa.space import ContinuousSpace, NetworkGrid, PropertyLayer, SingleGrid
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


class TestPropertyLayer(unittest.TestCase):
    def setUp(self):
        self.layer = PropertyLayer("test_layer", 10, 10, 0)

    # Initialization Test
    def test_initialization(self):
        self.assertEqual(self.layer.name, "test_layer")
        self.assertEqual(self.layer.width, 10)
        self.assertEqual(self.layer.height, 10)
        self.assertTrue(np.array_equal(self.layer.data, np.zeros((10, 10))))

    # Set Cell Test
    def test_set_cell(self):
        self.layer.set_cell((5, 5), 1)
        self.assertEqual(self.layer.data[5, 5], 1)

    # Set Cells Tests
    def test_set_cells_no_condition(self):
        self.layer.set_cells(2)
        np.testing.assert_array_equal(self.layer.data, np.full((10, 10), 2))

    def test_set_cells_with_condition(self):
        self.layer.set_cell((5, 5), 1)

        def condition(x):
            return x == 0

        self.layer.set_cells(3, condition)
        self.assertEqual(self.layer.data[5, 5], 1)
        self.assertEqual(self.layer.data[0, 0], 3)
        # Check if the sum is correct
        self.assertEqual(np.sum(self.layer.data), 3 * 99 + 1)

    def test_set_cells_with_random_condition(self):
        # Probability for a cell to be updated
        update_probability = 0.5

        # Define a condition with a random part
        def condition(val):
            return np.random.rand() < update_probability

        # Apply set_cells
        self.layer.set_cells(True, condition)

        # Count the number of cells that were set to True
        true_count = np.sum(self.layer.data)

        width = self.layer.width
        height = self.layer.height

        # Calculate expected range (with some tolerance for randomness)
        expected_min = width * height * update_probability * 0.5
        expected_max = width * height * update_probability * 1.5

        # Check if the true_count falls within the expected range
        assert expected_min <= true_count <= expected_max

    # Modify Cell Test
    def test_modify_cell_lambda(self):
        self.layer.data = np.zeros((10, 10))
        self.layer.modify_cell((2, 2), lambda x: x + 5)
        self.assertEqual(self.layer.data[2, 2], 5)

    def test_modify_cell_ufunc(self):
        self.layer.data = np.ones((10, 10))
        self.layer.modify_cell((3, 3), np.add, 4)
        self.assertEqual(self.layer.data[3, 3], 5)

    def test_modify_cell_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.layer.modify_cell((1, 1), np.add)  # Missing value for ufunc

    # Modify Cells Test
    def test_modify_cells_lambda(self):
        self.layer.data = np.zeros((10, 10))
        self.layer.modify_cells(lambda x: x + 2)
        np.testing.assert_array_equal(self.layer.data, np.full((10, 10), 2))

    def test_modify_cells_ufunc(self):
        self.layer.data = np.ones((10, 10))
        self.layer.modify_cells(np.multiply, 3)
        np.testing.assert_array_equal(self.layer.data, np.full((10, 10), 3))

    def test_modify_cells_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.layer.modify_cells(np.add)  # Missing value for ufunc

    # Aggregate Property Test
    def test_aggregate_property_lambda(self):
        self.layer.data = np.arange(100).reshape(10, 10)
        result = self.layer.aggregate_property(lambda x: np.sum(x))
        self.assertEqual(result, np.sum(np.arange(100)))

    def test_aggregate_property_ufunc(self):
        self.layer.data = np.full((10, 10), 2)
        result = self.layer.aggregate_property(np.mean)
        self.assertEqual(result, 2)

    # Edge Case: Negative or Zero Dimensions
    def test_initialization_negative_dimensions(self):
        with self.assertRaises(ValueError):
            PropertyLayer("test_layer", -10, 10, 0)

    def test_initialization_zero_dimensions(self):
        with self.assertRaises(ValueError):
            PropertyLayer("test_layer", 0, 10, 0)

    # Edge Case: Out-of-Bounds Cell Access
    def test_set_cell_out_of_bounds(self):
        with self.assertRaises(IndexError):
            self.layer.set_cell((10, 10), 1)

    def test_modify_cell_out_of_bounds(self):
        with self.assertRaises(IndexError):
            self.layer.modify_cell((10, 10), lambda x: x + 5)

    # Edge Case: Selecting Cells with Complex Conditions
    def test_select_cells_complex_condition(self):
        self.layer.data = np.random.rand(10, 10)
        selected = self.layer.select_cells(lambda x: (x > 0.5) & (x < 0.75))
        for c in selected:
            self.assertTrue(0.5 < self.layer.data[c] < 0.75)

    # More edge cases
    def test_set_cells_with_numpy_ufunc(self):
        # Set some cells to a specific value
        self.layer.data[0:5, 0:5] = 5

        # Use a numpy ufunc as a condition. Here, we're using `np.greater`
        # which will return True for cells with values greater than 2.
        condition = np.greater
        self.layer.set_cells(10, lambda x: condition(x, 2))

        # Check if cells that had value greater than 2 are now set to 10
        updated_cells = self.layer.data[0:5, 0:5]
        np.testing.assert_array_equal(updated_cells, np.full((5, 5), 10))

        # Check if cells that had value 0 (less than or equal to 2) remain unchanged
        unchanged_cells = self.layer.data[5:, 5:]
        np.testing.assert_array_equal(unchanged_cells, np.zeros((5, 5)))

    def test_modify_cell_boundary_condition(self):
        self.layer.data = np.zeros((10, 10))
        self.layer.modify_cell((0, 0), lambda x: x + 5)
        self.layer.modify_cell((9, 9), lambda x: x + 5)
        self.assertEqual(self.layer.data[0, 0], 5)
        self.assertEqual(self.layer.data[9, 9], 5)

    def test_aggregate_property_std_dev(self):
        self.layer.data = np.arange(100).reshape(10, 10)
        result = self.layer.aggregate_property(np.std)
        self.assertAlmostEqual(result, np.std(np.arange(100)), places=5)

    def test_data_type_consistency(self):
        self.layer.data = np.zeros((10, 10), dtype=int)
        self.layer.set_cell((5, 5), 5.5)
        self.assertIsInstance(self.layer.data[5, 5], self.layer.data.dtype.type)


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
            for i, pos in enumerate(list(self.space.empties)):
                a = MockAgent(-i, pos)
                self.space.place_agent(a, pos)
        with self.assertRaises(Exception):
            self.space.move_to_empty(a)

    def test_empty_mask_consistency(self):
        # Check that the empty mask is consistent with the empties set
        empty_mask = self.space.empty_mask
        empties = self.space.empties
        for i in range(self.space.width):
            for j in range(self.space.height):
                mask_value = empty_mask[i, j]
                empties_value = (i, j) in empties
                assert mask_value == empties_value

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

    def test_move_agent_random_selection(self):
        agent = self.agents[0]
        possible_positions = [(10, 10), (20, 20), (30, 30)]
        self.space.move_agent_to_one_of(agent, possible_positions, selection="random")
        assert agent.pos in possible_positions

    def test_move_agent_closest_selection(self):
        agent = self.agents[0]
        agent.pos = (5, 5)
        possible_positions = [(6, 6), (10, 10), (20, 20)]
        self.space.move_agent_to_one_of(agent, possible_positions, selection="closest")
        assert agent.pos == (6, 6)

    def test_move_agent_invalid_selection(self):
        agent = self.agents[0]
        possible_positions = [(10, 10), (20, 20), (30, 30)]
        with self.assertRaises(ValueError):
            self.space.move_agent_to_one_of(
                agent, possible_positions, selection="invalid_option"
            )

    def test_distance_squared(self):
        pos1 = (3, 4)
        pos2 = (0, 0)
        expected_distance_squared = 3**2 + 4**2
        assert self.space._distance_squared(pos1, pos2) == expected_distance_squared

    def test_iter_cell_list_contents(self):
        """
        Test neighborhood retrieval
        """
        cell_list_1 = list(self.space.iter_cell_list_contents(TEST_AGENTS_GRID[0]))
        assert len(cell_list_1) == 1

        cell_list_2 = list(
            self.space.iter_cell_list_contents(
                (TEST_AGENTS_GRID[0], TEST_AGENTS_GRID[1])
            )
        )
        assert len(cell_list_2) == 2

        cell_list_3 = list(self.space.iter_cell_list_contents(tuple(TEST_AGENTS_GRID)))
        assert len(cell_list_3) == 3

        cell_list_4 = list(
            self.space.iter_cell_list_contents((TEST_AGENTS_GRID[0], (0, 0)))
        )
        assert len(cell_list_4) == 1


class TestSingleGridTorus(unittest.TestCase):
    def setUp(self):
        self.space = SingleGrid(50, 50, True)  # Torus is True here
        self.agents = []
        for i, pos in enumerate(TEST_AGENTS_GRID):
            a = MockAgent(i, None)
            self.agents.append(a)
            self.space.place_agent(a, pos)

    def test_move_agent_random_selection(self):
        agent = self.agents[0]
        possible_positions = [(49, 49), (1, 1), (25, 25)]
        self.space.move_agent_to_one_of(agent, possible_positions, selection="random")
        assert agent.pos in possible_positions

    def test_move_agent_closest_selection(self):
        agent = self.agents[0]
        agent.pos = (0, 0)
        possible_positions = [(3, 3), (49, 49), (25, 25)]
        self.space.move_agent_to_one_of(agent, possible_positions, selection="closest")
        # Expecting (49, 49) to be the closest in a torus grid
        assert agent.pos == (49, 49)

    def test_move_agent_invalid_selection(self):
        agent = self.agents[0]
        possible_positions = [(10, 10), (20, 20), (30, 30)]
        with self.assertRaises(ValueError):
            self.space.move_agent_to_one_of(
                agent, possible_positions, selection="invalid_option"
            )

    def test_move_agent_empty_list(self):
        agent = self.agents[0]
        possible_positions = []
        agent.pos = (3, 3)
        self.space.move_agent_to_one_of(agent, possible_positions, selection="random")
        assert agent.pos == (3, 3)

    def test_move_agent_empty_list_warning(self):
        agent = self.agents[0]
        possible_positions = []
        # Should assert RuntimeWarning
        with self.assertWarns(RuntimeWarning):
            self.space.move_agent_to_one_of(
                agent, possible_positions, selection="random", handle_empty="warning"
            )

    def test_move_agent_empty_list_error(self):
        agent = self.agents[0]
        possible_positions = []
        with self.assertRaises(ValueError):
            self.space.move_agent_to_one_of(
                agent, possible_positions, selection="random", handle_empty="error"
            )

    def test_distance_squared_torus(self):
        pos1 = (0, 0)
        pos2 = (49, 49)
        expected_distance_squared = 1**2 + 1**2  # In torus, these points are close
        assert self.space._distance_squared(pos1, pos2) == expected_distance_squared


class TestSingleGridWithPropertyGrid(unittest.TestCase):
    def setUp(self):
        self.grid = SingleGrid(10, 10, False)
        self.property_layer1 = PropertyLayer("layer1", 10, 10, 0)
        self.property_layer2 = PropertyLayer("layer2", 10, 10, 1)
        self.grid.add_property_layer(self.property_layer1)
        self.grid.add_property_layer(self.property_layer2)

    # Test adding and removing property layers
    def test_add_property_layer(self):
        self.assertIn("layer1", self.grid.properties)
        self.assertIn("layer2", self.grid.properties)

    def test_remove_property_layer(self):
        self.grid.remove_property_layer("layer1")
        self.assertNotIn("layer1", self.grid.properties)

    def test_add_property_layer_mismatched_dimensions(self):
        with self.assertRaises(ValueError):
            self.grid.add_property_layer(PropertyLayer("layer3", 5, 5, 0))

    def test_add_existing_property_layer(self):
        with self.assertRaises(ValueError):
            self.grid.add_property_layer(self.property_layer1)

    def test_remove_nonexistent_property_layer(self):
        with self.assertRaises(ValueError):
            self.grid.remove_property_layer("nonexistent_layer")

    # Test getting masks
    def test_get_empty_mask(self):
        empty_mask = self.grid.empty_mask
        self.assertTrue(np.all(empty_mask == np.ones((10, 10), dtype=bool)))

    def test_get_empty_mask_with_agent(self):
        agent = MockAgent(0, self.grid)
        self.grid.place_agent(agent, (4, 6))

        empty_mask = self.grid.empty_mask
        expected_mask = np.ones((10, 10), dtype=bool)
        expected_mask[4, 6] = False

        self.assertTrue(np.all(empty_mask == expected_mask))

    def test_get_neighborhood_mask(self):
        agent = MockAgent(0, self.grid)
        agent2 = MockAgent(1, self.grid)
        self.grid.place_agent(agent, (5, 5))
        self.grid.place_agent(agent2, (5, 6))
        neighborhood_mask = self.grid.get_neighborhood_mask((5, 5), True, False, 1)
        expected_mask = np.zeros((10, 10), dtype=bool)
        expected_mask[4:7, 4:7] = True
        expected_mask[5, 5] = False
        self.assertTrue(np.all(neighborhood_mask == expected_mask))

    # Test selecting and moving to cells based on multiple conditions
    def test_select_cells_by_properties(self):
        def condition(x):
            return x == 0

        selected_cells = self.grid.select_cells({"layer1": condition})
        self.assertEqual(len(selected_cells), 100)

    def test_select_cells_by_properties_return_mask(self):
        def condition(x):
            return x == 0

        selected_mask = self.grid.select_cells({"layer1": condition}, return_list=False)
        self.assertTrue(isinstance(selected_mask, np.ndarray))
        self.assertTrue(selected_mask.all())

    def test_move_agent_to_cell_by_properties(self):
        agent = MockAgent(1, self.grid)
        self.grid.place_agent(agent, (5, 5))
        conditions = {"layer1": lambda x: x == 0}
        target_cells = self.grid.select_cells(conditions)
        self.grid.move_agent_to_one_of(agent, target_cells)
        # Agent should move, since none of the cells match the condition
        self.assertNotEqual(agent.pos, (5, 5))

    def test_move_agent_no_eligible_cells(self):
        agent = MockAgent(3, self.grid)
        self.grid.place_agent(agent, (5, 5))
        conditions = {"layer1": lambda x: x != 0}
        target_cells = self.grid.select_cells(conditions)
        self.grid.move_agent_to_one_of(agent, target_cells)
        self.assertEqual(agent.pos, (5, 5))

    # Test selecting and moving to cells based on extreme values
    def test_select_extreme_value_cells(self):
        self.grid.properties["layer2"].set_cell((3, 1), 1.1)
        target_cells = self.grid.select_cells(extreme_values={"layer2": "highest"})
        self.assertIn((3, 1), target_cells)

    def test_select_extreme_value_cells_return_mask(self):
        self.grid.properties["layer2"].set_cell((3, 1), 1.1)
        target_mask = self.grid.select_cells(
            extreme_values={"layer2": "highest"}, return_list=False
        )
        self.assertTrue(isinstance(target_mask, np.ndarray))
        self.assertTrue(target_mask[3, 1])

    def test_move_agent_to_extreme_value_cell(self):
        agent = MockAgent(2, self.grid)
        self.grid.place_agent(agent, (5, 5))
        self.grid.properties["layer2"].set_cell((3, 1), 1.1)
        target_cells = self.grid.select_cells(extreme_values={"layer2": "highest"})
        self.grid.move_agent_to_one_of(agent, target_cells)
        self.assertEqual(agent.pos, (3, 1))

    # Test using masks
    def test_select_cells_by_properties_with_empty_mask(self):
        self.grid.place_agent(
            MockAgent(0, self.grid), (5, 5)
        )  # Placing an agent to ensure some cells are not empty
        empty_mask = self.grid.empty_mask

        def condition(x):
            return x == 0

        selected_cells = self.grid.select_cells({"layer1": condition}, masks=empty_mask)
        self.assertNotIn(
            (5, 5), selected_cells
        )  # (5, 5) should not be in the selection as it's not empty

    def test_select_cells_by_properties_with_neighborhood_mask(self):
        neighborhood_mask = self.grid.get_neighborhood_mask((5, 5), True, False, 1)

        def condition(x):
            return x == 0

        selected_cells = self.grid.select_cells(
            {"layer1": condition}, masks=neighborhood_mask
        )
        expected_selection = [
            (4, 4),
            (4, 5),
            (4, 6),
            (5, 4),
            (5, 6),
            (6, 4),
            (6, 5),
            (6, 6),
        ]  # Cells in the neighborhood of (5, 5)
        self.assertCountEqual(selected_cells, expected_selection)

    def test_move_agent_to_cell_by_properties_with_empty_mask(self):
        agent = MockAgent(1, self.grid)
        self.grid.place_agent(agent, (5, 5))
        self.grid.place_agent(
            MockAgent(2, self.grid), (4, 5)
        )  # Placing another agent to create a non-empty cell
        empty_mask = self.grid.empty_mask
        conditions = {"layer1": lambda x: x == 0}
        target_cells = self.grid.select_cells(conditions, masks=empty_mask)
        self.grid.move_agent_to_one_of(agent, target_cells)
        self.assertNotEqual(
            agent.pos, (4, 5)
        )  # Agent should not move to (4, 5) as it's not empty

    def test_move_agent_to_cell_by_properties_with_neighborhood_mask(self):
        agent = MockAgent(1, self.grid)
        self.grid.place_agent(agent, (5, 5))
        neighborhood_mask = self.grid.get_neighborhood_mask((5, 5), True, False, 1)
        conditions = {"layer1": lambda x: x == 0}
        target_cells = self.grid.select_cells(conditions, masks=neighborhood_mask)
        self.grid.move_agent_to_one_of(agent, target_cells)
        self.assertIn(
            agent.pos, [(4, 4), (4, 5), (4, 6), (5, 4), (5, 6), (6, 4), (6, 5), (6, 6)]
        )  # Agent should move within the neighborhood

    # Test invalid inputs
    def test_invalid_property_name_in_conditions(self):
        def condition(x):
            return x == 0

        with self.assertRaises(KeyError):
            self.grid.select_cells(conditions={"nonexistent_layer": condition})

    # Test if coordinates means the same between the grid and the property layer
    def test_property_layer_coordinates(self):
        agent = MockAgent(0, self.grid)
        correct_pos = (1, 8)
        incorrect_pos = (8, 1)
        self.grid.place_agent(agent, correct_pos)

        # Simple check on layer 1: set by agent, check by layer
        self.grid.properties["layer1"].set_cell(agent.pos, 2)
        self.assertEqual(self.grid.properties["layer1"].data[agent.pos], 2)

        # More complicated check on layer 2: set by layer, check by agent
        self.grid.properties["layer2"].set_cell(correct_pos, 3)
        self.grid.properties["layer2"].set_cell(incorrect_pos, 4)

        correct_grid_value = self.grid.properties["layer2"].data[correct_pos]
        incorrect_grid_value = self.grid.properties["layer2"].data[incorrect_pos]
        agent_grid_value = self.grid.properties["layer2"].data[agent.pos]

        self.assertEqual(correct_grid_value, agent_grid_value)
        self.assertNotEqual(incorrect_grid_value, agent_grid_value)

    # Test selecting cells with only_empty parameter
    def test_select_cells_only_empty(self):
        self.grid.place_agent(MockAgent(0, self.grid), (5, 5))  # Occupying a cell
        selected_cells = self.grid.select_cells(only_empty=True)
        self.assertNotIn(
            (5, 5), selected_cells
        )  # The occupied cell should not be selected

    def test_select_cells_only_empty_with_conditions(self):
        self.grid.place_agent(MockAgent(1, self.grid), (5, 5))
        self.grid.properties["layer1"].set_cell((5, 5), 2)
        self.grid.properties["layer1"].set_cell((6, 6), 2)

        def condition(x):
            return x == 2

        selected_cells = self.grid.select_cells({"layer1": condition}, only_empty=True)
        self.assertIn((6, 6), selected_cells)
        self.assertNotIn((5, 5), selected_cells)

    # Test selecting cells with multiple extreme values
    def test_select_cells_multiple_extreme_values(self):
        self.grid.properties["layer1"].set_cell((1, 1), 3)
        self.grid.properties["layer1"].set_cell((2, 2), 3)
        self.grid.properties["layer2"].set_cell((2, 2), 0.5)
        self.grid.properties["layer2"].set_cell((3, 3), 0.5)
        selected_cells = self.grid.select_cells(
            extreme_values={"layer1": "highest", "layer2": "lowest"}
        )
        self.assertIn((2, 2), selected_cells)
        self.assertNotIn((1, 1), selected_cells)
        self.assertNotIn((3, 3), selected_cells)
        self.assertEqual(len(selected_cells), 1)


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
        assert len(self.space.get_neighborhood(0, include_center=True)) == 3
        assert len(self.space.get_neighborhood(0, include_center=False)) == 2
        assert len(self.space.get_neighborhood(2, include_center=True, radius=3)) == 7
        assert len(self.space.get_neighborhood(2, include_center=False, radius=3)) == 6

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
            len(self.space.get_neighborhood(0, include_center=True))
            == TestMultipleNetworkGrid.GRAPH_SIZE
        )
        assert (
            len(self.space.get_neighborhood(0, include_center=False))
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
