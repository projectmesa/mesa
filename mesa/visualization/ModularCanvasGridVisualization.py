'''
Modular Canvas rendering
'''
from collections import defaultdict
from mesa.visualization.ModularVisualization import VisualizationElement

class CanvasGrid(VisualizationElement):
    template = "canvas_module.html"
    portrayal_method = None # Portrayal function
    canvas_height = 500
    canvas_width = 500

    def __init__(self, portrayal_method, grid_height, grid_width,
                 canvas_height=500, canvas_width=500):
        '''
        Instantiate a new CanvasGrid
        '''

        self.portrayal_method = portrayal_method
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        self.render_args = {
                            "grid_height": self.grid_height,
                            "grid_width": self.grid_width,
                            "canvas_height": self.canvas_height,
                            "canvas_width": self.canvas_width
                            }

    def render(self, model):
        grid_state = defaultdict(list)
        for y in range(model.grid.height):
            for x in range(model.grid.width):
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                for obj in cell_objects:
                    portrayal = self.portrayal_method(obj)
                    if portrayal:
                        grid_state[portrayal["Layer"]].append(portrayal)
        return grid_state


