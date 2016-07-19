from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from game_of_life.portrayal import portrayCell
from game_of_life.model import GameOfLife


# Make a world that is 50x50, on a 250x250 display.
canvas_element = CanvasGrid(portrayCell, 50, 50, 250, 250)

server = ModularServer(GameOfLife, [canvas_element], "Game of Life",
                       50, 50)
