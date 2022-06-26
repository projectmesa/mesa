import time

import bokeh
from bokeh.models import ColumnDataSource
import panel as pn


def get_grid_values(model, portray):
    """Get grid cell states"""
    xs = []
    ys = []
    values = []
    for x in range(model.grid.width):
        for y in range(model.grid.height):
            cell_objects = model.grid.get_cell_list_contents([(x, y)])
            portrayal = None
            for obj in cell_objects:
                portrayal = portray(obj)
            if portrayal is not None:
                xs.append(x)
                ys.append(y)
                values.append(portrayal)
    return ColumnDataSource(dict(x=xs, y=ys, value=values))


class JupyterSpaceVisualization:
    def __init__(self, model_cls, portray):
        self.model = model_cls()
        self.portray = portray
        pn.extension()
        self.space_pane = pn.pane.Bokeh()
        self.pane = pn.Row(self.space_pane, sizing_mode="stretch_width")
        self.space_pane.object = self.render_space(self.model, self.portray)

    @staticmethod
    def render_space(model, portray):
        ds = get_grid_values(model, portray)
        p = bokeh.plotting.figure(
            plot_width=500,
            plot_height=500,
            x_range=(-1, model.grid.width),
            y_range=(-1, model.grid.height),
        )
        p.circle(
            x="x", y="y", size=10, source=ds, fill_color="value", line_color="black"
        )
        p.background_fill_color = "white"
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.toolbar.logo = None
        return p

    def run(self, steps=50, sleep=0.3):
        for i in range(steps):
            self.model.step()
            self.space_pane.object = self.render_space(self.model, self.portray)
            time.sleep(sleep)
