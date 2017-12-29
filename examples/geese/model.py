from mesa import Agent, Model
from mesa.time import SimultaneousActivation, RandomActivation
from mesa.space import MultiGrid

import random

class MoneyAgent(Agent):
    """ An agent with fixed intial wealth """
    def __init__(self, unique_id, model):
        super().__init__(unique_id,model)
        self.wealth = 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()

    def advance(self):
        pass

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore = True,
            include_center = False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice (cellmates)
            other.wealth += 1
            self.wealth -= 1

class MoneyModel(Model):
    """ A model with some number of agents """
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid (width, height, True)
        self.schedule = SimultaneousActivation(self)
        #self.schedule = RandomActivation(self)        
        for i in range(self.num_agents):
            a = MoneyAgent(i, self) 
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))

    def step(self):
        self.schedule.step()


def main():
    empty_model = MoneyModel(10,10,10)
    for i in range(1000):
        empty_model.step()

    for agent in empty_model.schedule.agents:
        print (agent.unique_id,agent.wealth)

if __name__ == '__main__':
    main()