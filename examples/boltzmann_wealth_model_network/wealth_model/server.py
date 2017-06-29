from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

from .model import MoneyModel
from .NetworkVisualization import NetworkElement

grid = NetworkElement()
chart = ChartModule([
    {"Label": "Gini", "Color": "Black"}],
    data_collector_name='datacollector'
)

server = ModularServer(MoneyModel, [grid, chart], "Money Model", 7, 8)
server.port = 8521
