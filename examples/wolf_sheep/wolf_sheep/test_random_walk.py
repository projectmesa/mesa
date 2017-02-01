'''
Testing the RandomWalker by having an ABM composed only of random walker
agents.
'''

import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.TextVisualization import TextVisualization, TextGrid

from random_walk import RandomWalker


class WalkerAgent(RandomWalker):
    '''
    Agent which only walks around.
    '''

    def step(self):
        self.random_move()


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

        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.agent_count):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            a = WalkerAgent((x, y), self, True)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()


class WalkerWorldViz(TextVisualization):
    '''
    ASCII Visualization for a WalkerWorld agent.
    Each cell is displayed as the number of agents currently in that cell.
    '''

    def __init__(self, model):
        '''
        Create a new visualization for a WalkerWorld instance.

        args:
            model: An instance of a WalkerWorld model.
        '''
        self.model = model
        grid_viz = TextGrid(self.model.grid, None)
        grid_viz.converter = lambda x: str(len(x))
        self.elements = [grid_viz]


if __name__ == "__main__":
    print("Testing 10x10 world, with 50 random walkers, for 10 steps.")
    model = WalkerWorld(10, 10, 50)
    viz = WalkerWorldViz(model)
    for i in range(10):
        print("Step:", str(i))
        viz.step()
