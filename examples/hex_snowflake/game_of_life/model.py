from random import random

from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import HexGrid

from game_of_life.cell import Cell


class GameOfLife(Model):
    '''
    Represents the hex grid of cells. The grid is represented by a 2-dimensional array of cells with adjacency rules specific to hexagons.
    '''

    def __init__(self, height, width):
        '''
        Create a new playing area of (height, width) cells.
        '''

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a hexagonal grid, where edges wrap around.
        self.grid = HexGrid(height, width, torus=True)

        # Place a dead cell at each location.
        for (contents, x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self)
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

        #activate the center(ish) cell.
        self.grid[width // 2][height // 2].state = 1

        self.running = True

    def step(self):
        '''
        Have the scheduler advance each cell by one step
        '''
        self.schedule.step()
