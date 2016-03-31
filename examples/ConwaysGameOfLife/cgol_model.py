from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
from cgol_cell import CGoLCell
import random



class CGoLModel(Model):
    '''
    Represents the 2-dimensional array of cells in Conway's
    Game of Life.
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

        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=True)

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for (contents, x, y) in self.grid.coord_iter():
            pos = (x, y)
            init_state = CGoLCell.DEAD
            # Initially, make 10% of the cells ALIVE.
            if random.random() < 0.1:
                init_state = CGoLCell.ALIVE
            cell = CGoLCell(pos, self, init_state)
            # Put this cell in the grid at position (x, y)
            self.grid.place_agent(cell, pos)
            # Add this cell to the scheduler.
            self.schedule.add(cell)
        self.running = True

    def step(self):
        '''
        Advance the model by one step.
        '''
        self.schedule.step()

