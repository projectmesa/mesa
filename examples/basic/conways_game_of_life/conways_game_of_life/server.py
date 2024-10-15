import mesa

from .model import ConwaysGameOfLife
from .portrayal import portrayCell

# Make a world that is 50x50, on a 250x250 display.
canvas_element = mesa.visualization.CanvasGrid(portrayCell, 50, 50, 250, 250)

server = mesa.visualization.ModularServer(
    ConwaysGameOfLife, [canvas_element], "Game of Life", {"height": 50, "width": 50}
)
