from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid3D

from .model import BoidModel


def boid_draw(agent):
    return {"Layer": 0, "Shape": "circle", "r": 2, "Filled": "true", "Color": "red"}

boid_canvas = CanvasGrid3D(boid_draw, 100, 100, 500, 500, flip_y=True)
model_params = {
    "population": 100,
    "width": 100,
    "height": 100,
    "speed": 5,
    "vision": 10,
    "separation": 2
}

server = ModularServer(BoidModel, [boid_canvas], "Boids", model_params)
