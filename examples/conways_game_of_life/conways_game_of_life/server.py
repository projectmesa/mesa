from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .portrayal import portrayCell
from .model import ConwaysGameOfLife


# Make a world that is 50x50, on a 250x250 display.
canvas_element = CanvasGrid(portrayCell, 50, 50, 250, 250)

server = ModularServer(ConwaysGameOfLife, [canvas_element], "Game of Life",
                       {"height": 50, "width": 50})
