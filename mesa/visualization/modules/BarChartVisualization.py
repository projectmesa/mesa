"""
Pie Chart Module
============

Module for drawing live-updating bar charts using d3.js
"""
import json

from mesa.visualization.ModularVisualization import D3_JS_FILE, VisualizationElement


class BarChartModule(VisualizationElement):
    """Each bar chart can either visualize model-level or agent-level fields from a datcollector
        with a bar chart.

    Attributes:
        scope: whether to visualize agent-level or model-level fields
        fields: A List of Dictionaries containing information about each field to be charted,
                including the name of the datacollector field and the desired color of the
                corresponding bar.
                Ex: [{"Label":"<your field name>", "Color":"<your desired color in hex>"}]
        sorting: Whether to sort ascending, descending, or neither when charting agent fields
        sort_by: The agent field to sort by
        canvas_height, canvas_width: The width and height to draw the chart on the page, in pixels.
                                    Default to 800 x 400
        data_collector_name: Name of the DataCollector object in the model to retrieve data from.
    """

    package_includes = [D3_JS_FILE, "BarChartModule.js"]

    def __init__(
        self,
        fields,
        scope="model",
        sorting="none",
        sort_by="none",
        canvas_height=400,
        canvas_width=800,
        data_collector_name="datacollector",
    ):
        """
        Create a new bar chart visualization.

        Args:
            scope: "model" if visualizing model-level fields, "agent" if visualizing agent-level
                   fields.
            fields: A List of Dictionaries containing information about each field to be charted,
                    including the name of the datacollector field and the desired color of the
                    corresponding bar.
                    Ex: [{"Label":"<your field name>", "Color":"<your desired color in hex>"}]
            sorting: "ascending", "descending", or "none"
            sort_by: The agent field to sort by
            canvas_height, canvas_width: Size in pixels of the chart to draw.
            data_collector_name: Name of the DataCollector to use.
        """

        self.scope = scope
        self.fields = fields
        self.sorting = sorting
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.data_collector_name = data_collector_name

        fields_json = json.dumps(self.fields)
        new_element = "new BarChartModule({}, {}, {}, '{}', '{}')"
        new_element = new_element.format(
            fields_json, canvas_width, canvas_height, sorting, sort_by
        )
        self.js_code = "elements.push(" + new_element + ")"

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        if self.scope == "agent":
            df = data_collector.get_agent_vars_dataframe().astype("float")
            latest_step = df.index.levels[0][-1]
            label_strings = [f["Label"] for f in self.fields]
            dict = df.loc[latest_step].T.loc[label_strings].to_dict()
            current_values = list(dict.values())

        elif self.scope == "model":
            out_dict = {}
            for s in self.fields:
                name = s["Label"]
                try:
                    val = data_collector.model_vars[name][-1]
                except (IndexError, KeyError):
                    val = 0
                out_dict[name] = val
            current_values.append(out_dict)
        else:
            raise ValueError("scope must be 'agent' or 'model'")
        return current_values
