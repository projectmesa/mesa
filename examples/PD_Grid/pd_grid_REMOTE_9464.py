'''
Spatial Demographic Prisoner's Dilemma
=========================================

In this model, agents are situated on a grid and play the Prisoner's Dilemma
with all of their neighbors simultaneously; an agent can either be Cooperating
or Defecting.
'''

import random

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid


class PD_Agent(Agent):

    def __init__(self, pos, model, starting_move=None):
        '''
        Create a new Prisoner's Dilemma agent.

        Args:
            pos: (x, y) tuple of the agent's position.
            starting_move: If provided, determines the agent's initial state:
                           C(ooperating) or D(efecting). Otherwise, random.
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.score = 0
        if starting_move:
            self.move = starting_move
        else:
            self.move = random.choice(["C", "D"])
        self.next_move = None

    def step(self):
        '''
        Get the neighbors' moves, and change own move accordingly.
        '''
        neighbors = self.model.grid.get_neighbors(self.pos, True,
                                                  include_center=True)
        best_neighbor = max(neighbors, key=lambda a: a.score)
        self.next_move = best_neighbor.move

        if self.model.schedule_type != "Simultaneous":
            self.advance()

    def advance(self):
        self.move = self.next_move
        self.score += self.increment_score()

    def increment_score(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True)
        if self.model.schedule_type == "Simultaneous":
            moves = [neighbor.next_move for neighbor in neighbors]
        else:
            moves = [neighbor.move for neighbor in neighbors]
        return sum(self.model.payoff[(self.move, move)] for move in moves)


class PD_Model(Model):
    '''
    Model class for iterated, spatial prisoner's dilemma model.
    '''

    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}

    # This dictionary holds the payoff for this agent,
    # keyed on: (my_move, other_move)

    payoff = {("C", "C"): 1,
              ("C", "D"): 0,
              ("D", "C"): 1.6,
              ("D", "D"): 0}

    def __init__(self, height, width, schedule_type, payoffs=None):
        '''
        Create a new Spatial Prisoners' Dilemma Model.

        Args:
            height, width: Grid size. There will be one agent per grid cell.
            schedule_type: Can be "Sequential", "Random", or "Simultaneous".
                           Determines the agent activation regime.
            payoffs: (optional) Dictionary of (move, neighbor_move) payoffs.
        '''
        self.running = True
        self.grid = SingleGrid(height, width, torus=True)
        self.schedule_type = schedule_type
        self.schedule = self.schedule_types[self.schedule_type](self)

        # Create agents
        for x in range(width):
            for y in range(height):
                agent = PD_Agent((x, y), self)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.datacollector = DataCollector({
            "Cooperating_Agents":
            lambda m: len([a for a in m.schedule.agents if a.move == "C"])
        })

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def run(self, n):
        '''
        Run the model for a certain number of steps.
        '''
        for _ in range(n):
            self.step()
