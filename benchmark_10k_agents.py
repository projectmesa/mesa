"""10,000 agent Solara benchmark for SVG-based visualization performance testing."""

import random
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.visualization.solara_viz import SolaraViz


class TestAgent(Agent):
    """A simple agent that randomly moves each step."""

    def step(self):
        """Move the agent to a random position."""
        x = random.randrange(self.model.grid.width)
        y = random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))


class TestModel(Model):
    """Test model used for benchmarking 10,000 agents."""

    def __init__(self, n=10_000, width=100, height=100):
        """Initialize the model with N agents on a grid."""
        super().__init__()
        self.num_agents = n
        self.grid = MultiGrid(width, height, torus=True)

        for _ in range(self.num_agents):
            agent = TestAgent(self)
            x = random.randrange(width)
            y = random.randrange(height)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        """Advance the model by one step."""
        for agent in self.agents:
            agent.step()


def agent_portrayal(agent):
    """Render agents using the SVG worker icon."""
    return {
        "shape": "url:/static/agent_worker.svg",
        "scale": 0.8,
    }


model = TestModel()

page = SolaraViz(
    model,
    visualization_description="10,000 Agent SVG Performance Benchmark",
    agent_portrayal=agent_portrayal,
)
