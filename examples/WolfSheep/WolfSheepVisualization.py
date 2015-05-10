'''
Visualization for the Wolf-Sheep Predation
'''

from WolfSheep import Wolf, Sheep
from mesa.visualization.TextVisualization import TextVisualization, TextGrid


class WolfSheepVisualization(TextVisualization):
    '''
    ASCII visualization of the WolfSheepPredation model.

    Each cell displays S if only sheep, W if only wolves, or X if both.
    (blank if none)
    '''

    def __init__(self, model):
        self.model = model
        grid_viz = TextGrid(self.model.grid, self.draw_cell)
        self.elements = [grid_viz]

    @staticmethod
    def draw_cell(cell):
        if len(cell) == 0:
            return " "
        if len([obj for obj in cell if isinstance(obj, Sheep)]) == len(cell):
            return "S"
        if len([obj for obj in cell if isinstance(obj, Wolf)]) == len(cell):
            return "W"
        else:
            return "X"
