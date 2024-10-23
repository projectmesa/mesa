from mesa.visualization import SolaraViz, Slider, make_space_matplotlib, make_plot_measure

from mesa.examples.advanced.epstein_civil_violence.agents import Citizen, Cop
from mesa.examples.advanced.epstein_civil_violence.model import EpsteinCivilViolence

COP_COLOR = "#000000"
AGENT_QUIET_COLOR = "#648FFF"
AGENT_REBEL_COLOR = "#FE6100"
JAIL_COLOR = "#808080"
JAIL_SHAPE = "rect"


def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 25,
        # "shape": "circle",
        "x": agent.cell.coordinate[0],
        "y": agent.cell.coordinate[1],
        # "filled": True,
    }

    if isinstance(agent, Citizen):
        color = AGENT_QUIET_COLOR if agent.condition == "Quiescent" else AGENT_REBEL_COLOR
        color = JAIL_COLOR if agent.jail_sentence else color
        shape = JAIL_SHAPE if agent.jail_sentence else "circle"
        portrayal["color"] = color
        portrayal["shape"] = shape
        if shape == "rect":
            portrayal["w"] = 0.9
            portrayal["h"] = 0.9
        else:
            portrayal["r"] = 0.5
            portrayal["filled"] = False
        portrayal["layer"] = 0

    elif isinstance(agent, Cop):
        portrayal["color"] = COP_COLOR
        portrayal["r"] = 0.9
        portrayal["layer"] = 1

    return portrayal


model_params = {
    "height": 40,
    "width": 40,
    "citizen_density": Slider("Initial Agent Density", 0.7, 0.0, 0.9, 0.1),
    "cop_density": Slider("Initial Cop Density", 0.04, 0.0, 0.1, 0.01),
    "citizen_vision": Slider("Citizen Vision", 7, 1, 10, 1),
    "cop_vision": Slider("Cop Vision", 7, 1, 10, 1),
    "legitimacy": Slider("Government Legitimacy", 0.82, 0.0, 1, 0.01),
    "max_jail_term": Slider("Max Jail Term", 30, 0, 50, 1),
}

space_component = make_space_matplotlib(citizen_cop_portrayal)
chart_component = make_plot_measure(["Quiescent", "Active", "Jailed"])

epstein_model = EpsteinCivilViolence()

page = SolaraViz(
    epstein_model,
    components=[
        space_component,
        chart_component],
    model_params=model_params,
    name="Epstein Civil Violence",
)
page  # noqa
