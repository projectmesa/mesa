from boid_flockers.model import BoidFlockers
from mesa.visualization import SolaraViz, make_space_matplotlib


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

model = BoidFlockers(100, 100, 100, 5, 10, 2)

page = SolaraViz(
    model,
    [make_space_matplotlib(agent_portrayal=boid_draw)],
    model_params=model_params,
    name="BoidFlockers",
)
page  # noqa
