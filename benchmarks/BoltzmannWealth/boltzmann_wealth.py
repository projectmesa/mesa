# noqa D100
# https://github.com/projectmesa/mesa-examples/blob/main/examples/boltzmann_wealth_model_experimental/model.py
from __future__ import annotations

import mesa
from mesa.experimental.signals import (
    Computable,
    Computed,
    HasObservables,
    Observable,
)


def compute_gini(model):  # noqa D103
    agent_wealth = model.agent_wealth.get()
    x = sorted(agent_wealth)
    n = len(agent_wealth)
    b = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
    return 1 + (1 / n) - 2 * b


def get_agent_wealth(model):  # noqa D103
    return [agent.wealth for agent in model.agents]


class Collector:
    def __init__(self, model, obj, attr):
        self.data = []
        self.obj = obj
        self.attr = attr
        self.model = model

    def collect(self):
        self.data.append(getattr(self.obj, self.attr))


class Table:
    def __init__(self, model: BoltzmannWealth):
        self.data = {}
        for agent in model.agents:
            agent.observe("wealth", "on_change", self.update)
            self.data[agent.unique_id] = agent.wealth

    def update(self, signal):
        self.data[signal.owner.unique_id] = signal.new_value

    def get(self):
        return self.data.values()


class BoltzmannWealth(mesa.Model, HasObservables):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    gini = Computable()

    def __init__(self, seed=None, n=100, width=10, height=10):  # noqa D103
        super().__init__(seed)
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_gini})
        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # testing a chain of observable --> computable --> computable
        # we cannot pass model.agent_wealth as an argument
        # to self.gini, because the autodiscovery is tied to Observable.__get__
        # which thus needs! to be accessed inside the callable
        self.agent_wealth = Table(self)
        self.gini = Computed(compute_gini, self)

        self.running = True
        self.datacollector = [
            Collector(self, self, "gini"),
            Collector(self, self, "agent_wealth"),
        ]

    def step(self):  # noqa D103
        self.agents.shuffle_do("step")  # collect data
        for c in self.datacollector:
            c.collect()

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
