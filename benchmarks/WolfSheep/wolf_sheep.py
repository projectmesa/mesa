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
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType

from .agents import GrassPatch, Sheep, Wolf


class WolfSheep(mesa.Model):
    """
    Wolf-Sheep Predation Model

    A model for simulating wolf and sheep (predator-prey) ecosystem modelling.
    """

    def __init__(
        self,
        seed,
        height,
        width,
        initial_sheep,
        initial_wolves,
        sheep_reproduce,
        wolf_reproduce,
        grass_regrowth_time,
        wolf_gain_from_food=13,
        sheep_gain_from_food=5,
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
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
        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass_regrowth_time = grass_regrowth_time
        self.sheep_gain_from_food = sheep_gain_from_food

        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)

        # Create sheep:
        for _i in range(self.initial_sheep):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * self.sheep_gain_from_food)
            sheep = Sheep(self.next_id(), pos, self, True, energy)
            self.grid.place_agent(sheep, pos)
            self.schedule.add(sheep)

        # Create wolves
        for _i in range(self.initial_wolves):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.next_id(), pos, self, True, energy)
            self.grid.place_agent(wolf, pos)
            self.schedule.add(wolf)

        # Create grass patches
        possibly_fully_grown = [True, False]
        for _agent, pos in self.grid.coord_iter():
            fully_grown = self.random.choice(possibly_fully_grown)
            if fully_grown:
                countdown = self.grass_regrowth_time
            else:
                countdown = self.random.randrange(self.grass_regrowth_time)
            patch = GrassPatch(self.next_id(), pos, self, fully_grown, countdown)
            self.grid.place_agent(patch, pos)
            self.schedule.add(patch)

    def step(self):
        self.schedule.step()
