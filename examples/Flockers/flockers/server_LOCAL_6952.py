from flockers import BoidModel
from mesa.visualization.ModularVisualization import ModularServer
from SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}
boid_canvas = SimpleCanvas(boid_draw, 500, 500)

model_params = dict(N=100, width=100, height=100, speed=5,
                    vision=10, separation=2)
server = ModularServer(BoidModel, [boid_canvas], "Boids", model_params)
server.launch()
