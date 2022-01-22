"""
Chart Module
============

Module for drawing live-updating line charts using Charts.js

"""
import json
import statistics
from mesa.visualization.ModularVisualization import VisualizationElement


class ChartModule(VisualizationElement):
    """Each chart can visualize one or more model-level series as lines
     with the data value on the Y axis and the step number as the X axis.

    At the moment, each call to the render method returns a list of the most
    recent values of each series.

    Attributes:
        series: A list of dictionaries containing information on series to
                plot. Each dictionary must contain (at least) the "Label" and
                "Color" keys. The "Label" value must correspond to a
                model-level series collected by the model's DataCollector, and
                "Color" must have a valid HTML color.
        canvas_height, canvas_width: The width and height to draw the chart on
                                     the page, in pixels. Default to 200 x 500
        data_collector_name: Name of the DataCollector object in the model to
                             retrieve data from.
        template: "chart_module.html" stores the HTML template for the module.


    Example:
        schelling_chart = ChartModule([{"Label": "happy", "Color": "Black"}],
                                      data_collector_name="datacollector")

    TODO:
        More Pythonic customization; in particular, have both series-level and
        chart-level options settable in Python, and passed to the front-end
        the same way that "Color" is currently.

    """

    package_includes = ["Chart.min.js", "ChartModule.js"]

    def __init__(
        self,
        series,
        canvas_height=200,
        canvas_width=500,
        data_collector_name="datacollector",
    ):
        """
        Create a new line chart visualization.

        Args:
            series: A list of dictionaries containing series names and
                    HTML colors to chart them in, e.g.
                    [{"Label": "happy", "Color": "Black"},]
            canvas_height, canvas_width: Size in pixels of the chart to draw.
            data_collector_name: Name of the DataCollector to use.
        """

        self.series = series
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.data_collector_name = data_collector_name

        series_json = json.dumps(self.series)
        new_element = "new ChartModule({}, {},  {})"
        new_element = new_element.format(series_json, canvas_width, canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        for s in self.series:
            name = s["Label"]
            entity = s["Type"]
            if entity == "Model":
                try:
                    val = data_collector.model_vars[name][-1]  # Latest value
                except (IndexError, KeyError):
                    val = 0
            elif entity == "Agent":
                agent_dict = {e.__name__: e for e in list(model.schedule.agents_by_type.keys())}
                agent_type = agent_dict[s["Agent_type"]]
                try:
                    # Get the reporter from the name
                    reporter = model.datacollector.agent_name_index[agent_type][name]

                    # Get the index of the reporter
                    attr_index = model.datacollector.agent_attr_index[agent_type][reporter]

                    # Create a dictionary with all attributes from all agents
                    attr_dict = model.datacollector._agent_records[agent_type]

                    # Get the values from all agents in a list
                    values_tuples = list(attr_dict.values())[-1]

                    # Get the correct value using the attribute index
                    values = [value_tuple[attr_index] for value_tuple in values_tuples]

                    # Calculate the mean among all agents
                    val = statistics.mean(values)

                except (IndexError, KeyError):
                    val = 0
            current_values.append(val)
        return current_values
