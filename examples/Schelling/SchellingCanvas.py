'''
Visualize a Schelling model via a Canvas server
'''

from Schelling import SchellingModel
from mesa.visualization.CanvasServer import CanvasServer

def schelling_draw(agent):
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
    portrayal["x"] = agent.x
    portrayal["y"] = agent.y
    if agent.type == 0:
        portrayal["Color"] = "#AA0000"
    else:
        portrayal["Color"] = "#0000AA"
    return portrayal

server = CanvasServer(SchellingModel, schelling_draw, 500, 500,
        "Schelling", 10, 10, 0.8, 0.2, 3)

server.launch()