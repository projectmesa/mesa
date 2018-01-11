"""
Test the model random method.
"""

from unittest import TestCase
from mesa import Model


class MockModel(Model):
    """Mock model to test random method."""

    def __init__(self, seed=None):
        """
        Create a Model instance with a default seed.

        Args:
            seed (int): initializing the model with a fixed seed.
                            This will help to replicate results
        """
        # Initilize the super class.
        super().__init__(seed=seed)


class TestModelRandomShuffle(TestCase):
    """Test the model random shuffle."""

    def test_model_shuffle(self):
        mock_model = MockModel(seed=123)
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        mock_model.random.shuffle(test_list)
        self.assertEqual(test_list, [8, 1, 6, 7, 4, 2, 9, 5, 3])
