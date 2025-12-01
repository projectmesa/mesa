import unittest
import pytest
import random
from mesa.discrete_space import OrthogonalMooreGrid, Network, VoronoiGrid
from mesa.model import Model

class TestNoRNGWarnings(unittest.TestCase):
    def test_orthogonal_grid_no_warning(self):
        """Test that OrthogonalMooreGrid with seeded RNG emits no warning."""
        with pytest.warns(None) as record:
            OrthogonalMooreGrid((10, 10), random=random.Random(42))
        # Filter out unrelated warnings if any
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0

    def test_network_no_warning(self):
        """Test that Network with seeded RNG emits no warning."""
        with pytest.warns(None) as record:
            Network(random=random.Random(42))
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0

    def test_voronoi_grid_no_warning(self):
        """Test that VoronoiGrid with seeded RNG emits no warning."""
        with pytest.warns(None) as record:
            VoronoiGrid([(0,0), (1,1)], random=random.Random(42))
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0
