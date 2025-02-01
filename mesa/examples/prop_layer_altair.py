from mesa import Agent, Model
from mesa.mesa_logging import DEBUG, log_to_stderr
from mesa.space import MultiGrid, PropertyLayer
from mesa.visualization import SolaraViz
from mesa.visualization.components.altair_components import make_altair_space

log_to_stderr(DEBUG)


# A simple agent that consumes sugar
class SimpleAgent(Agent):
    def __init__(self, model, pos):
        super().__init__(model)
        self.pos = pos

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()
        x, y = self.pos
        sugar = self.model.grid.properties["sugar"].data[(x, y)]
        self.model.grid.properties["sugar"].set_cell((x, y), max(0, sugar - 1))


# Simple model with a property layer for sugar
class SimpleModel(Model):
    def __init__(self, num_agents=100, width=10, height=10, seed=None):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        layer1 = PropertyLayer(
            name="sugar", width=width, height=width, default_value=10
        )
        self.grid = MultiGrid(
            width=width, height=height, torus=True, property_layers=layer1
        )

        for _ in range(self.num_agents):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = SimpleAgent(self, (x, y))
            self.grid.place_agent(a, (x, y))
        self.running = True

    def step(self):
        self.agents.shuffle_do("step")


model_params = {
    "width": 10,
    "height": 10,
    "num_agents": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
}


propertylayer_portrayal = {
    "sugar": {
        "colormap": "pastel1",
        "alpha": 0.75,
        "colorbar": True,
        "vmin": 0,
        "vmax": 10,
    }
}

model = SimpleModel(50, 10, 10)


def agent_portrayal(agent):
    return {"Shape": "o", "color": "red", "size": 20}


SpaceGraph = make_altair_space(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=propertylayer_portrayal,
    post_process=None,
)


page = SolaraViz(
    model,
    components=[SpaceGraph],
    model_params=model_params,
    name="Simple Model",
)
page  # noqa
