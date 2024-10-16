import mesa
from mesa.visualization import SolaraViz
from mesa.visualization.UserParam import Slider
# Import make_space_altair
from mesa.visualization import make_space_altair, make_plot_measure

from model import PdGrid

def portray_pd_agent(agent):
    """This function is called to portray each agent in the visualization."""
    if agent is None:
        return {}
    return {
        "shape": "rect",
        "w": 1,
        "h": 1,
        "color": "blue" if agent.isCooroperating else "red",
    }

# Define model parameters
model_params = {
    "height": Slider("Grid Height", 50, 10, 100, 1),
    "width": Slider("Grid Width", 50, 10, 100, 1),
    # TODO: Implement Choice in UserParam. See https://github.com/projectmesa/mesa/issues/2376
    # "activation_order": Choice(
    #     "Activation regime",
    #     value="Random",
    #     choices=PdGrid.activation_regimes,
    # ),
}

# Create the model instance
pd_model = PdGrid()

coop_plot = make_plot_measure("cooperating_agents")

# Create the SolaraViz instance
page = SolaraViz(
    pd_model,
    # TODO: Support the Cell Space in SolaraViz.
    components=[coop_plot],  # [make_space_altair(portray_pd_agent)],
    model_params=model_params,
    name="Prisoner's Dilemma"
)
page  # noqa
