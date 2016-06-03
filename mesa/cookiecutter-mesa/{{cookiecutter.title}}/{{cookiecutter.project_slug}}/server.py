"""
Configure visualization elements and instantiate a server
"""

from .model import {{ cookiecutter.model }}, {{ cookiecutter.agent }}

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule


def circle_portrayal_example(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 1}
    return portrayal

canvas_element = CanvasGrid(circle_portrayal_example, 20, 20, 500, 500)
chart_element = ChartModule([{"Label": "{{ cookiecutter.title }}", "Color": "#AA0000"}])

model_kwargs = {"num_agents": 10,
                "width": 10,
                "height": 10}

server = ModularServer({{ cookiecutter.model }}, [canvas_element, chart_element],
                       "{{ cookiecutter.title }}", **model_kwargs)
