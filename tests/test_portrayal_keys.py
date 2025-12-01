import unittest

import pytest

from mesa.agent import Agent
from mesa.model import Model
from mesa.space import SingleGrid
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.mpl_space_drawing import collect_agent_data


class TestPortrayalKeys(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.grid = SingleGrid(10, 10, torus=True)
        self.agent = Agent(self.model)
        self.grid.place_agent(self.agent, (5, 5))

    def test_dict_deprecation_warning(self):
        """Test that returning a dict emits a DeprecationWarning."""

        def portrayal(agent):
            return {"size": 10, "color": "red"}

        with pytest.warns(DeprecationWarning, match="Returning a dict"):
            collect_agent_data(self.grid, portrayal)

    def test_ignored_keys_warning(self):
        """Test that returning a dict with 's' emits UserWarning about ignored keys."""

        def portrayal(agent):
            return {"s": 10, "color": "red"}

        # Should warn about deprecation AND ignored keys
        with pytest.warns(UserWarning, match="ignored: s"):
            with pytest.warns(DeprecationWarning, match="Returning a dict"):
                collect_agent_data(self.grid, portrayal)

    def test_agent_portrayal_style_no_warning(self):
        """Test that returning AgentPortrayalStyle emits no warnings."""
        import warnings

        def portrayal(agent):
            return AgentPortrayalStyle(size=10, color="red")

        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            collect_agent_data(self.grid, portrayal)
        assert len(record) == 0
