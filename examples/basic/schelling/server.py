import mesa
from model import Schelling


def get_happy_agents(model):
    """
    Display a text count of how many happy agents there are.
    """
    return f"Happy agents: {model.happy}"


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


canvas_element = mesa.visualization.CanvasGrid(schelling_draw, 20, 20, 500, 500)
happy_chart = mesa.visualization.ChartModule([{"Label": "happy", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": mesa.visualization.Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": mesa.visualization.Slider("Fraction minority", 0.2, 0.00, 1.0, 0.05),
    "homophily": mesa.visualization.Slider("Homophily", 3, 0, 8, 1),
}

server = mesa.visualization.ModularServer(
    Schelling,
    [canvas_element, get_happy_agents, happy_chart],
    "Schelling",
    model_params,
)
