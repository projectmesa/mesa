import os.path
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
)


from mesa.examples.advanced.epstein_civil_violence.agents import (
    Citizen,
    CitizenState,
    Cop,
)
from mesa.examples.advanced.epstein_civil_violence.model import EpsteinCivilViolence
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_measure,
    make_space_matplotlib,
)

COP_COLOR = "#000000"
QUIET_COLOR = "#648FFF"
ACTIVE_COLOR = "#FE6100"
ARRESTED_COLOR = "#808080"


def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 25,
    }

    if isinstance(agent, Citizen):
        match agent.state:
            case CitizenState.ACTIVE:
                color = ACTIVE_COLOR
            case CitizenState.QUIET:
                color = QUIET_COLOR
            case CitizenState.ARRESTED:
                color = ARRESTED_COLOR
        portrayal["color"] = color
    elif isinstance(agent, Cop):
        portrayal["color"] = COP_COLOR

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
chart_component = make_plot_measure([state.name.lower() for state in CitizenState])

epstein_model = EpsteinCivilViolence()

page = SolaraViz(
    epstein_model,
    components=[space_component, chart_component],
    model_params=model_params,
    name="Epstein Civil Violence",
)
page  # noqa
