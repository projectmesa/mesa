import solara
from model import Schelling

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_measure,
    make_space_matplotlib,
)


def get_happy_agents(model):
    """Display a text count of how many happy agents there are."""
    return solara.Markdown(f"**Happy agents: {model.happy}**")


def agent_portrayal(agent):
    return {"color": "tab:orange" if agent.type == 0 else "tab:blue"}


model_params = {
    "density": Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": Slider("Fraction minority", 0.2, 0.0, 1.0, 0.05),
    "homophily": Slider("Homophily", 3, 0, 8, 1),
    "width": 20,
    "height": 20,
}

model1 = Schelling(20, 20, 0.8, 0.2, 3)

HappyPlot = make_plot_measure("happy")

page = SolaraViz(
    model1,
    components=[
        make_space_matplotlib(agent_portrayal),
        make_plot_measure("happy"),
        get_happy_agents,
    ],
    model_params=model_params,
)
page  # noqa
