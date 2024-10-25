from mesa.examples.advanced.wolf_sheep.agents import GrassPatch, Sheep, Wolf
from mesa.examples.advanced.wolf_sheep.model import WolfSheep
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_measure,
    make_space_matplotlib,
)

WOLF_COLOR = "#000000"
SHEEP_COLOR = "#648FFF"


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 25,
        "shape": "s",  # square marker
    }

    if isinstance(agent, Wolf):
        portrayal["color"] = WOLF_COLOR
        portrayal["Layer"] = 3
    elif isinstance(agent, Sheep):
        portrayal["color"] = SHEEP_COLOR
        portrayal["Layer"] = 2
    elif isinstance(agent, GrassPatch):
        if agent.fully_grown:
            portrayal["color"] = "#00FF00"
        else:
            portrayal["color"] = "#84e184"
        # portrayal["shape"] = "rect"
        # portrayal["Filled"] = "true"
        portrayal["Layer"] = 1

    return portrayal


model_params = {
    # The following line is an example to showcase StaticText.
    "grass": {
        "type": "Select",
        "value": True,
        "values": [True, False],
        "label": "grass regrowth enabled?",
    },
    "grass_regrowth_time": Slider("Grass Regrowth Time", 20, 1, 50),
    "initial_sheep": Slider("Initial Sheep Population", 100, 10, 300),
    "sheep_reproduce": Slider("Sheep Reproduction Rate", 0.04, 0.01, 1.0, 0.01),
    "initial_wolves": Slider("Initial Wolf Population", 10, 5, 100),
    "wolf_reproduce": Slider(
        "Wolf Reproduction Rate",
        0.05,
        0.01,
        1.0,
        0.01,
    ),
    "wolf_gain_from_food": Slider("Wolf Gain From Food Rate", 20, 1, 50),
    "sheep_gain_from_food": Slider("Sheep Gain From Food", 4, 1, 10),
}


space_component = make_space_matplotlib(wolf_sheep_portrayal)
lineplot_component = make_plot_measure(["Wolves", "Sheep", "Grass"])

model = WolfSheep()


page = SolaraViz(
    model,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Wolf Sheep",
)
page  # noqa
