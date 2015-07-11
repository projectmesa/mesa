'''
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.

TODO: Implement grass
'''

import random

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from RandomWalk import RandomWalker


class WolfSheepPredation(Model):
    '''
    Wolf-Sheep Predation Model
    '''

    initial_sheep = 100
    initial_wolves = 50
    sheep_gain_from_food = 4

    grass = False

    wolf_gain_from_food = 20
    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    height = 20
    width = 20

    def __init__(self, height=20, width=20,
                 initial_sheep=100, initial_wolves=50, sheep_reproduce=0.04,
                 wolf_reproduce=0.05, wolf_gain_from_food=20,
                 grass=False, sheep_gain_from_food=4):
        '''
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        '''

        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.sheep_gain_from_food = sheep_gain_from_food

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)

        # Create sheep:
        for i in range(self.initial_sheep):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            sheep = Sheep(self.grid, (x, y), True)
            self.grid.place_agent(sheep, (x, y))
            self.schedule.add(sheep)

        # Create wolves
        for i in range(self.initial_wolves):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            energy = random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.grid, (x, y), True, energy)
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)

        self.running = True

    def step(self):
        self.schedule.step()


class Sheep(RandomWalker, Agent):
    '''
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    '''

    def step(self, model):
        '''
        A model step. Move, then eat grass and reproduce.
        '''
        self.random_move()
        if random.random() < model.sheep_reproduce:
            # Create a new sheep:
            x, y = self.pos
            lamb = Sheep(self.grid, self.pos, self.moore)
            model.grid[y][x].add(lamb)
            model.schedule.add(lamb)


class Wolf(RandomWalker, Agent):
    '''
    A wolf that walks around, reproduces (asexually) and eats sheep.
    '''

    energy = None

    def __init__(self, grid, pos, moore, energy):
        super().__init__(grid, pos, moore)
        self.energy = energy

    def step(self, model):
        self.random_move()
        self.energy -= 1

        # If there are sheep present, eat one
        x, y = self.pos
        this_cell = model.grid[y][x]
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = random.choice(sheep)
            self.energy += model.wolf_gain_from_food

            # Kill the sheep
            model.grid[y][x].remove(sheep_to_eat)
            model.schedule.remove(sheep_to_eat)

        # Reproduction:
        if random.random() < model.wolf_reproduce:
            # Create a new wolf cub
            cub = Wolf(self.grid, self.pos, self.moore, self.energy / 2)
            self.energy = self.energy / 2
            model.grid[y][x].add(cub)
            model.schedule.add(cub)
