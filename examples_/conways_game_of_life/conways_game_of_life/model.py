from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid

from .cell import Cell


class ConwaysGameOfLife(Model):
    '''
    Represents the 2-dimensional array of cells in Conway's
    Game of Life.
    '''

    def __init__(self, height=50, width=50):
        '''
        Create a new playing area of (height, width) cells.
        '''

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=True)

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for (contents, x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self)
            if self.random.random() < 0.1:
                cell.state = cell.ALIVE
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

        self.running = True

    def step(self):
        '''
        Have the scheduler advance each cell by one step
        '''
        self.schedule.step()
