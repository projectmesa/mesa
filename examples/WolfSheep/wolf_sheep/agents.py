import random

from mesa import Agent

from wolf_sheep.random_walk import RandomWalker


class Sheep(RandomWalker):
    '''
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    '''

    energy = None

    def __init__(self, grid, pos, moore, energy=None):
        super().__init__(grid, pos, moore)
        self.energy = energy

    def step(self, model):
        '''
        A model step. Move, then eat grass and reproduce.
        '''
        self.random_move()
        living = True

        if model.grass:
            # Reduce energy
            self.energy -= 1

            # If there is grass available, eat it
            this_cell = model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell
                           if isinstance(obj, GrassPatch)][0]
            if grass_patch.fully_grown:
                self.energy += model.sheep_gain_from_food
                grass_patch.fully_grown = False

            # Death
            if self.energy < 0:
                model.grid._remove_agent(self.pos, self)
                model.schedule.remove(self)
                living = False

        if living and random.random() < model.sheep_reproduce:
            # Create a new sheep:
            if model.grass:
                self.energy /= 2
            lamb = Sheep(self.grid, self.pos, self.moore, self.energy)
            model.grid.place_agent(lamb, self.pos)
            model.schedule.add(lamb)


class Wolf(RandomWalker):
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
        this_cell = model.grid.get_cell_list_contents([self.pos])
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = random.choice(sheep)
            self.energy += model.wolf_gain_from_food

            # Kill the sheep
            model.grid._remove_agent(self.pos, sheep_to_eat)
            model.schedule.remove(sheep_to_eat)

        # Death or reproduction
        if self.energy < 0:
            model.grid._remove_agent(self.pos, self)
            model.schedule.remove(self)
        else:
            if random.random() < model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(self.grid, self.pos, self.moore, self.energy)
                model.grid.place_agent(cub, cub.pos)
                model.schedule.add(cub)


class GrassPatch(Agent):
    '''
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    '''

    def __init__(self, fully_grown, countdown):
        '''
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        '''
        self.fully_grown = fully_grown
        self.countdown = countdown

    def step(self, model):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = model.grass_regrowth_time
            else:
                self.countdown -= 1
