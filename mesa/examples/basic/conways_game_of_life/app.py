import os.path
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
)


from mesa.examples.basic.conways_game_of_life.model import ConwaysGameOfLife
from mesa.visualization import (
    SolaraViz,
    make_space_component,
)


def agent_portrayal(agent):
    return {"c": "white" if agent.state == 0 else "black", "marker": "s"}


model_params = {
    "width": 50,
    "height": 50,
}

# Create initial model instance
model1 = ConwaysGameOfLife(50, 50)

# Create visualization elements. The visualization elements are solara components
# that receive the model instance as a "prop" and display it in a certain way.
# Under the hood these are just classes that receive the model instance.
# You can also author your own visualization elements, which can also be functions
# that receive the model instance and return a valid solara component.
SpaceGraph = make_space_component(agent_portrayal)


# Create the SolaraViz page. This will automatically create a server and display the
# visualization elements in a web browser.
# Display it using the following command in the example directory:
# solara run app.py
# It will automatically update and display any changes made to this file
page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="Game of Life",
)
page  # noqa
