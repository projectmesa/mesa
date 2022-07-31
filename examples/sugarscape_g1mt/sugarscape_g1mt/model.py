"""
Sugarscape {G1}, {M, T} Model
================================

"""

import numpy as np

import mesa

from .agents import Trader, Sugar, Spice


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

    def __init__(
        self,
        width=50,
        height=50,
        initial_population=200,
        endowment_min=25,
        endowment_max=50,
        metabolism_min=1,
        metabolism_max=5,
        vision_min=1,
        vision_max=5,
        seed=42,
    ):
        """
        Create a new Constant Growback model with the given parameters.
        Args:
            initial_population: Number of population to start with
        """

        # Set parameters
        self.width = width
        self.height = height
        self.initial_population = initial_population
        self.endowment_min = endowment_min
        self.endowment_max = endowment_max
        self.metabolism_min = metabolism_min
        self.metabolism_max = metabolism_max
        self.vision_min = vision_min
        self.vision_max = vision_max

        self.schedule = mesa.time.RandomActivationByType(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.datacollector = mesa.DataCollector(
            {
                "Trader": lambda m: m.schedule.get_type_count(Trader),
                "Trade volume": lambda m: sum(
                    len(a.prices) for a in m.schedule.agents_by_type[Trader].values()
                ),
                "Price": lambda m: geometric_mean(
                    flatten(
                        [a.prices for a in m.schedule.agents_by_type[Trader].values()]
                    )
                ),
            },
        )

        # Create sugar
        sugar_distribution = np.genfromtxt("sugarscape_g1mt/sugar-map.txt")
        spice_distribution = np.flip(sugar_distribution, 1)
        # ensure each agent has a unique _id
        agent_id = 0
        for _, x, y in self.grid.coord_iter():
            max_sugar = sugar_distribution[x, y]
            if max_sugar > 0:
                sugar = Sugar(agent_id, self, (x, y), max_sugar)
                self.grid.place_agent(sugar, (x, y))
                self.schedule.add(sugar)
                agent_id += 1
            # Same, but spice
            max_spice = spice_distribution[x, y]
            if max_spice > 0:
                spice = Spice(agent_id, self, (x, y), max_spice)
                self.grid.place_agent(spice, (x, y))
                self.schedule.add(spice)
                agent_id += 1

        # Create agent:
        for i in range(self.initial_population):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            # See GAS page 108 for parameters initialization.
            # Each agent is endowed by a random amount of sugar and spice
            sugar = self.random.uniform(self.endowment_min, self.endowment_max + 1)
            spice = self.random.uniform(self.endowment_min, self.endowment_max + 1)
            # Each agent's phenotype is initialized with uniform value
            metabolism_sugar = self.random.uniform(
                self.metabolism_min, self.metabolism_max
            )
            metabolism_spice = self.random.uniform(
                self.metabolism_min, self.metabolism_max
            )
            vision = int(self.random.uniform(self.vision_min, self.vision_max))
            trader = Trader(
                agent_id,
                self,
                (x, y),
                False,
                sugar,
                spice,
                metabolism_sugar,
                metabolism_spice,
                vision,
            )
            self.grid.place_agent(trader, (x, y))
            self.schedule.add(trader)
            agent_id += 1
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        for sugar in self.schedule.agents_by_type[Sugar].values():
            sugar.step()
        for spice in self.schedule.agents_by_type[Spice].values():
            spice.step()
        Traders = self.schedule.agents_by_type[Trader].values()
        Trader_shuffle = list(Traders)
        self.random.shuffle(Trader_shuffle)
        for agent in Trader_shuffle:
            agent.move()
        self.random.shuffle(Trader_shuffle)
        for agent in Trader_shuffle:
            agent.eat()
        for agent in list(Traders):
            agent.maybe_die()
        Trader_shuffle = list(Traders)
        self.random.shuffle(Trader_shuffle)
        for agent in Trader_shuffle:
            agent.prices = agent.trade_with_neighbors()
        self.schedule.steps += 1
        self.schedule.time += 1

        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print([self.schedule.time, self.schedule.get_type_count(Trader)])

    def run_model(self, step_count=1000):

        if self.verbose:
            print(
                "Initial number Sugarscape Agent: ",
                self.schedule.get_type_count(Trader),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Final number Sugarscape Agent: ",
                self.schedule.get_type_count(Trader),
            )

            # For plotting purpose TODO remove this.
            import matplotlib.pyplot as plt

            print(sum(self.datacollector.model_vars["Trade volume"]), "total trade")
            plt.plot(self.datacollector.model_vars["Price"])
            plt.show()
            # print(len([i for i in range(len(self.datacollector.model_vars["Trade volume"]))]))
            plt.bar(
                [i for i in range(len(self.datacollector.model_vars["Trade volume"]))],
                self.datacollector.model_vars["Trade volume"],
            )
            plt.show()
