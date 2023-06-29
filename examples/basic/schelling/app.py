from mesa_models.experimental import JupyterViz
from model import Schelling


def get_happy_agents(model):
    """
    Display a text count of how many happy agents there are.
    """
    return f"Happy agents: {model.happy}"


def agent_portrayal(agent):
    color = "tab:orange" if agent.type == 0 else "tab:blue"
    return {"color": color}


model_params = {
    "density": {
        "type": "SliderFloat",
        "value": 0.8,
        "label": "Agent density",
        "min": 0.1,
        "max": 1.0,
        "step": 0.1,
    },
    "minority_pc": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Fraction minority",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
    },
    "homophily": {
        "type": "SliderInt",
        "value": 3,
        "label": "Homophily",
        "min": 0,
        "max": 8,
        "step": 1,
    },
    "width": 20,
    "height": 20,
}

page = JupyterViz(
    Schelling,
    model_params,
    measures=["happy", get_happy_agents],
    name="Schelling",
    agent_portrayal=agent_portrayal,
)
page  # noqa
