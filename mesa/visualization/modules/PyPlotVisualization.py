from mesa.visualization.ModularVisualization import VisualizationElement
import base64
import io
from typing import Callable, Any
from matplotlib.figure import figure


class PyPlotVisualizationModule(VisualizationElement):
    """Visualize pyplot image visualizations on modular server.
    """

    package_includes = []
    local_includes = ["pltviz.js"]

    def __init__(self, img_func: Callable[[Any], figure],
                 canvas_height: int = 500,
                 canvas_width: int = 500):
        """Creates a new pyplot visualization.

        Args:
            img_func (function(Any)->figure): function to return pyplot figure
            canvas_height (int): canvas height
            canvas_width (int): canvas width
        """
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.img_func = img_func
        self.time_steps = []
        new_element = "new PyPlotModule({}, {})"
        new_element = new_element.format(canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        fig = self.img_func(model)
        io_bytes = io.BytesIO()
        fig.tight_layout()
        fig.savefig(io_bytes, format='jpg')
        io_bytes.seek(0)
        jpg_data = base64.b64encode(io_bytes.read())

        return jpg_data.decode('utf-8')
