"""Schelling separation for performance benchmarking."""
from __future__ import annotations

from mesa import Model
from mesa.experimental.cell_space import CellAgent, OrthogonalMooreGrid, Cell


class SchellingAgent(CellAgent):
    """Schelling segregation agent."""

    def __init__(self, model: Schelling, agent_type: int, radius: int, homophily: float, cell: Cell):
        """Create a new Schelling agent.

        Args:
            model: model instance
            agent_type: type of agent (minority=1, majority=0)
            radius: size of neighborhood of agent
            homophily: fraction of neighbors of the same type that triggers movement
            cell: the cell in which the agent is located
        """
        super().__init__(model)
        self.type = agent_type
        self.radius = radius
        self.homophily = homophily
        self.cell = cell

    def step(self):
        """Run one step of the agent."""
        similar = 0
        neighborhood = self.cell.get_neighborhood(radius=self.radius)
        for neighbor in neighborhood.agents:
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.homophily:
            self.cell = self.model.grid.select_random_empty_cell()
        else:
            self.model.happy += 1


class Schelling(Model):
    """Model class for the Schelling segregation model."""

    def __init__(
        self,
        simulator,
        height=40,
        width=40,
        homophily=3,
        radius=1,
        density=0.8,
        minority_pc=0.5,
        seed=None,
    ):
        """Create a new Schelling model.

        Args:
            simulator: simulator instance
            height: height of the grid
            width: width of the grid
            homophily: Minimum number of agents of same class needed to be happy
            radius: Search radius for checking similarity
            density: Initial Chance for a cell to populated
            minority_pc: Chances for an agent to be in minority class
            seed: the seed for the random number generator
            simulator: a simulator instance
        """
        super().__init__(seed=seed)
        self.simulator = simulator
        self.minority_pc = minority_pc
        self.happy = 0

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
                SchellingAgent(self, agent_type, radius, homophily, cell)

    def step(self):
        """Run one step of the model."""
        self.happy = 0  # Reset counter of happy agents
        self.agents.shuffle_do("step")


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
