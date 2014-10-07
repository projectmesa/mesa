'''
Generalized behavior for random walking, one grid cell at a time.
'''

import random

class RandomWalker(object):
    '''
    Class implementing random walker methods in a relatively generalized manner.

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
        self.x = x
        self.y = y
        self.moore = moore

    def random_move(self):
        '''
        Step one cell in any allowable direction.
        '''

        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])

        # If Von-Neumann Movement:
        if not self.moore:
            if random.random() < 0.5:
                dx = 0
            else:
                dy = 0

        # Pick the next cell, handling edges:
        try:
            new_x = self.grid._get_x(self.x + dx)
        except:
            new_x = 0

        try:
            new_y = self.grid._get_y(self.y + dy)
        except:
            new_y = 0

        # Now move:
        self.grid[self.y][self.x].remove(self)
        self.grid[new_y][new_x].add(self)
        self.x = new_x
        self.y = new_y
        












