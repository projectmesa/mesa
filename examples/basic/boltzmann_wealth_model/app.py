from mesa_models.experimental import JupyterViz
from boltzmann_wealth_model.model import BoltzmannWealthModel

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
    BoltzmannWealthModel, model_params, measures=["Gini"], name="Money Model"
)
