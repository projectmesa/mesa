from mesa.visualization.ModularVisualization import VisualizationElement

class ChartModule(VisualizationElement):
    '''
    Module for drawing live-updating line charts using Charts.js

    TODO: Fix the following limitations:
        Target model having a DataCollector named datacollector.
        Can only use model-level variables
    '''

    template="chart_module.html"

    def __init__(self, series, canvas_height=200, canvas_width=500):
        '''
        Create a new line chart visualization.

        Args:
            series: A list of dictionaries containing series names and 
                    HTML colors to chart them in, e.g.
                    [{"Label": "happy", "Color": "Black"},]
            canvas_height, canvas_width: Size in pixels of the chart to draw.
        '''

        self.series = series
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        self.render_args = {
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "series": self.series
        }

    def render(self, model):
        current_values = []
        for s in self.series:
            name = s["Label"]
            try:
                val = model.datacollector.model_vars[name][-1] # Latest value
            except:
                val = 0
            current_values.append(val)
        return current_values



