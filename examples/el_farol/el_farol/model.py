    
from mesa.space import MultiGrid
from mesa import Model
from mesa.time import RandomActivation
from .agent import BarCustomer
import numpy as np


class ElFarolBar(Model):
    def __init__(self, num_strategies=10,memory_size = 10,width = 100,height = 100,N=100):
        self.running = True 
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.attendance = 0
        self.history = np.random.randint(0,100,size = memory_size*2)

        for i in range(self.num_agents):
            
            #self.datacollector = DataCollector(
            #agent_reporters={"Bar": "Bar"})
#            x,y = random.randint(0,self.grid.width-1)\
#            ,random.randint(0,self.grid.height-1)
#            if x>width//2 and y>height//2:
#                if random.randint(0,1) ==0:
#                    x = x-(width//2-1)
#                else:
#                    y =y-(height//2-1)
            a = BarCustomer(i,self, num_strategies,memory_size) 
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            self.grid.place_agent(a,(x,y))

    def step(self):
        self.schedule.step()