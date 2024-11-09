from mesa.examples.basic.boltzmann_wealth_model.model import BoltzmannWealth
from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def agent_portrayal(agent):
    color = agent.wealth  # we are using a colormap to translate wealth to color
    return {"color": color}


model_params = {
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": 10,
    "height": 10,
}


def post_process(ax):
    ax.get_figure().colorbar(ax.collections[0], label="wealth", ax=ax)


# Create initial model instance
model = BoltzmannWealth(50, 10, 10)

# Create visualization elements. The visualization elements are solara components
# that receive the model instance as a "prop" and display it in a certain way.
# Under the hood these are just classes that receive the model instance.
# You can also author your own visualization elements, which can also be functions
# that receive the model instance and return a valid solara component.

SpaceGraph = make_space_component(
    agent_portrayal, cmap="viridis", vmin=0, vmax=10, post_process=post_process
)
GiniPlot = make_plot_component("Gini")

# Create the SolaraViz page. This will automatically create a server and display the
# visualization elements in a web browser.
# Display it using the following command in the example directory:
# solara run app.py
# It will automatically update and display any changes made to this file
page = SolaraViz(
    model,
    components=[SpaceGraph, GiniPlot],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)
page  # noqa


# In a notebook environment, we can also display the visualization elements directly
# SpaceGraph(model1)
# GiniPlot(model1)

# The plots will be static. If you want to pick up model steps,
# you have to make the model reactive first
# reactive_model = solara.reactive(model1)
# SpaceGraph(reactive_model)
# In a different notebook block:
# reactive_model.value.step()
