from Schelling import SchellingModel
from mesa.visualization.ModularTextVisualization import TextElement
from mesa.visualization.ModularCanvasGridVisualization import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import tornado.ioloop



class HappyElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''
    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)

def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
    if agent.type == 0:
        portrayal["Color"] = "Red"
    else:
        portrayal["Color"] = "Blue"
    return portrayal

happy_element = HappyElement()
canvas_element = CanvasGrid(schelling_draw, 10, 10, 500, 500)

server = ModularServer(SchellingModel, [canvas_element, happy_element], 
                       "Schelling", 10, 10, 0.8, 0.2, 3)
server.launch()
#server.listen(8888)
#tornado.ioloop.IOLoop.instance().start()
