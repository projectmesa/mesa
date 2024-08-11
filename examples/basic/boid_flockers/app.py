from boid_flockers.model import BoidFlockers
from mesa.visualization import SolaraViz


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

page = SolaraViz(
    model_class=BoidFlockers,
    model_params=model_params,
    measures=[],
    name="BoidFlockers",
    agent_portrayal=boid_draw,
)
page  # noqa
