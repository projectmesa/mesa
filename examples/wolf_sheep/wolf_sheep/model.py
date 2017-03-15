'''
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
'''

import random

from mesa.EvoModel import *
from mesa.SelectionModel import *
from mesa.ReproductionModel import *
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from wolf_sheep.agents import Sheep, Wolf, GrassPatch
from wolf_sheep.schedule import RandomActivationByBreed


class WolfSheepPredation(EvoModel):
    '''
    Wolf-Sheep Predation Model
    '''

    height = 20
    width = 20

    initial_sheep = 100
    initial_wolves = 50

    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    wolf_gain_from_food = 20

    grass = False
    grass_regrowth_time = 30
    sheep_gain_from_food = 4

    verbose = False  # Print-monitoring

    def __init__(self, height=20, width=20,
                 initial_sheep=100, initial_wolves=50,
                 sheep_reproduce=0.04, wolf_reproduce=0.05,
                 wolf_gain_from_food=20,
                 grass=False, grass_regrowth_time=30, sheep_gain_from_food=4):
        '''
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        '''

        r=AsexualReproduction()
        s=ProbabilisticSelection(r)
        super().__init__([[Sheep,initial_sheep,{"moore":True,"repr_p":sheep_reproduce,"die_p":0.0,"gain":sheep_gain_from_food}],
                          [Wolf,initial_wolves,{"moore":True,"repr_p":wolf_reproduce,"die_p":0.0,"gain":wolf_gain_from_food}]],s,RandomActivationByBreed)
        # Set parameters
        self.height = height
        self.width = width
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time

        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {"Wolves": lambda m: m.schedule.get_breed_count(Wolf),
             "Sheep": lambda m: m.schedule.get_breed_count(Sheep)})

        for a in self.schedule.agents:
            self.grid.place_agent(a, (a.pos[0], a.pos[1]))

        # Create grass patches
        if self.grass:
            for agent, x, y in self.grid.coord_iter():

                fully_grown = random.choice([True, False])

                if fully_grown:
                    countdown = self.grass_regrowth_time
                else:
                    countdown = random.randrange(self.grass_regrowth_time)

                patch = GrassPatch((x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        self.running = True

    def step(self):
        self.update_population()
        for i in self.sel_f.deaths:
            self.grid._remove_agent(i.pos, i)
        for i in self.sel_f.offsprings:
            self.grid.place_agent(i,i.pos)
        self.schedule.step()
        self.datacollector.collect(self)
        if self.verbose:
            print([self.schedule.time,
                   self.schedule.get_breed_count(Wolf),
                   self.schedule.get_breed_count(Sheep)])

    def run_model(self, step_count=200):

        if self.verbose:
            print('Initial number wolves: ',
                  self.schedule.get_breed_count(Wolf))
            print('Initial number sheep: ',
                  self.schedule.get_breed_count(Sheep))

        for i in range(step_count):
            self.step()

        if self.verbose:
            print('')
            print('Final number wolves: ',
                  self.schedule.get_breed_count(Wolf))
            print('Final number sheep: ',
                  self.schedule.get_breed_count(Sheep))
