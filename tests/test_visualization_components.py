"""Tests for Mesa's visualization components (SolaraViz).

This module provides comprehensive tests for Mesa's visualization components
to ensure they function correctly across all example models.
These tests validate visualization correctness without requiring a browser.
"""

import ipyvuetify as v
import numpy as np
import pytest
import solara

from mesa import Model
from mesa.agent import Agent
from mesa.examples import (
    BoltzmannWealth,
    ConwaysGameOfLife,
    Schelling,
    VirusOnNetwork,
)
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
            def __init__(self, unique_id, model, agent_type=0):
                super().__init__(unique_id, model)
                self.type = agent_type

        class MockModel(Model):
            def __init__(self, width=10, height=10, seed=42):
                super().__init__(seed=seed)
                self.width = width
                self.height = height
                self.grid = MultiGrid(width, height, torus=True)

                self.grid.property_layers["test_layer"] = PropertyLayer(
                    name="test_layer", width=width, height=height, default_value=1.0
                )

                a1 = MockAgent(1, self, agent_type=0)
                a2 = MockAgent(2, self, agent_type=1)
                self.grid.place_agent(a1, (2, 2))
                self.grid.place_agent(a2, (5, 5))

                self.schedule = []
                self.running = True
                self.datacollector = None

                self.time_series_data = {"data1": [1, 2, 3], "data2": [3, 2, 1]}

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
        """Test that matplotlib space component renders correctly."""
        component = make_mpl_space_component(self.agent_portrayal)
        box, rc = solara.render(component(mock_model), handle_error=False)

        assert rc.find("div").widget is not None

        component_with_layers = make_mpl_space_component(
            self.agent_portrayal, propertylayer_portrayal=self.propertylayer_portrayal()
        )
        box, rc = solara.render(component_with_layers(mock_model), handle_error=False)
        assert rc.find("div").widget is not None

    def test_mpl_plot_component(self, mock_model):
        """Test that matplotlib plot component renders correctly."""
        component = make_mpl_plot_component({"data1": "red", "data2": "blue"})
        box, rc = solara.render(component(mock_model), handle_error=False)

        assert rc.find("div").widget is not None

        def post_process(fig, ax):
            ax.set_title("Test Plot")

        component_with_custom = make_mpl_plot_component(
            {"data1": "red"},
            x_data=lambda model: np.arange(len(model.time_series_data["data1"])),
            post_process=post_process,
        )
        box, rc = solara.render(component_with_custom(mock_model), handle_error=False)
        assert rc.find("div").widget is not None


class TestAltairComponents(TestBaseVisualizationComponents):
    """Tests for Altair visualization components."""

    def test_altair_space_component(self, mock_model):
        """Test that Altair space component renders correctly."""
        component = make_altair_space(self.agent_portrayal)
        box, rc = solara.render(component(mock_model), handle_error=False)

        assert rc.find("div").widget is not None

        component_with_layers = make_altair_space(
            self.agent_portrayal, propertylayer_portrayal=self.propertylayer_portrayal()
        )
        box, rc = solara.render(component_with_layers(mock_model), handle_error=False)
        assert rc.find("div").widget is not None

    def test_altair_plot_component(self, mock_model):
        """Test that Altair plot component renders correctly."""
        component = make_plot_component({"data1": "red", "data2": "blue"})
        box, rc = solara.render(component(mock_model), handle_error=False)

        assert rc.find("div").widget is not None

        def post_process(chart):
            chart = chart.properties(title="Test Plot")
            return chart

        component_with_custom = make_plot_component(
            {"data1": "red"}, post_process=post_process
        )
        box, rc = solara.render(component_with_custom(mock_model), handle_error=False)
        assert rc.find("div").widget is not None


