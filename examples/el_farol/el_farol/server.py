from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import ElFarolBar

COLORS = {True: "Green", False: "Red"}


def el_farol_portrayal(customer):
    
    #portrayal = {"Shape": "circle", "Filled":True,"Layer": 0}
    #(x, y) = customer.pos
    #portrayal["x"] = x
    #portrayal["y"] = y
    #portrayal["Color"] = "red"#COLORS[customer.attend]
    #return portrayal
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.1}
    return portrayal

canvas_element = CanvasGrid(el_farol_portrayal, 20,20, 500, 500)
#tree_chart = ChartModule(
#    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
#)
#pie_chart = PieChartModule(
#    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
#)

model_params = {
    "num_strategies":10,
    "height": 20,
    "width": 20,
    "N":10,
    "num_strategies": UserSettableParameter("slider", "Number of Strategies", 10, 0, 20, 1),
}
server = ModularServer(
    ElFarolBar,[canvas_element],"El Farol Restaurant",model_params
)
