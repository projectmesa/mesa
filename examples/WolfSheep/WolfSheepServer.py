from WolfSheep import Wolf, Sheep, WolfSheepPredation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "Filled": "true"}

    if type(agent) is Sheep:
        portrayal["Color"] = "#666666"
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    elif type(agent) is Wolf:
        portrayal["Color"] = "#AA0000"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal

canvas_element = CanvasGrid(wolf_sheep_portrayal, 20, 20, 500, 500)

server = ModularServer(WolfSheepPredation, [canvas_element],
                      "WolfSheep")
server.launch()
