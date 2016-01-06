from mesa import Model, Agent

class CGoLCell(Agent):
    '''Represents a single ALIVE or DEAD cell in the simulation.'''

    DEAD = 0
    ALIVE = 1

    def __init__(self, pos, model, init_state):
        '''
        Create a cell, in the given state, at the given x, y position.
        '''
        Agent.__init__(self, pos, model)
        self._x = pos[0]
        self._y = pos[1]
        self._state = init_state
        self._nextState = None

    def getX(self):
        '''Return the x location of this cell.'''
        return self._x
    def getY(self):
        '''Return the y location of this cell.'''
        return self._y
    def getState(self):
        '''Return the current state (ALIVE or DEAD) of this cell.'''
        return self._state

    def step(self, model):
        '''
        Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState.
        '''

        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        live_neighbors = 0
        for n in model.grid.neighbor_iter( (self._x, self._y), True):  # all 8 neighbors
            if n.getState() == CGoLCell.ALIVE:
                live_neighbors += 1

        # Assume nextState is unchanged, unless changed below.
        self._nextState = self._state
        if self._state == CGoLCell.DEAD:
            if live_neighbors == 3:
                self._nextState = CGoLCell.ALIVE
        else:  # for when I am alive.
            if live_neighbors < 2 or live_neighbors > 3:
                self._nextState = CGoLCell.DEAD

        # NOTE: we don't change our _state in this method because we need to
        # iterate over all cells, checking their neighbors' _states before
        # we change any of them.
        

    def advance(self, model):
        '''
        Set the state to the new computed state -- computed in step().
        '''
        self._state = self._nextState
    
