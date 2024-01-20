import random

from mesa import Model, Agent
from mesa.time import RandomActivation
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
        r = self.model.radius
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, radius=r):
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1


class SchellingModel(Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(
        self, seed, height, width, homophily, radius, density, minority_pc=0.5
    ):
        """ """
        super().__init__(seed=seed)
        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily
        self.radius = radius

        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(height, width, torus=True)

        self.happy = 0

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cont, pos in self.grid.coord_iter():
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0
                agent = SchellingAgent(pos, self, agent_type)
                self.grid.place_agent(agent, pos)
                self.schedule.add(agent)

    def step(self):
        """
        Run one step of the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
