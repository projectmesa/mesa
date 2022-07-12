import mesa

from .agents import Trader, Sugar, Spice
from .model import SugarscapeG1mt

color_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800"}
spice_dic = {4: "#8B7E66", 3: "#CDBA96", 2: "#EED8AE", 1: "#FFE7BA"}


def Trader_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Trader:
        portrayal["Shape"] = "sugarscape_cg/resources/ant.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    elif type(agent) is Sugar:
        if agent.amount != 0:
            portrayal["Color"] = color_dic[agent.amount]
        else:
            portrayal["Color"] = "#D6F5D6"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif type(agent) is Spice:
        if agent.amount != 0:
            portrayal["Color"] = spice_dic[agent.amount]
        else:
            portrayal["Color"] = "#D6F5D6"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(Trader_portrayal, 50, 50, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [{"Label": "Trader", "Color": "#AA0000"}]
)

server = mesa.visualization.ModularServer(
    SugarscapeG1mt, [canvas_element, chart_element], "Sugarscape 2 Constant Growback"
)
