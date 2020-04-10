# -*- coding: utf-8 -*-
"""
Modular Canvas Rendering
========================

Module for visualizing model objects in hexagonal grid cells.

"""
from collections import defaultdict
from mesa.visualization.ModularVisualization import VisualizationElement


class CanvasHexGrid(VisualizationElement):
    """ A CanvasHexGrid object functions similarly to a CanvasGrid object. It takes a portrayal dictionary and talks to HexDraw.js to draw that shape.

    A portrayal as a dictionary with the following structure:
        "x", "y": Coordinates for the cell in which the object is placed.
        "Shape": Can be either "hex" or "circle"
            "r": The radius, defined as a fraction of cell size. r=1 will
                 fill the entire cell.
        "Color": The color to draw the shape in; needs to be a valid HTML
                 color, e.g."Red" or "#AA08F8"
        "Filled": either "true" or "false", and determines whether the shape is
                  filled or not.
        "Layer": Layer number of 0 or above; higher-numbered layers are drawn
                 above lower-numbered layers.
        "text": The text to be inscribed inside the Shape. Normally useful for
                showing the unique_id of the agent.
        "text_color": The color to draw the inscribed text. Should be given in
                      conjunction of "text" property.


    Attributes:
        portrayal_method: Function which generates portrayals from objects, as
                          described above.
        grid_height, grid_width: Size of the grid to visualize, in cells.
        canvas_height, canvas_width: Size, in pixels, of the grid visualization
                                     to draw on the client.
        template: "canvas_module.html" stores the module's HTML template.

    """

    package_includes = ["HexDraw.js", "CanvasHexModule.js", "InteractionHandler.js"]
    portrayal_method = None  # Portrayal function
    canvas_width = 500
    canvas_height = 500

    def __init__(
        self,
        portrayal_method,
        grid_width,
        grid_height,
        canvas_width=500,
        canvas_height=500,
    ):
        """ Instantiate a new CanvasGrid.

        Args:
            portrayal_method: function to convert each object on the grid to
                              a portrayal, as described above.
            grid_width, grid_height: Size of the grid, in cells.
            canvas_height, canvas_width: Size of the canvas to draw in the
                                         client, in pixels. (default: 500x500)

        """
        self.portrayal_method = portrayal_method
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        new_element = "new CanvasHexModule({}, {}, {}, {})".format(
            self.canvas_width, self.canvas_height, self.grid_width, self.grid_height
        )

        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        grid_state = defaultdict(list)
        for x in range(model.grid.width):
            for y in range(model.grid.height):
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                for obj in cell_objects:
                    portrayal = self.portrayal_method(obj)
                    if portrayal:
                        portrayal["x"] = x
                        portrayal["y"] = y
                        grid_state[portrayal["Layer"]].append(portrayal)

        return grid_state
