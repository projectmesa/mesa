import mesa

from .model import BoidFlockers
from .SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    if not agent.neighbors:  # Only for the first Frame
        neighbors = len(agent.model.space.get_neighbors(agent.pos, agent.vision, False))
    else:
        neighbors = len(agent.neighbors)

    if neighbors <= 1:
        return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}
    elif neighbors >= 2:
        return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Green"}


boid_canvas = SimpleCanvas(
    portrayal_method=boid_draw, canvas_height=500, canvas_width=500
)
model_params = {
    "population": mesa.visualization.Slider(
        name="Number of boids",
        value=100,
        min_value=10,
        max_value=200,
        step=10,
        description="Choose how many agents to include in the model",
    ),
    "width": 100,
    "height": 100,
    "speed": mesa.visualization.Slider(
        name="Speed of Boids",
        value=5,
        min_value=1,
        max_value=20,
        step=1,
        description="How fast should the Boids move",
    ),
    "vision": mesa.visualization.Slider(
        name="Vision of Bird (radius)",
        value=10,
        min_value=1,
        max_value=50,
        step=1,
        description="How far around should each Boid look for its neighbors",
    ),
    "separation": mesa.visualization.Slider(
        name="Minimum Separation",
        value=2,
        min_value=1,
        max_value=20,
        step=1,
        description="What is the minimum distance each Boid will attempt to keep from any other",
    ),
}

server = mesa.visualization.ModularServer(
    model_cls=BoidFlockers,
    visualization_elements=[boid_canvas],
    name="Boid Flocking Model",
    model_params=model_params,
)
