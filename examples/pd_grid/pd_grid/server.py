from mesa.visualization.VegaVisualization import VegaServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import PdGrid

grid_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
    "width": 250,
    "height": 250,
    "data": {"name": "agents"},
    "mark": {"type": "bar"},
    "encoding": {
      "x": {"type": "nominal", "field": "x"},
      "y": {"type": "nominal", "field": "y"},
      "color": {"type": "nominal", "field": "cooperating"}
    }
}
"""

line_spec = """
{
    "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
    "width": 250,
    "height": 250,
    "data": {"name": "model"},
    "mark": {"type": "line"},
    "encoding": {
      "y": {"type": "quantitative", "field": "cooperating_agents"},
      "x": {"type": "quantitative", "field": "step"}
    }
}
"""

model_params = {
    "seed": 123,
    "height": 30,
    "width": 30,
    "schedule_type": UserSettableParameter("choice", "Scheduler type", value="Random",
                                           choices=list(PdGrid.schedule_types.keys()))
}

server = VegaServer(PdGrid, [grid_spec, line_spec], "Prisoner's Dilemma",
                       model_params, 3)
