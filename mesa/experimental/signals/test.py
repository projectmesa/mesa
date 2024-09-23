# noqa D100
# https://github.com/projectmesa/mesa-examples/blob/main/examples/boltzmann_wealth_model_experimental/model.py
import mesa
from mesa.experimental.signals import (
    Computable,
    HasObservables,
    Observable,
)


def compute_gini(agent_wealth):  # noqa D103
    x = sorted(agent_wealth)
    n = len(agent_wealth)
    b = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
    return 1 + (1 / n) - 2 * b


def get_agent_wealth(model):  # noqa D103
    return [agent.wealth for agent in model.agents]


class BoltzmannWealth(mesa.Model, HasObservables):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    agent_wealth = Computable()
    gini = Computable()

    def __init__(self, seed=None, n=100, width=10, height=10):  # noqa D103
        super().__init__(seed)
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": "gini"}, agent_reporters={"Wealth": "wealth"}
        )
        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # testing a chain of observable --> computable --> computable
        self.agent_wealth = get_agent_wealth(self), self, None  # fixme
        self.gini = compute_gini, self.agent_wealth, None  # fixme

        self.running = True
        self.datacollector.collect(self)

    def step(self):  # noqa D103
        self.agents.shuffle().do("step")
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):  # noqa D103
        for _i in range(n):
            self.step()


class MoneyAgent(mesa.Agent, HasObservables):
    """An agent with fixed initial wealth."""

    wealth = Observable()

    def __init__(self, model):  # noqa D103
        super().__init__(model)
        self.wealth = 1

    def move(self):  # noqa D103
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):  # noqa D103
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(
            cellmates.index(self)
        )  # Ensure agent is not giving money to itself
        if len(cellmates) > 0:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):  # noqa D103
        self.move()
        if self.wealth > 0:
            self.give_money()


if __name__ == "__main__":
    model = BoltzmannWealth()
    model.run_model(10)