class TestExampleModelVisualizations:
    """Tests for example model visualizations."""

    def test_schelling_visualization(self):
        """Test Schelling model visualization components."""
        from mesa.examples.basic.schelling.app import agent_portrayal, model_params

        model = Schelling(seed=42)
        component = make_altair_space(agent_portrayal)

        box, rc = solara.render(component(model), handle_error=False)
        assert rc.find("div").widget is not None

        viz = SolaraViz(model, components=[component], model_params=model_params)

        box, rc = solara.render(viz, handle_error=False)
        rc.find(v.Btn, children=["Step"]).assert_single()
        rc.find(v.Btn, children=["Reset"]).assert_single()

        step_button = rc.find(v.Btn, children=["Step"]).widget
        step_button.click()
        assert model.schedule.steps > 0

    def test_conways_game_visualization(self):
        """Test Conway's Game of Life model visualization components."""
        from mesa.examples.basic.conways_game_of_life.app import (
            agent_portrayal,
        )

        model = ConwaysGameOfLife(seed=42)
        component = make_altair_space(agent_portrayal)

        box, rc = solara.render(component(model), handle_error=False)
        assert rc.find("div").widget is not None

    def test_virus_network_visualization(self):
        """Test Virus on Network model visualization components."""
        from mesa.examples.basic.virus_on_network.app import (
            agent_portrayal,
        )

        model = VirusOnNetwork(seed=42)
        component = make_altair_space(agent_portrayal)

        box, rc = solara.render(component(model), handle_error=False)
        assert rc.find("div").widget is not None

    def test_boltzmann_visualization(self):
        """Test Boltzmann Wealth model visualization components."""
        from mesa.examples.basic.boltzmann_wealth_model.app import (
            agent_portrayal,
        )

        model = BoltzmannWealth(seed=42)
        component = make_altair_space(agent_portrayal)

        box, rc = solara.render(component(model), handle_error=False)
        assert rc.find("div").widget is not None

        plot_component = make_plot_component({"Gini": "blue"})
        box, rc = solara.render(plot_component(model), handle_error=False)
        assert rc.find("div").widget is not None


class TestSolaraVizController:
    """Tests for SolaraViz controller functionality."""

    def test_model_controller(self):
        """Test the model controller (step, play, pause, reset)."""
        model = Schelling(seed=42)
        initial_agents = len(model.schedule.agents)

        def agent_portrayal(agent):
            return {"color": "orange" if agent.type == 0 else "blue", "marker": "o"}

        component = make_altair_space(agent_portrayal)

        viz = SolaraViz(model, components=[component], play_interval=10)

        box, rc = solara.render(viz, handle_error=False)

        step_button = rc.find(v.Btn, children=["Step"]).widget
        step_button.click()

        assert model.schedule.steps == 1

        model.step()
        assert model.schedule.steps == 2

        reset_button = rc.find(v.Btn, children=["Reset"]).widget
        reset_button.click()

        assert model.schedule.steps == 0
        assert len(model.schedule.agents) == initial_agents

        play_button = rc.find(v.Btn, children=["Play"]).widget
        play_button.click()

        import time

        time.sleep(0.1)

        assert model.schedule.steps > 0

        pause_button = rc.find(v.Btn, children=["Pause"]).widget
        pause_button.click()

        steps_after_pause = model.schedule.steps

        time.sleep(0.1)

        assert model.schedule.steps == steps_after_pause


class TestPerformanceBenchmarks:
    """Benchmark tests for visualization performance."""

    def test_rendering_performance(self):
        """Test visualization rendering performance."""
        import time

        small_model = Schelling(width=10, height=10, seed=42)
        medium_model = Schelling(width=20, height=20, seed=42)
        large_model = Schelling(width=50, height=50, seed=42)

        def agent_portrayal(agent):
            return {"color": "orange" if agent.type == 0 else "blue", "marker": "o"}

        mpl_component = make_mpl_space_component(agent_portrayal)

        start_time = time.time()
        box, rc = solara.render(mpl_component(small_model), handle_error=False)
        small_mpl_time = time.time() - start_time

        start_time = time.time()
        box, rc = solara.render(mpl_component(medium_model), handle_error=False)
        medium_mpl_time = time.time() - start_time

        start_time = time.time()
        box, rc = solara.render(mpl_component(large_model), handle_error=False)
        large_mpl_time = time.time() - start_time

        altair_component = make_altair_space(agent_portrayal)

        start_time = time.time()
        box, rc = solara.render(altair_component(small_model), handle_error=False)
        small_altair_time = time.time() - start_time

        start_time = time.time()
        box, rc = solara.render(altair_component(medium_model), handle_error=False)
        medium_altair_time = time.time() - start_time

        start_time = time.time()
        box, rc = solara.render(altair_component(large_model), handle_error=False)
        large_altair_time = time.time() - start_time

        assert small_mpl_time <= medium_mpl_time
        assert medium_mpl_time <= large_mpl_time * 1.2

        assert small_altair_time <= medium_altair_time
        assert medium_altair_time <= large_altair_time * 1.2

        print(
            f"Matplotlib rendering times: small={small_mpl_time:.4f}s, medium={medium_mpl_time:.4f}s, large={large_mpl_time:.4f}s"
        )
        print(
            f"Altair rendering times: small={small_altair_time:.4f}s, medium={medium_altair_time:.4f}s, large={large_altair_time:.4f}s"
        )
