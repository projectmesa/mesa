from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from forest_fire.model import ForestFire


def forest_fire_portrayal(tree):
    if tree is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = tree.get_pos()
    portrayal["x"] = x
    portrayal["y"] = y
    colors = {"Fine": "#00AA00",
              "On Fire": "#880000",
              "Burned Out": "#000000"}
    portrayal["Color"] = colors[tree.condition]
    return portrayal

canvas_element = CanvasGrid(forest_fire_portrayal, 100, 100, 500, 500)
tree_chart = ChartModule([{"Label": "Fine", "Color": "green"},
                          {"Label": "On Fire", "Color": "red"},
                          {"Label": "Burned Out", "Color": "black"}])

server = ModularServer(ForestFire, [canvas_element, tree_chart], "Forest Fire",
                       100, 100, 0.65)
