from mesa.visualization.VegaVisualization import VegaServer
from mesa.visualization.UserParam import UserSettableParameter


from .model import ConwaysGameOfLife

grid_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 500,
    "height": 500,
    "data": {"name": "agents"},
    "mark": "bar",
    "encoding": {
      "x": {"type": "nominal", "field": "x"},
      "y": {"type": "nominal", "field": "y"},
      "color": {"type": "nominal", "field": "isAlive"}
    }
}
"""

server = VegaServer(
    ConwaysGameOfLife,
    [grid_spec],
    "Game of Life",
    {
        "size": UserSettableParameter(
            "slider", "Size", value=50, min_value=10, max_value=100, step=5
        )
    },
    n_simulations=1,
)
