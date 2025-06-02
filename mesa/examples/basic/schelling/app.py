import solara

from mesa.examples.basic.schelling.model import Schelling
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from mesa.visualization.components import AgentPortrayalStyle


def get_happy_agents(model):
    """Display a text count of how many happy agents there are."""
    return solara.Markdown(f"**Happy agents: {model.happy}**")


def agent_portrayal(agent):
    style = AgentPortrayalStyle(
        x=agent.cell.coordinate[0],
        y=agent.cell.coordinate[1],
        marker="./resources/orange_happy.png",
        size=75,
    )
    if agent.type == 0:
        if agent.happy:
            style.update(
                ("marker", "./resources/blue_happy.png"),
            )
        else:
            style.update(
                ("marker", "./resources/blue_unhappy.png"),
                ("size", 50),
                ("zorder", 2),
            )
    else:
        if not agent.happy:
            style.update(
                ("marker", "./resources/orange_unhappy.png"),
                ("size", 50),
                ("zorder", 2),
            )

    return style


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "density": Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": Slider("Fraction minority", 0.2, 0.0, 1.0, 0.05),
    "homophily": Slider("Homophily", 0.4, 0.0, 1.0, 0.125),
    "width": 20,
    "height": 20,
}

model1 = Schelling()

HappyPlot = make_plot_component({"happy": "tab:green"})

page = SolaraViz(
    model1,
    components=[
        make_space_component(agent_portrayal),
        HappyPlot,
        get_happy_agents,
    ],
    model_params=model_params,
)
page  # noqa
