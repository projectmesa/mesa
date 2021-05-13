    
from mesa.space import ContinuousSpace

import random

  
class ElFarolBar(Model,width = 100,height = 100):
    def __init__(self, N=100):
        self.running = True 
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = ContinuousSpace(width, height, False,-width,-height)
        
        
        for i in range(self.num_agents):
            a = BarCostumer(i, self) 
            self.schedule.add(a)
            #self.datacollector = DataCollector(
            #agent_reporters={"Bar": "Bar"})
            x,y = random.uniform(self.grid.x_min,self.grid.x_max)\
            ,random.uniform(self.grid.y_min,self.grid.y_max)
            if x>0 and y>0:
                if random.randint(0,1) ==0:
                    x = -x
                else:
                    y =-y
            grid.place_agent(agent = a,pos = (x,y))

        