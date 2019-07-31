import json

from mesa import Model, Agent
from mesa import time
from mesa.space import SingleGrid


class SchellingAgent(Agent):
    """
    Schelling segregation agent
    """

    def __init__(self, pos, model, agent_type):
        """
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type

    def step(self):
        similar = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1

    def as_json(self):
        return json.dumps({"x": self.pos[0], "y": self.pos[1], "agent_type": self.type})


class Schelling(Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(
        self, height=20, width=20, density=0.8, schedule="RandomActivation", **kwargs
    ):
        """
        """

        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = 0.4
        self.homophily = 3

        self.schedule = getattr(time, schedule)(self)
        self.grid = SingleGrid(height, width, torus=True)

        self.happy = 0

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:
                if self.random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                agent = SchellingAgent((x, y), self, agent_type)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True

    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()

        if self.happy == self.schedule.get_agent_count():
            self.running = False

    def on_click(self, x, y, agent_type, **kwargs):
        """Change agent type on click."""
        self.grid[x][y].type = 1 if agent_type == 0 else 0
