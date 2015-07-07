from flockers import BoidModel
from mesa.visualization.ModularVisualization import ModularServer
from SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}
boid_canvas = SimpleCanvas(boid_draw, 500, 500)
server = ModularServer(BoidModel, [boid_canvas], "Boids",
    100, 100, 100, 5, 10, 2)
server.launch()
