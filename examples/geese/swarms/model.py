from mesa import Agent, Model
from mesa.time import SimultaneousActivation, RandomActivation
from mesa.space import MultiGrid
from swarms.agent import SwarmAgent

import random

class EnvironmentModel(Model):
    """ A environemnt to model swarms """
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid (width, height, True)
        self.schedule = SimultaneousActivation(self)
        #self.schedule = RandomActivation(self)  

        for i in range(self.num_agents):
            a = SwarmAgent(i, self) 
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))

    def step(self):
        self.schedule.step()



#if __name__ == '__main__':
#   main()