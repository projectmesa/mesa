import altair as alt

from mesa.examples.basic.boltzmann_wealth_model.model import BoltzmannWealth
from mesa.mesa_logging import INFO, log_to_stderr
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

log_to_stderr(INFO)


def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color=agent.wealth,
        tooltip={"Agent ID": agent.unique_id, "Wealth": agent.wealth},
    )


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}


model = BoltzmannWealth(50, 10, 10)

# The SpaceRenderer is responsible for drawing the model's space and agents.
# It builds the visualization in layers, first drawing the grid structure,
# and then drawing the agents on top. It uses a specified backend
# (like "altair" or "matplotlib") for creating the plots.
renderer = SpaceRenderer(model, backend="altair")
# Can customize the grid appearance.
renderer.draw_structure(grid_color="black", grid_dash=[6, 2], grid_opacity=0.3)
renderer.draw_agents(
    agent_portrayal=agent_portrayal,
    cmap="viridis",
    vmin=0,
    vmax=10,
    legend_title="Wealth",
)

# Creates a line plot component from the model's "Gini" datacollector.
GiniPlot = make_plot_component("Gini")

# The SolaraViz page combines the model, renderer, and components into a web interface.
# To run the visualization, save this code as app.py and run `solara run app.py`
page = SolaraViz(
    model,
    renderer,
    components=[GiniPlot],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)
page  # noqa