import random

from mesa.visualization.VegaVisualization import VegaServer

from .model import ConwaysGameOfLife

grid_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 300,
    "height": 300,
    "data": {"name": "agents"},
    "mark": "bar",
    "encoding": {
      "x": {"type": "nominal", "field": "x"},
      "y": {"type": "nominal", "field": "y"},
      "color": {"type": "nominal", "field": "isAlive"}
    }
}
"""

line_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 300,
    "height": 300,
    "data": {"name": "agents"},
    "mark": "bar",
    "encoding": {
      "x": {"type": "nominal", "field": "isAlive"},
      "y": {"aggregate": "count", "type": "quantitative"},
      "color": {"type": "nominal", "field": "isAlive"}
    }
}
"""

seed = random.random()

server = VegaServer(
    ConwaysGameOfLife,
    [grid_spec, line_spec],
    "Game of Life",
    {"height": 20, "width": 20, "seed": seed},
    n_simulations=2,
)
