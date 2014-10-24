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
from mesa.time import Random_Activation

from RandomWalk import RandomWalker

class WolfSheepPredation(Model):
    '''
    Wolf-Sheep Predation Model
    '''

    initial_sheep = 100
    initial_wolves = 50
    sheep_gain_from_food = 4
    wolf_gain_from_food = 20
    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    height = 20
    width = 20

    def __init__(self):
        '''
        Create a new Wolf-Sheep model with the given parameters.
        '''
        #TODO: Accept all other parameters
        
        self.schedule = Random_Activation(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)

        # Create sheep:
        for i in range(self.initial_sheep):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            sheep = Sheep(self.grid, x,  y, True)
            self.grid[y][x].add(sheep)
            self.schedule.add(sheep)

        # Create wolves
        for i in range(self.initial_wolves):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            energy = random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.grid, x,  y, True, energy)
            self.grid[y][x].add(wolf)
            self.schedule.add(wolf)

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
            lamb = Sheep(self.grid, self.x, self.y, self.moore)
            model.grid[self.y][self.x].add(lamb)
            model.schedule.add(lamb)


class Wolf(RandomWalker, Agent):
    '''
    A wolf that walks around, reproduces (asexually) and eats sheep.
    '''

    energy = None

    def __init__(self, grid, x, y, moore, energy):
        super().__init__(grid, x, y, moore)
        self.energy = energy


    def step(self, model):
        self.random_move()
        self.energy -= 1

        # If there are sheep present, eat one
        this_cell = model.grid[self.y][self.x]
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = random.choice(sheep)
            self.energy += model.wolf_gain_from_food

            # Kill the sheep
            model.grid[self.y][self.x].remove(sheep_to_eat)
            model.schedule.remove(sheep_to_eat)

        # Reproduction:
        if random.random() < model.wolf_reproduce:
            # Create a new wolf cub
            cub = Wolf(self.grid, self.x, self.y, self.moore, self.energy/2)
            self.energy = self.energy/2
            model.grid[self.y][self.x].add(cub)
            model.schedule.add(cub)









