import mesa

from hex_snowflake.portrayal import portrayCell
from hex_snowflake.model import HexSnowflake

width, height = 50, 50

# Make a world that is 50x50, on a 500x500 display.
canvas_element = mesa.visualization.CanvasHexGrid(portrayCell, width, height, 500, 500)

server = mesa.visualization.ModularServer(
    HexSnowflake, [canvas_element], "Hex Snowflake", {"height": height, "width": width}
)
