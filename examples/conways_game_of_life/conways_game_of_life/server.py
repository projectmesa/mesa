from mesa.visualization.modules import VegaModule
from mesa.visualization.ModularVisualization import ModularServer

from .model import ConwaysGameOfLife

spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 500,
    "height": 500,
    "data": {"name": "model"},
    "mark": "bar",
    "encoding": {
      "x": {"type": "nominal", "field": "x"},
      "y": {"type": "nominal", "field": "y"},
      "color": {"type": "nominal", "field": "isAlive"}
    }
}
"""

canvas_element = VegaModule(spec, agent_attributes=["x", "y", "isAlive"])

server = ModularServer(ConwaysGameOfLife, [canvas_element], "Game of Life",
                       {"height": 50, "width": 50})
