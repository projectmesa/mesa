from boid_flockers.model import BoidFlockers
from mesa.experimental import JupyterViz


def boid_draw(agent):
    return {"color": "tab:red"}


model_params = {
    "population": 100,
    "width": 100,
    "height": 100,
    "speed": 5,
    "vision": 10,
    "separation": 2,
}

page = JupyterViz(
    BoidFlockers,
    model_params,
    measures=[],
    name="BoidFlockers",
    agent_portrayal=boid_draw,
)
page  # noqa
