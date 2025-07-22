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
    color = agent.wealth  # we are using a colormap to translate wealth to color
    return AgentPortrayalStyle(color=color)


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


def post_process(ax):
    ax.get_figure().colorbar(ax.collections[0], label="wealth", ax=ax)


# Create initial model instance
model = BoltzmannWealth(50, 10, 10)

# Create a renderer. The renderer is responsible for rendering the spaces that is
# drawing the grid, agents and property layers, separately or together. It can
# use different backends, such as matplotlib or altair. It is passed into the
# SolaraViz page, which will display it in a web browser.
# In this case the renderer first draws the structure of the grid,
# then draws the agents with a colormap based on their wealth on top of the grid.
# The post_process function is called after the agents are drawn, allowing for fine-tuning the
# plot (e.g., control ticks, add colorbars, etc.)
renderer = SpaceRenderer(model, backend="matplotlib")
renderer.draw_structure()
renderer.draw_agents(agent_portrayal=agent_portrayal, cmap="viridis", vmin=0, vmax=10)
renderer.post_process = post_process


# Create plot visualization elements. These elements are solara components
# that receive the model instance as a "prop" and display it in a certain way.
# Under the hood these are just classes that receive the model instance.
# You can also author your own visualization elements, which can also be functions
# that receive the model instance and return a valid solara component.
GiniPlot = make_plot_component("Gini")

# Create the SolaraViz page. This will automatically create a server and display the
# visualization elements in a web browser.
# Display it using the following command in the example directory:
# solara run app.py
# It will automatically update and display any changes made to this file
page = SolaraViz(
    model,
    renderer,
    components=[GiniPlot],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)
page  # noqa


# In a notebook environment, we can also display the visualization elements directly
# GiniPlot(model1)

# The plots will be static. If you want to pick up model steps,
# you have to make the model reactive first
# reactive_model = solara.reactive(model1)
# GiniPlot(reactive_model)
# In a different notebook block:
# reactive_model.value.step()
