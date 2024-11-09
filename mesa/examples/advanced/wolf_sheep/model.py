"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa
from mesa.examples.advanced.wolf_sheep.agents import GrassPatch, Sheep, Wolf
from mesa.experimental.cell_space import OrthogonalMooreGrid


class WolfSheep(mesa.Model):
    """
    Wolf-Sheep Predation Model
    """

    height = 20
    width = 20

    initial_sheep = 100
    initial_wolves = 50

    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    wolf_gain_from_food = 20

    grass = False
    grass_regrowth_time = 30
    sheep_gain_from_food = 4

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        simulator=None,
        width=20,
        height=20,
        initial_sheep=100,
        initial_wolves=50,
        sheep_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass=False,
        grass_regrowth_time=30,
        sheep_gain_from_food=4,
        seed=None,
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            simulator: a Simulator instance
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        """
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)

        # Set parameters
        self.width = width
        self.height = height
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time

        self.grid = OrthogonalMooreGrid(
            (self.width, self.height), torus=True, random=self.random
        )

        collectors = {
            "Wolves": lambda m: len(m.agents_by_type[Wolf]),
            "Sheep": lambda m: len(m.agents_by_type[Sheep]),
            "Grass": lambda m: len(
                m.agents_by_type[GrassPatch].select(lambda a: a.fully_grown)
            )
            if m.grass
            else -1,
        }

        self.datacollector = mesa.DataCollector(collectors)

        # Create sheep:
        for _ in range(self.initial_sheep):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.sheep_gain_from_food)
            Sheep(
                self, energy, sheep_reproduce, sheep_gain_from_food, self.grid[(x, y)]
            )

        # Create wolves
        for _ in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.wolf_gain_from_food)
            Wolf(self, energy, wolf_reproduce, wolf_gain_from_food, self.grid[(x, y)])

        # Create grass patches
        if self.grass:
            possibly_fully_grown = [True, False]
            for cell in self.grid:
                fully_grown = self.random.choice(possibly_fully_grown)
                countdown = (
                    0
                    if fully_grown
                    else self.random.randrange(0, stop=grass_regrowth_time)
                )
                GrassPatch(self, countdown, grass_regrowth_time, cell)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # This replicated the behavior of the old RandomActivationByType scheduler
        # when using step(shuffle_types=True, shuffle_agents=True).
        # Conceptually, it can be argued that this should be modelled differently.
        agent_types = [Wolf, Sheep]
        self.random.shuffle(agent_types)
        for agent_type in agent_types:
            self.agents_by_type[agent_type].shuffle_do("step")

        # collect data
        self.datacollector.collect(self)
