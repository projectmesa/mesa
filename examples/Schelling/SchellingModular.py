from Schelling import SchellingModel
from mesa.visualization.ModularTextVisualization import TextElement
from mesa.visualization.ModularVisualization import ModularServer
import tornado.ioloop


class HappyElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)

happy_element = HappyElement()

server = ModularServer(SchellingModel, [happy_element], "Schelling", 
                       10, 10, 0.8, 0.2, 3)

server.listen(8888)
tornado.ioloop.IOLoop.instance().start()
