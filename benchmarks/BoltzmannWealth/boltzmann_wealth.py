"""boltmann wealth model for performance benchmarking.

https://github.com/projectmesa/mesa-examples/blob/main/examples/boltzmann_wealth_model_experimental/model.py
"""

import mesa
import mesa.spaces as spaces


def compute_gini(model):
    """Calculate gini for wealth in model.

    Args:
        model: a Model instance

    Returns:
        float: gini score

    """
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    n = model.num_agents
    b = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
    return 1 + (1 / n) - 2 * b


class BoltzmannWealth(mesa.Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, seed=None, n=100, width=10, height=10):
        """Initializes the model.

        Args:
            seed: the seed for random number generator
            n: the number of agents
            width: the width of the grid
            height: the height of the grid
        """
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = spaces.OrthogonalMooreGrid((width, height))
        self.schedule = mesa.time.RandomActivation(self)
        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        # Create agents
        for _ in range(self.num_agents):
            agent = MoneyAgent(self)
            # Add the agent to a random grid cell
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            agent.move_to(self.grid[(x, y)])

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """Run the model for a single step."""
        self.agents.shuffle_do("step")
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        """Run the model for n steps.

        Args:
            n: the number of steps for which to run the model

        """
        for _i in range(n):
            self.step()


class MoneyAgent(mesa.spaces.CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        """Instantiate an agent.

        Args:
            model: a Model instance
        """
        super().__init__(model)
        self.wealth = 1

    def give_money(self):
        cellmates = [agent for agent in self.cell.agents if agent is not self]
        if len(cellmates) > 0:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        """Run the agent for 1 step."""
        self.move_to(self.cell.neighborhood().select_random_cell())
        if self.wealth > 0:
            self.give_money()


if __name__ == "__main__":
    model = BoltzmannWealth()
    for _ in range(10):
        model.step()
