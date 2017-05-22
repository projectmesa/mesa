import random
from mesa.EvoAgent import *

from wolf_sheep.random_walk import RandomWalker


class Sheep(RandomWalker):
    '''
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    '''

    energy = None

    def __init__(self, unique_id, model, **kwargs):
        super().__init__(unique_id, model, **kwargs)

    def step(self):
        '''
        A model step. Move, then eat grass and reproduce.
        '''
        self.random_move()

        if self.model.grass:
            # Reduce energy
            self.consume_energy()

            # If there is grass available, eat it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell
                           if isinstance(obj, GrassPatch)][0]
            if grass_patch.fully_grown:
                self.gain_energy(self.gain_from_food)
                grass_patch.fully_grown = False

    def duplicate(self):
        dup=super().duplicate()
        dup.gain_from_food=self.gain_from_food
        return dup

class Wolf(RandomWalker):
    '''
    A wolf that walks around, reproduces (asexually) and eats sheep.
    '''

    energy = None

    def __init__(self, unique_id, model, **kwargs):
        super().__init__(unique_id, model, **kwargs)

    def step(self):
        self.random_move()
        self.consume_energy()

        # If there are sheep present, eat one
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = random.choice(sheep)
            self.gain_energy(self.gain_from_food)
            sheep_to_eat.kill()

    def duplicate(self):
        dup=super().duplicate()
        dup.gain_from_food=self.gain_from_food
        return dup

class GrassPatch(Agent):
    '''
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    '''

    def __init__(self, pos, model, fully_grown, countdown):
        '''
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        '''
        super().__init__(pos, model)
        self.fully_grown = fully_grown
        self.countdown = countdown

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
