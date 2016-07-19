"""
handles the definition of the canvas parameters and
the drawing of the model representation on the canvas
"""
# import webbrowser

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .model import ColorPatchModel

_COLORS = ['Aqua', 'Blue', 'Fuchsia', 'Gray', 'Green',
           'Lime', 'Maroon', 'Navy', 'Olive', 'Orange', 'Purple',
           'Red', 'Silver', 'Teal', 'White', 'Yellow']


GRID_ROWS = 50
GRID_COLS = 25
CELL_SIZE = 10
CANVAS_WIDTH = GRID_ROWS * CELL_SIZE
CANVAS_HEIGHT = GRID_COLS * CELL_SIZE


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


CANVAS_ELEMENT = CanvasGrid(color_patch_draw,
                            GRID_ROWS, GRID_COLS,
                            CANVAS_WIDTH, CANVAS_HEIGHT)

server = ModularServer(ColorPatchModel,
                       [CANVAS_ELEMENT], "Color Patches",
                       GRID_ROWS, GRID_COLS)

# webbrowser.open('http://127.0.0.1:8888')  # TODO: make this configurable
