"""
Network Visualization Module
============

Module for rendering the network, using [d3.js](https://d3js.org/) framework.
"""
from mesa.visualization.ModularVisualization import D3_JS_FILE, VisualizationElement


class NetworkModule(VisualizationElement):
    package_includes = []

    def __init__(
        self,
        portrayal_method,
        canvas_height=500,
        canvas_width=500,
    ):
        NetworkModule.package_includes = ["NetworkModule_d3.js", D3_JS_FILE]

        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = f"new NetworkModule({self.canvas_width}, {self.canvas_height})"
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        return self.portrayal_method(model.G)
