"""Tests for RNG determinism in discrete spaces."""
import random
import unittest

from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.model import Model


class TestSpacesRNG(unittest.TestCase):
    """Test case for OrthogonalMooreGrid RNG behavior."""
    def test_orthogonal_grid_determinism(self):
        """Test that OrthogonalMooreGrid behaves deterministically with a seeded RNG."""
        seed = 42

        # Run 1
        rng1 = random.Random(seed)
        grid1 = OrthogonalMooreGrid((10, 10), random=rng1)
        model1 = Model()
        agents1 = [CellAgent(model1) for _ in range(5)]
        positions1 = []
        for agent in agents1:
            agent.cell = grid1.select_random_empty_cell()
            positions1.append(agent.cell.coordinate)

        # Run 2
        rng2 = random.Random(seed)
        grid2 = OrthogonalMooreGrid((10, 10), random=rng2)
        model2 = Model()
        agents2 = [CellAgent(model2) for _ in range(5)]
        positions2 = []
        for agent in agents2:
            agent.cell = grid2.select_random_empty_cell()
            positions2.append(agent.cell.coordinate)

        self.assertEqual(positions1, positions2)

    def test_orthogonal_grid_randomness(self):
        """Test that OrthogonalMooreGrid behaves differently with different seeds."""
        # Run 1
        rng1 = random.Random(42)
        grid1 = OrthogonalMooreGrid((10, 10), random=rng1)
        model1 = Model()
        agents1 = [CellAgent(model1) for _ in range(5)]
        positions1 = []
        for agent in agents1:
            agent.cell = grid1.select_random_empty_cell()
            positions1.append(agent.cell.coordinate)

        # Run 2
        rng2 = random.Random(43)
        grid2 = OrthogonalMooreGrid((10, 10), random=rng2)
        model2 = Model()
        agents2 = [CellAgent(model2) for _ in range(5)]
        positions2 = []
        for agent in agents2:
            agent.cell = grid2.select_random_empty_cell()
            positions2.append(agent.cell.coordinate)

        self.assertNotEqual(positions1, positions2)
