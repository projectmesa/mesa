import mesa

from .model import SugarscapeG1mt
from .resource_agents import Spice, Sugar
from .trader_agents import Trader

sugar_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800"}
spice_dic = {4: "#acac00", 3: "#c5c500", 2: "#dfdf00", 1: "#f8f800"}


def Agent_portrayal(agent):
    if agent is None:
        return

    if isinstance(agent, Trader):
        return {
            "Shape": "circle",
            "Filled": "true",
            "r": 0.5,
            "Layer": 0,
            "Color": "#FF0A01",
        }

    elif isinstance(agent, Sugar):
        color = sugar_dic[agent.amount] if agent.amount != 0 else "#D6F5D6"
        layer = 1 if agent.amount > 2 else 0
        return {
            "Color": color,
            "Shape": "rect",
            "Filled": "true",
            "Layer": layer,
            "w": 1,
            "h": 1,
        }

    elif isinstance(agent, Spice):
        color = spice_dic[agent.amount] if agent.amount != 0 else "#D6F5D6"
        layer = 1 if agent.amount > 2 else 0
        return {
            "Color": color,
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1,
        }

    return {}


canvas_element = mesa.visualization.CanvasGrid(Agent_portrayal, 50, 50, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [{"Label": "Trader", "Color": "#AA0000"}]
)
chart_element2 = mesa.visualization.ChartModule(
    [{"Label": "Price", "Color": "#000000"}]
)

server = mesa.visualization.ModularServer(
    SugarscapeG1mt,
    [canvas_element, chart_element, chart_element2],
    "Sugarscape with Traders",
)
# server.launch()
