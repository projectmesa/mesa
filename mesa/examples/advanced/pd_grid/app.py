"""
Solara-based visualization for the Spatial Prisoner's Dilemma Model.
"""

from mesa.examples.advanced.pd_grid.model import PdGrid
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def pd_agent_portrayal(agent):
    """
    Portrayal function for rendering PD agents in the visualization.
    """
    return {
        "color": "blue" if agent.move == "C" else "red",
        "marker": "s",  # square marker
        "size": 25,
    }


# Model parameters
model_params = {
    "width": Slider("Grid Width", value=50, min=10, max=100, step=1),
    "height": Slider("Grid Height", value=50, min=10, max=100, step=1),
    "activation_order": {
        "type": "Select",
        "value": "Random",
        "values": PdGrid.activation_regimes,
        "label": "Activation Regime",
    },
}


# Create grid visualization component using Altair
grid_viz = make_space_component(agent_portrayal=pd_agent_portrayal)

# Create plot for tracking cooperating agents over time
plot_component = make_plot_component("Cooperating_Agents")

# Initialize model
initial_model = PdGrid()

# Create visualization with all components
page = SolaraViz(
    model=initial_model,
    components=[grid_viz, plot_component],
    model_params=model_params,
    name="Spatial Prisoner's Dilemma",
)
page  # noqa B018
