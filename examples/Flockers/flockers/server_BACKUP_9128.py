from mesa.visualization.ModularVisualization import ModularServer

from .model import BoidModel
from .SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}

boid_canvas = SimpleCanvas(boid_draw, 500, 500)
<<<<<<< HEAD:examples/Flockers/Flocker_Server.py

model_params = dict(N=100, width=100, height=100, speed=5,
                    vision=10, separation=2)
server = ModularServer(BoidModel, [boid_canvas], "Boids", model_params)
server.launch()
=======
server = ModularServer(BoidModel, [boid_canvas], "Boids",
                       100, 100, 100, 5, 10, 2)
>>>>>>> refs/remotes/projectmesa/master:examples/Flockers/flockers/server.py
