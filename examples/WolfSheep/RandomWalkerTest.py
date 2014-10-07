'''
Testing the RandomWalker by having an ABM composed only of random walker agents.
'''

import random

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import Random_Activation

from RandomWalk import RandomWalker

class WalkerWorld(Model):
    '''
    Random walker world.
    '''
    height = 10
    width = 10

    def __init__(self, height, width, agent_count):
        '''
        Create a new WalkerWorld.

        Args:
            height, width: World size.
            agent_count: How many agents to create.
        '''
        self.height = height
        self.width = width
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.agent_count = agent_count

        self.schedule = Random_Activation(self)
        # Create agents
        for i in range(self.agent_count):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            a = WalkerAgent(self.grid, x, y, True)
            self.schedule.add(a)
            self.grid[y][x].add(a)

    def step(self):
        self.schedule.step()


class WalkerAgent(RandomWalker, Agent):
    '''
    Agent which only walks around.
    '''

    def step(self, model):
        self.random_move()




