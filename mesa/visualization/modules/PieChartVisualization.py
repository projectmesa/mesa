"""
Pie Chart Module
============

Module for drawing live-updating pie charts using d3.js
"""
import json
from mesa.visualization.ModularVisualization import VisualizationElement, D3_JS_FILE


class PieChartModule(VisualizationElement):
    """Each chart can visualize one set of fields from a datacollector as a
    pie chart.

    Attributes:
        fields: A list of dictionaries containing information on fields to
                plot. Each dictionary must contain (at least) the "Label" and
                "Color" keys. The "Label" value must correspond to a
                model-level field collected by the model's DataCollector, and
                "Color" must have a valid HTML color.
        canvas_height, canvas_width: The width and height to draw the chart on
                                     the page, in pixels. Default to 500 x 500
        data_collector_name: Name of the DataCollector object in the model to
                             retrieve data from.
    """

    package_includes = [D3_JS_FILE, "PieChartModule.js"]

    def __init__(
        self,
        fields,
        canvas_height=500,
        canvas_width=500,
        data_collector_name="datacollector",
    ):
        """
        Create a new line chart visualization.

        Args:
            fields: A list of dictionaries containing fields names and
                    HTML colors to chart them in, e.g.
                    [{"Label": "happy", "Color": "Black"},]
            canvas_height, canvas_width: Size in pixels of the chart to draw.
            data_collector_name: Name of the DataCollector to use.
        """

        self.fields = fields
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.data_collector_name = data_collector_name

        fields_json = json.dumps(self.fields)
        new_element = "new PieChartModule({}, {}, {})"
        new_element = new_element.format(fields_json, canvas_width, canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        for s in self.fields:
            name = s["Label"]
            try:
                val = data_collector.model_vars[name][-1]  # Latest value
            except (IndexError, KeyError):
                val = 0
            current_values.append(val)
        return current_values
