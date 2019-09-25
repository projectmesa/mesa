from mesa import Agent


class Cell(Agent):
    '''Represents a single ALIVE or DEAD cell in the simulation.'''

    DEAD = 0
    ALIVE = 1

    def __init__(self, pos, model, init_state=DEAD):
        '''
        Create a cell, in the given state, at the given x, y position.
        '''
        super().__init__(pos, model)
        self.x, self.y = pos
        self.state = init_state
        self._nextState = None
        self.isConsidered = False

    @property
    def isAlive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y))

    @property
    def considered(self):
        return self.isConsidered is True

    def step(self):
        '''
        Compute if the cell will be dead or alive at the next tick. A dead
        cell will become alive if it has only one neighbor. The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        When a cell is made alive, its neighbors are able to be considered in the next step. Only cells that are considered check their neighbors for performance reasons.
        '''
        # assume no state change
        self._nextState = self.state

        if not self.isAlive and self.isConsidered:
            # Get the neighbors and apply the rules on whether to be alive or dead
            # at the next tick.
            live_neighbors = sum(
                neighbor.isAlive for neighbor in self.neighbors)

            if live_neighbors == 1:
                self._nextState = self.ALIVE
                for a in self.neighbors:
                    a.isConsidered = True

    def advance(self):
        '''
        Set the state to the new computed state -- computed in step().
        '''
        self.state = self._nextState
