from mesa.visualization.VegaVisualization import VegaServer
from mesa.visualization.UserParam import UserSettableParameter

from model import Schelling

grid_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 250,
    "height": 250,
    "data": {"name": "agents"},
    "mark": "bar",
    "encoding": {
      "x": {"type": "nominal", "field": "x"},
      "y": {"type": "nominal", "field": "y"},
      "color": {"type": "nominal", "field": "agent_type"}
    }
}
"""

line_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
    "width": 250,
    "height": 250,
    "data": {"name": "model"},
    "mark": "line",
    "encoding": {
      "y": {"type": "quantitative", "field": "happy"},
      "x": {"type": "quantitative", "field": "step"}
    }
}
"""


model_params = {
    "height": 20,
    "width": 20,
    "density": UserSettableParameter("slider", "Agent density", 0.8, 0.1, 1.0, 0.1),
    "schedule": UserSettableParameter(
        "choice",
        "Activation",
        value="RandomActivation",
        choices=["RandomActivation", "BaseScheduler"],
    ),
}

server = VegaServer(Schelling, [grid_spec, line_spec], "Schelling", model_params, 3)
server.launch()
