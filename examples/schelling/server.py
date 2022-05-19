import mesa

from model import Schelling


class HappyElement(mesa.visualization.TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}

    if agent.type == 0:
        portrayal["Color"] = ["#FF0000", "#FF9999"]
        portrayal["stroke_color"] = "#00FF00"
    else:
        portrayal["Color"] = ["#0000FF", "#9999FF"]
        portrayal["stroke_color"] = "#000000"
    return portrayal


happy_element = HappyElement()
canvas_element = mesa.visualization.CanvasGrid(schelling_draw, 20, 20, 500, 500)
happy_chart = mesa.visualization.ChartModule([{"Label": "happy", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": mesa.visualization.UserSettableParameter(
        "slider", "Agent density", 0.8, 0.1, 1.0, 0.1
    ),
    "minority_pc": mesa.visualization.UserSettableParameter(
        "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    ),
    "homophily": mesa.visualization.UserSettableParameter(
        "slider", "Homophily", 3, 0, 8, 1
    ),
}

server = mesa.visualization.ModularServer(
    Schelling, [canvas_element, happy_element, happy_chart], "Schelling", model_params
)
