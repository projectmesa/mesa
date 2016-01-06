from cgol_model import CGoLModel
from cgol_cell import CGoLCell
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def cgol_draw(cell):
    '''
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the cell in its current state.
    :param cell:  the cell in the simulation
    :return: the portrayal dictionary.
    '''
    assert cell is not None
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    x, y = cell.getX(), cell.getY()
    portrayal["x"] = x
    portrayal["y"] = y
    colors = {CGoLCell.DEAD: "white",
              CGoLCell.ALIVE: "black"}
    portrayal["Color"] = colors[cell.getState()]
    return portrayal

# Make a world that is 50x50, on a 250x250 display.
canvas_element = CanvasGrid(cgol_draw, 50, 50, 250, 250)

server = ModularServer(CGoLModel, [canvas_element], "Game of Life",
                       50, 50)
server.launch()
