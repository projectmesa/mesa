import random
from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.visualization.solara_viz import SolaraViz


class TestAgent(Agent):
    def step(self):
        x = random.randrange(self.model.grid.width)
        y = random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))


class TestModel(Model):
    def __init__(self, n=10_000, width=100, height=100):
        super().__init__()
        self.num_agents = n
        self.grid = MultiGrid(width, height, torus=True)

        for _ in range(self.num_agents):
            agent = TestAgent(self)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        for agent in self.agents:
            agent.step()

#BASELINE MODE (CIRCLES)
'''def agent_portrayal(agent):
    return {
        "shape": "circle",
        "r": 0.5,
        "filled": True,
        "color": "blue",
    }
'''

#with SVG
def agent_portrayal(agent):
    return {
        "shape": "url:/static/agent_worker.svg",
        "scale": 0.8,
    }




model = TestModel()

page = SolaraViz(
    model,
    visualization_description="10,000 Agent Baseline Benchmark",
    agent_portrayal=agent_portrayal,
)

page
