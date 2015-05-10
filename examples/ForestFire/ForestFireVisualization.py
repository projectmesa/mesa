from ForestFire import ForestFire
from mesa.visualization.ModularCanvasGridVisualization import CanvasGrid
from mesa.visualization.ModularChartVisualization import ChartModule
from mesa.visualization.ModularVisualization import ModularServer


def forestfire_draw(tree):
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

<<<<<<< HEAD
canvas_element  = CanvasGrid(forestfire_draw, 100, 100, 500, 500)
tree_chart = ChartModule([
                           {"Label": "Fine", "Color": "green"},
                           {"Label": "On Fire", "Color": "red"},
                           {"Label": "Burned Out", "Color": "black"}
                         ])

server = ModularServer(ForestFire, [canvas_element, tree_chart], "Forest Fire",
                       100, 100, 0.65)
server.launch()
=======
server = CanvasServer(ForestFire, forestfire_draw, 500, 500,
                      "Forest Fire", 100, 100, 0.45)
server.launch()
>>>>>>> master
