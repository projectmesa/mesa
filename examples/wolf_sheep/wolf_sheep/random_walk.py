'''
Generalized behavior for random walking, one grid cell at a time.
'''

import random

from mesa.EvoAgent import *


class RandomWalker(EvoAgent):
    '''
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    '''

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id,model,moore=True,gain=1,**kwargs):
        '''
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        '''
        x = random.randrange(model.width)
        y = random.randrange(model.height)
        self.moore = moore
        self.pos = (x,y)
        self.gain_from_food=gain
        energy=random.randrange(2 * self.gain_from_food)
        super().__init__(unique_id, model,energy=energy,**kwargs)

    def random_move(self):
        '''
        Step one cell in any allowable direction.
        '''
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

    def duplicate(self):
        dup=super().duplicate()
        dup.pos=self.pos
        dup.moore=self.moore
        return dup
