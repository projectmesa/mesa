"""
Sugarscape {G1}, {M, T} Model
================================

"""

import numpy as np

import mesa

from .agents import SsAgent, Sugar, Spice


def mean(x):
    if len(x) > 0:
        return sum(x) / len(x)
    return 0.0


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def geometric_mean(x):
    return np.exp(np.log(x).mean())


class SugarscapeG1mt(mesa.Model):
    """
    Sugarscape ({G1}, {M, T})
    """

    verbose = True  # Print-monitoring

    def __init__(self, width=50, height=50, initial_population=100, seed=42):
        """
        Create a new Constant Growback model with the given parameters.

        Args:
            initial_population: Number of population to start with
        """

        # Set parameters
        self.width = width
        self.height = height
        self.initial_population = initial_population

        self.schedule = mesa.time.RandomActivationByType(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.datacollector = mesa.DataCollector(
            {
                "SsAgent": lambda m: m.schedule.get_type_count(SsAgent),
                "Trade volume": lambda m: sum(
                    len(a.prices) for a in m.schedule.agents_by_type[SsAgent].values()
                ),
                "Price": lambda m: geometric_mean(
                    flatten(
                        [a.prices for a in m.schedule.agents_by_type[SsAgent].values()]
                    )
                ),
            },
        )

        # Create sugar
        sugar_distribution = np.genfromtxt("sugarscape_g1mt/sugar-map.txt")
        spice_distribution = sugar_distribution.T
        for _, x, y in self.grid.coord_iter():
            max_sugar = sugar_distribution[x, y]
            if max_sugar > 0:
                sugar = Sugar((x, y), self, max_sugar)
                self.grid.place_agent(sugar, (x, y))
                self.schedule.add(sugar)
            # Same, but spice
            max_spice = spice_distribution[x, y]
            if max_spice > 0:
                spice = Spice((x, y), self, max_spice)
                self.grid.place_agent(spice, (x, y))
                self.schedule.add(spice)

        # Create agent:
        for i in range(self.initial_population):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            # See GAS page 108 for parameters initialization.
            # Each agent is endowed by a random amount of sugar and spice
            sugar = self.random.randrange(25, 51)
            spice = self.random.randrange(25, 51)
            # Each agent's phenotype is initialized with random value
            metabolism_sugar = self.random.randrange(1, 3)
            metabolism_spice = self.random.randrange(1, 3)
            vision = self.random.randrange(1, 6)
            ssa = SsAgent(
                (x, y),
                self,
                False,
                sugar,
                spice,
                metabolism_sugar,
                metabolism_spice,
                vision,
            )
            self.grid.place_agent(ssa, (x, y))
            self.schedule.add(ssa)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        for sugar in self.schedule.agents_by_type[Sugar].values():
            sugar.step()
        for spice in self.schedule.agents_by_type[Spice].values():
            spice.step()
        ssAgents = self.schedule.agents_by_type[SsAgent].values()
        for agent in ssAgents:
            agent.move()
        for agent in ssAgents:
            agent.eat()
        for agent in list(ssAgents):
            agent.maybe_die()
        for agent in ssAgents:
            agent.prices = agent.trade_with_neighbors()

        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print([self.schedule.time, self.schedule.get_type_count(SsAgent)])

    def run_model(self, step_count=200):

        if self.verbose:
            print(
                "Initial number Sugarscape Agent: ",
                self.schedule.get_type_count(SsAgent),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Final number Sugarscape Agent: ",
                self.schedule.get_type_count(SsAgent),
            )

            # For plotting purpose TODO remove this.
            # import matplotlib.pyplot as plt
            # plt.plot(self.datacollector.model_vars["Price"])
            # plt.plot(self.datacollector.model_vars["Trade volume"])
