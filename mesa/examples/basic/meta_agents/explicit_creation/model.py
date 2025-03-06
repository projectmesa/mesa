import networkx as nx
import numpy as np
import pandas as pd
import os

import mesa
import mesa.examples.basic.meta_agents.explicit_creation.agents as agents
from mesa.experimental.meta_agents.meta_agent import MetaAgent


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
        self.map = pd.read_csv(os.path.join(os.path.dirname(__file__), "warehouse_layout.csv"),
                                header=None).values

        print(self.map)
