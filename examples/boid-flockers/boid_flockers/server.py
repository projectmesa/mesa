from mesa.visualization.ModularVisualization import ModularServer

from .model import BoidFlockers
from .SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}


boid_canvas = SimpleCanvas(boid_draw, 500, 500)
model_params = {
    "population": 100,
    "width": 100,
    "height": 100,
    "speed": 5,
    "vision": 10,
    "separation": 2
}

server = ModularServer(BoidFlockers, [boid_canvas], "Boids", model_params)
