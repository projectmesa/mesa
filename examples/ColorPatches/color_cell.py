"""
Subclassing Agent to represent a cell
"""


from collections import Counter
import random

from mesa import Agent



class ColorCell(Agent):
    '''
    Represents a cell's opinion (visualized by a color)
    '''

    OPINIONS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


    def __init__(self, pos, model, initial_state):
        '''
        Create a cell, in the given state, at the given row, col position.
        '''
        Agent.__init__(self, pos, model)
        self._row = pos[1]
        self._col = pos[0]
        self._state = initial_state
        self._next_state = None

    def get_col(self):
        '''Return the col location of this cell.'''
        return self._col

    def get_row(self):
        '''Return the row location of this cell.'''
        return self._row

    def get_state(self):
        '''Return the current state (OPINION) of this cell.'''
        return self._state

    def step(self, model):
        '''
        Determines the agent opinion for the next step by polling its neighbors
        The opinion is determined by the majority of the 8 neighbors' opinion
        A choice is made at random in case of a tie
        The next state is stored until all cells have been polled
        '''
        neighbors_opinion = Counter(n.get_state() \
                            for n in model.grid.neighbor_iter((self._col, self._row), True))
        polled_opinions = neighbors_opinion.most_common()  #a tuple (attribute, occurrences)
        tied_opinions = []
        for neighbor in polled_opinions:
            if neighbor[1] == polled_opinions[0][1]:
                tied_opinions.append(neighbor)

        self._next_state = random.choice(tied_opinions)[0]


    # model argument is unused
    def advance(self, model):
        '''
        Set the state of the agent to the next state
        '''
        self._state = self._next_state

