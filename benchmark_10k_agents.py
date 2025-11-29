"""10,000 agent Solara benchmark for SVG-based visualization performance testing."""

import random

from mesa.time import RandomActivation

from mesa import Agent, Model
from mesa.space import MultiGrid


class TestAgent(Agent):
    """Simple test agent that randomly moves each step."""

    def step(self) -> None:
        """Move to a random position within the grid."""
        x = random.randrange(self.model.grid.width)
        y = random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))


class TestModel(Model):
    """Model containing 10,000 randomly moving agents."""

    def __init__(self, n: int = 10_000, width: int = 100, height: int = 100) -> None:
        """Initialize the test model with N agents on a grid."""
        super().__init__()
        self.num_agents = n
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)

        for _ in range(self.num_agents):
            agent = TestAgent(self)
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def step(self) -> None:
        """Advance the model by one step."""
        self.schedule.step()


def agent_portrayal(agent: TestAgent) -> dict:
    """Return SVG portrayal for an agent."""
    return {
        "shape": "url:agent_worker.svg",
        "scale": 0.8,
    }


# Solara must ONLY be imported at runtime, never during docs build
if __name__ == "__main__":
    from mesa.visualization.solara_viz import SolaraViz

    model = TestModel()

    page = SolaraViz(
        model,
        visualization_description="10,000 Agent Baseline Benchmark",
        agent_portrayal=agent_portrayal,
    )
