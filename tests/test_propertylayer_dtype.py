import unittest
import numpy as np
import pytest
from mesa.discrete_space import PropertyLayer

class TestPropertyLayerDtype(unittest.TestCase):
    def test_dtype_match_no_warning(self):
        """Test that matching default_value and dtype emits no warning."""
        with pytest.warns(None) as record:
            PropertyLayer("test", (10, 10), default_value=np.float64(0.0), dtype=np.float64)
        assert len(record) == 0

    def test_dtype_mismatch_warning(self):
        """Test that mismatching default_value and dtype emits a UserWarning."""
        with pytest.warns(UserWarning, match="might not be best suitable"):
            PropertyLayer("test", (10, 10), default_value=0, dtype=np.float64)

    def test_float_vs_float64_warning(self):
        """Test that Python float vs np.float64 emits warning (strict check)."""
        # This confirms the behavior we observed and fixed
        with pytest.warns(UserWarning, match="might not be best suitable"):
            PropertyLayer("test", (10, 10), default_value=0.0, dtype=np.float64)
