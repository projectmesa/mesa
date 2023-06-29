from mesa_models.experimental import JupyterViz

from model import BoltzmannWealthModel


def agent_portrayal(agent):
    if agent.wealth > 0:
        return 50
    return 10


model_params = {
    "N": {
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

page = JupyterViz(
    BoltzmannWealthModel,
    model_params,
    measures=["Gini"],
    name="Money Model",
    agent_portrayal=agent_portrayal,
)
page
