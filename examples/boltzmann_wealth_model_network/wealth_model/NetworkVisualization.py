from mesa.visualization.ModularVisualization import VisualizationElement


class NetworkElement(VisualizationElement):
    local_includes = ["wealth_model/templates/network_canvas.js",
                      "wealth_model/templates/sigma.min.js"]

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500):
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = ("new Network_Module({}, {})".
                       format(self.canvas_width, self.canvas_height))
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        return self.portrayal_method(model.G)
