import mesa
from agents import MoneyAgent

class BoltzmannWealthModel(mesa.Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, N=100, width=10, height=10):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": self.compute_gini},
            agent_reporters={"Wealth": "wealth"}
        )
        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

    def compute_gini(self):
        agent_wealths = [agent.wealth for agent in self.agents]
        x = sorted(agent_wealths)
        N = self.num_agents
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
        return 1 + (1 / N) - 2 * B
