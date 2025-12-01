"""Tests for RNG warning suppression in discrete spaces."""
import unittest
import warnings
import random
import networkx as nx
from mesa.discrete_space import OrthogonalMooreGrid, Network, VoronoiGrid

class TestNoRNGWarnings(unittest.TestCase):
    """Test case for ensuring no RNG warnings are emitted when properly seeded."""

    def test_orthogonal_grid_no_warning(self):
        """Test that OrthogonalMooreGrid with seeded RNG emits no warning."""
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            OrthogonalMooreGrid((10, 10), random=random.Random(42))
        # Filter out unrelated warnings if any
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0

    def test_network_no_warning(self):
        """Test that Network with seeded RNG emits no warning."""
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            Network(nx.Graph(), random=random.Random(42))
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0

    def test_voronoi_grid_no_warning(self):
        """Test that VoronoiGrid with seeded RNG emits no warning."""
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            VoronoiGrid([(0,0), (1,1)], random=random.Random(42))
        relevant_warnings = [w for w in record if "Random number generator" in str(w.message)]
        assert len(relevant_warnings) == 0
