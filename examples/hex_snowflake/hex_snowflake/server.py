from mesa.visualization.modules import CanvasHexGrid
from mesa.visualization.ModularVisualization import ModularServer

from portrayal import portrayCell
from model import HexSnowflake

width, height = 50, 50

# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasHexGrid(portrayCell, width, height, 500, 500)

server = ModularServer(
    HexSnowflake, [canvas_element], "Hex Snowflake", {"height": height, "width": width}
)
