"""
handles the definition of the canvas parameters and
the drawing of the model representation on the canvas
"""
# import webbrowser

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .model import ColorPatches

_COLORS = ['Aqua', 'Blue', 'Fuchsia', 'Gray', 'Green',
           'Lime', 'Maroon', 'Navy', 'Olive', 'Orange', 'Purple',
           'Red', 'Silver', 'Teal', 'White', 'Yellow']


grid_rows = 50
grid_cols = 25
cell_size = 10
canvas_width = grid_rows * cell_size
canvas_height = grid_cols * cell_size


def color_patch_draw(cell):
    '''
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the cell in its current state.

    :param cell:  the cell in the simulation

    :return: the portrayal dictionary.

    '''
    assert cell is not None
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    portrayal["x"] = cell.get_row()
    portrayal["y"] = cell.get_col()
    portrayal["Color"] = _COLORS[cell.get_state()]
    return portrayal


canvas_element = CanvasGrid(color_patch_draw,
                            grid_rows, grid_cols,
                            canvas_width, canvas_height)

server = ModularServer(ColorPatches,
                       [canvas_element], "Color Patches",
                       {"width": canvas_width, "height": canvas_height})

# webbrowser.open('http://127.0.0.1:8521')  # TODO: make this configurable
