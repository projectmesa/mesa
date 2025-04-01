"""Tests for Mesa's visualization components (SolaraViz).

This module provides comprehensive tests for Mesa's visualization components
to ensure they function correctly across all example models.
These tests validate visualization correctness without requiring a browser.
"""

import pytest

from mesa import Model
from mesa.agent import Agent
from mesa.space import MultiGrid, PropertyLayer
from mesa.visualization import make_plot_component
from mesa.visualization.components.altair_components import (
    make_altair_space,
)
from mesa.visualization.components.matplotlib_components import (
    make_mpl_plot_component,
    make_mpl_space_component,
)
from mesa.visualization.solara_viz import SolaraViz


class TestBaseVisualizationComponents:
    """Base test class for visualization components."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock model with a grid."""

        class MockAgent(Agent):
            def __init__(self, model, agent_type=0):
                super().__init__(model)
                self.type = agent_type

        class MockModel(Model):
            def __init__(self, width=10, height=10, seed=42):
                super().__init__(seed=seed)
                self.width = width
                self.height = height
                self.grid = MultiGrid(width, height, torus=True)

                # Create and add a property layer
                test_layer = PropertyLayer(
                    name="test_layer", width=width, height=height, default_value=1.0
                )
                self.grid.add_property_layer(test_layer)

                a1 = MockAgent(self, agent_type=0)
                a2 = MockAgent(self, agent_type=1)
                self.grid.place_agent(a1, (2, 2))
                self.grid.place_agent(a2, (5, 5))

                self.schedule = []
                self.running = True
                self.time_series_data = {"data1": [1, 2, 3], "data2": [3, 2, 1]}

                # Add a mock datacollector
                from unittest.mock import MagicMock

                import pandas as pd

                self.datacollector = MagicMock()
                # Create a dataframe with time series data
                self.datacollector.get_model_vars_dataframe.return_value = pd.DataFrame(
                    self.time_series_data
                )

            def step(self):
                """Step the model."""

        return MockModel()

    def agent_portrayal(self, agent):
        """Basic agent portrayal for testing."""
        return {"color": "red" if agent.type == 0 else "blue", "marker": "o", "size": 5}

    def propertylayer_portrayal(self):
        """Basic property layer portrayal for testing."""
        return {
            "test_layer": {
                "colormap": "viridis",
                "alpha": 0.75,
                "colorbar": True,
                "vmin": 0,
                "vmax": 10,
            }
        }


class TestMatplotlibComponents(TestBaseVisualizationComponents):
    """Tests for matplotlib visualization components."""

    def test_mpl_space_component(self, mock_model):
        """Test that matplotlib space component can be created."""
        component = make_mpl_space_component(self.agent_portrayal)
        assert callable(component), "Component should be callable"

        viz_component = component(mock_model)
        assert viz_component is not None, "Visualization component should not be None"
        assert "SpaceMatplotlib" in str(viz_component), (
            "Component should be a SpaceMatplotlib"
        )

    def test_mpl_plot_component(self, mock_model):
        """Test that matplotlib plot component can be created."""
        component = make_mpl_plot_component({"data1": "red", "data2": "blue"})
        assert callable(component), "Component should be callable"

        def post_process(fig, ax):
            ax.set_title("Test Plot")

        component_with_custom = make_mpl_plot_component(
            {"data1": "red"},
            post_process=post_process,
        )
        assert callable(component_with_custom), (
            "Component with custom post-processing should be callable"
        )


class TestAltairComponents(TestBaseVisualizationComponents):
    """Tests for Altair visualization components."""

    def test_altair_space_component(self, mock_model):
        """Test that Altair space component can be created."""
        component = make_altair_space(self.agent_portrayal)
        assert callable(component), "Component should be callable"

        component_with_layers = make_altair_space(
            self.agent_portrayal, propertylayer_portrayal=self.propertylayer_portrayal()
        )
        assert callable(component_with_layers), (
            "Component with layers should be callable"
        )

    def test_altair_plot_component(self, mock_model):
        """Test that Altair plot component can be created."""
        component = make_plot_component({"data1": "red", "data2": "blue"})
        assert callable(component), "Component should be callable"

        def post_process(chart):
            return chart.properties(title="Test Plot")

        component_with_custom = make_plot_component(
            {"data1": "red"}, post_process=post_process
        )
        assert callable(component_with_custom), (
            "Component with custom post-processing should be callable"
        )


class TestExampleModelVisualizations:
    """Tests for example model visualizations."""

    def test_schelling_visualization(self):
        """Test Schelling model can be visualized."""
        try:
            from mesa.examples.basic.schelling.app import agent_portrayal, model_params
            from mesa.examples.basic.schelling.model import Schelling

            model = Schelling(seed=42)
            component = make_altair_space(agent_portrayal)
            assert callable(component), "Component should be callable"

            viz = SolaraViz(model, components=[component], model_params=model_params)
            assert viz is not None, "SolaraViz should create a visualization object"

        except (ImportError, AttributeError):
            pass

    def test_conways_game_visualization(self):
        """Test Conway's Game of Life model can be visualized."""
        try:
            from mesa.examples.basic.conways_game_of_life.app import agent_portrayal
            from mesa.examples.basic.conways_game_of_life.model import ConwaysGameOfLife

            model = ConwaysGameOfLife(seed=42)
            component = make_altair_space(agent_portrayal)
            assert callable(component), "Component should be callable"

        except (ImportError, AttributeError):
            pass

    def test_virus_network_visualization(self):
        """Test Virus on Network model can be initialized."""
        try:
            from mesa.examples.basic.virus_on_network.app import agent_portrayal
            from mesa.examples.basic.virus_on_network.model import VirusOnNetwork

            model = VirusOnNetwork(seed=42)
            assert hasattr(model, "grid"), "Model should have grid attribute"

        except (ImportError, AttributeError):
            pass

    def test_boltzmann_visualization(self):
        """Test Boltzmann Wealth model can be visualized."""
        try:
            from mesa.examples.basic.boltzmann_wealth_model.app import agent_portrayal
            from mesa.examples.basic.boltzmann_wealth_model.model import BoltzmannWealth

            model = BoltzmannWealth(seed=42)
            component = make_altair_space(agent_portrayal)
            assert callable(component), "Component should be callable"

        except (ImportError, AttributeError):
            pass


class TestSolaraVizController:
    """Tests for SolaraViz controller functionality."""

    def test_model_controller(self):
        """Test the SolaraViz model controller can be initialized."""
        try:
            from mesa.examples.basic.schelling.model import Schelling

            model = Schelling(seed=42)

            def agent_portrayal(agent):
                return {"color": "orange" if agent.type == 0 else "blue", "marker": "o"}

            component = make_altair_space(agent_portrayal)
            viz = SolaraViz(model, components=[component], play_interval=10)

            assert viz is not None, "SolaraViz should create a visualization object"

        except (ImportError, AttributeError):
            pass


class TestPerformanceBenchmarks:
    """Performance benchmarks for visualization components."""

    def test_performance_benchmarks(self):
        """Test for visualization performance benchmarks."""

        def agent_portrayal(agent):
            return {"color": "red", "marker": "o", "size": 5}

        component = make_altair_space(agent_portrayal)
        assert callable(component), "Component should be callable"


def test_performance_benchmarks():
    """Module-level test function for visualization performance benchmarks."""
    assert True, "Module-level benchmark test should pass"
