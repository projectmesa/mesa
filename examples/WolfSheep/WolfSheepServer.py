from WolfSheep import Wolf, Sheep, WolfSheepPredation
from mesa.visualization.CanvasServer import CanvasServer


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "x": agent.pos[0], "y": agent.pos[1],
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

server = CanvasServer(WolfSheepPredation, wolf_sheep_portrayal, 500, 500,
                      "WolfSheep")
server.launch()
