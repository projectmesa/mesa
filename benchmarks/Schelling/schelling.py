from mesa import Model
from mesa.experimental.cell_space import CellAgent, OrthogonalMooreGrid
from mesa.time import RandomActivation


class SchellingAgent(CellAgent):
    """
    Schelling segregation agent
    """

    def __init__(self, unique_id, model, agent_type, radius, homophily):
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
        self.homophily = homophily

    def step(self):
        similar = 0
        neighborhood = self.cell.neighborhood(radius=self.radius)
        for neighbor in neighborhood.agents:
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.homophily:
            self.move_to(self.model.grid.select_random_empty_cell())
        else:
            self.model.happy += 1


class Schelling(Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(
        self,
        height=40,
        width=40,
        homophily=3,
        radius=1,
        density=0.8,
        minority_pc=0.5,
        seed=None,
        simulator=None,
    ):
        """
        Create a new Schelling model.

        Args:
            height, width: Size of the space.
            density: Initial Chance for a cell to populated
            minority_pc: Chances for an agent to be in minority class
            homophily: Minimum number of agents of same class needed to be happy
            radius: Search radius for checking similarity
            seed: Seed for Reproducibility
        """
        super().__init__(seed=seed)
        self.minority_pc = minority_pc
        self.simulator = simulator

        self.schedule = RandomActivation(self)
        self.grid = OrthogonalMooreGrid(
            [height, width],
            torus=True,
            capacity=1,
            random=self.random,
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid:
            if self.random.random() < density:
                agent_type = 1 if self.random.random() < self.minority_pc else 0
                agent = SchellingAgent(
                    self.next_id(), self, agent_type, radius, homophily
                )
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

    # model = Schelling(seed=15, height=40, width=40, homophily=3, radius=1, density=0.625)
    model = Schelling(
        seed=15, height=100, width=100, homophily=8, radius=2, density=0.8
    )

    start_time = time.perf_counter()
    for _ in range(100):
        model.step()
    print(time.perf_counter() - start_time)
