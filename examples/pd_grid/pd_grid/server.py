from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from .portrayal import portrayPDAgent
from .model import PDModel


# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasGrid(portrayPDAgent, 50, 50, 500, 500)

server = ModularServer(PDModel, [canvas_element], "Prisoner's Dilemma", 50, 50,
                       'Random')
