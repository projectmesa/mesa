'''
Generalized behavior for random walking, one grid cell at a time.
'''

import random


class RandomWalker(object):
    '''
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    '''

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, grid, x, y, moore=True):
        '''
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        '''
        self.grid = grid
        self.pos = (x, y)
        self.moore = moore

    def random_move(self):
        '''
        Step one cell in any allowable direction.
        '''
        x, y = self.pos
        # Pick the next cell from the adjacent cells.
        next_moves = self.grid.get_neighborhood(x, y, self.moore, True)
        next_move = random.choice(next_moves)
        # Now move:
        self.grid._remove_agent(self.pos, self)
        self.grid._place_agent(next_move, self)
        self.pos = next_move
