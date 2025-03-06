import os

import pandas as pd

import mesa


class WarehouseModel(mesa.Model):
    """
    Model for simulating multi-level alliances among agents.
    """

    def __init__(self, seed=42):
        """
        Initialize the model.

        Args:
            seed (int): Random seed.
        """
        super().__init__(seed=42)
        self.map = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "warehouse_layout.csv"), header=None
        ).values

        print(self.map)
