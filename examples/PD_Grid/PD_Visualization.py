from pd_grid import PD_Model

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParams import UserParam, UserOption

def pd_draw(agent):
    '''
    Canvas portrayal method.
    '''
    if agent is None:
        return

    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    if agent.move == "C":
        portrayal["Color"] = "Blue"
    if agent.move == "D":
        portrayal["Color"] = "Red"
    return portrayal


canvas = CanvasGrid(pd_draw, 20, 20, 500, 500)
model_params = {"width": 20, "height": 20, 
                "schedule_type": 
                UserOption("Sequential", list(PD_Model.schedule_types.keys()))}

server = ModularServer(PD_Model, [canvas], "Prisoner's Dilemma Grid", 
                       model_params)
server.launch()