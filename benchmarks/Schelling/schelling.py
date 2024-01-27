from mesa import Model
from mesa.experimental.cell_space import OrthogonalGrid, CellAgent
from mesa.time import RandomActivation


class SchellingAgent(CellAgent):
    """
    Schelling segregation agent
    """

    def __init__(self, unique_id, model, agent_type, radius):
        """
        Create a new Schelling agent.
        Args:
           unique_id: Unique identifier for the agent.
           x, y: Agent initial location.
           agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(unique_id, model)
        self.type = agent_type
        self.radius = radius

    def step(self):
        similar = 0
        for neighbor in self.cell.neighborhood(radius=self.radius).agents:
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.model.homophily:
            self.move_to(self.model.grid.select_random_empty_cell())
        else:
            self.model.happy += 1


class Schelling(Model):
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

        self.schedule = RandomActivation(self)
        self.grid = OrthogonalGrid(height, width, torus=True)

        self.happy = 0

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid:
            if self.random.random() < self.density:
                agent_type = 1 if self.random.random() < self.minority_pc else 0
                agent = SchellingAgent(self.next_id(), self, agent_type, radius)
                agent.move_to(cell)
                self.schedule.add(agent)

    def step(self):
        """
        Run one step of the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()


if __name__ == "__main__":
    import time

    # model = Schelling(15, 40, 40, 3, 1, 0.625)
    model = Schelling(15, 100, 100, 8, 2, 0.8)

    start_time = time.perf_counter()
    for _ in range(100):
        model.step()

    print(time.perf_counter() - start_time)
