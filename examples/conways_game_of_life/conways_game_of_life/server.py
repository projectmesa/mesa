from .VegaModule import VegaGrid
from mesa.visualization.ModularVisualization import ModularServer

from .model import ConwaysGameOfLife


# Make a world that is 50x50, on a 250x250 display.
vega_grid = VegaGrid()

server = ModularServer(ConwaysGameOfLife, [vega_grid], "Game of Life",
                       {"height": 50, "width": 50})
