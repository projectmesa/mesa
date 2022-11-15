"""
Configure visualization elements and instantiate a server
"""

from .model import {{ cookiecutter.model }}, {{ cookiecutter.agent }}  # noqa

import mesa


def circle_portrayal_example(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
        "Color": "Pink",
    }
    return portrayal


canvas_element = mesa.visualization.CanvasGrid(
    circle_portrayal_example, 20, 20, 500, 500
)
chart_element = mesa.visualization.ChartModule([{"Label": "{{ cookiecutter.camel }}", "Color": "Pink"}])

model_kwargs = {"num_agents": 10, "width": 10, "height": 10}

server = mesa.visualization.ModularServer(
    {{cookiecutter.model}},
    [canvas_element, chart_element],
    "{{ cookiecutter.camel }}",
    model_kwargs,
)
