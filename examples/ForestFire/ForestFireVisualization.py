from ForestFire import ForestFire
from mesa.visualization.CanvasServer import CanvasServer


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

server = CanvasServer(ForestFire, forestfire_draw, 500, 500,
                      "Forest Fire", 100, 100, 0.65)
server.launch()
