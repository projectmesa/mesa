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
from collections import defaultdict

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from RandomWalk import RandomWalker


class WolfSheepPredation(Model):
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

    verbose = False # Print-monitoring

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

        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time
        self.sheep_gain_from_food = sheep_gain_from_food

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {"Wolves": lambda m: m.schedule.get_breed_count(Wolf),
            "Sheep": lambda m: m.schedule.get_breed_count(Sheep)})

        # Create sheep:
        for i in range(self.initial_sheep):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            energy = random.randrange(2 * self.sheep_gain_from_food)
            sheep = Sheep(self.grid, (x, y), True, energy)
            self.grid.place_agent(sheep, (x, y))
            self.schedule.add(sheep)

        # Create wolves
        for i in range(self.initial_wolves):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            energy = random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.grid, (x, y), True, energy)
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)

        # Create grass patches
        if self.grass:
            for agent, x, y in self.grid.coord_iter():

                fully_grown = random.choice([True, False])

                if fully_grown:
                    countdown = self.grass_regrowth_time
                else:
                    countdown = random.randrange(self.grass_regrowth_time)

                patch = GrassPatch(fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        self.running = True

    def step(self):
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

class Sheep(RandomWalker, Agent):
    '''
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    '''

    energy = None

    def __init__(self, grid, pos, moore, energy=None):
        super().__init__(grid, pos, moore)
        self.energy = energy

    def step(self, model):
        '''
        A model step. Move, then eat grass and reproduce.
        '''
        self.random_move()
        living = True

        if model.grass:
            # Reduce energy
            self.energy -= 1

            # If there is grass available, eat it
            this_cell = model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell 
                           if isinstance(obj, GrassPatch)][0]
            if grass_patch.fully_grown:
                self.energy += model.sheep_gain_from_food
                grass_patch.fully_grown = False

            # Death
            if self.energy < 0:
                model.grid._remove_agent(self.pos, self)
                model.schedule.remove(self)
                living = False

        if living and random.random() < model.sheep_reproduce:
            # Create a new sheep:
            if model.grass:
                self.energy /= 2
            lamb = Sheep(self.grid, self.pos, self.moore, self.energy)
            model.grid.place_agent(lamb, self.pos)
            model.schedule.add(lamb)


class Wolf(RandomWalker, Agent):
    '''
    A wolf that walks around, reproduces (asexually) and eats sheep.
    '''

    energy = None

    def __init__(self, grid, pos, moore, energy):
        super().__init__(grid, pos, moore)
        self.energy = energy

    def step(self, model):
        self.random_move()
        self.energy -= 1

        # If there are sheep present, eat one
        x, y = self.pos
        this_cell = model.grid.get_cell_list_contents([self.pos])
        sheep = [obj for obj in this_cell if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = random.choice(sheep)
            self.energy += model.wolf_gain_from_food

            # Kill the sheep
            model.grid._remove_agent(self.pos, sheep_to_eat)
            model.schedule.remove(sheep_to_eat)

        # Death or reproduction
        if self.energy < 0:
            model.grid._remove_agent(self.pos, self)
            model.schedule.remove(self)
        else:
            if random.random() < model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(self.grid, self.pos, self.moore, self.energy)
                model.grid.place_agent(cub, cub.pos)
                model.schedule.add(cub)


class GrassPatch(Agent):
    '''
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    '''

    def __init__(self, fully_grown, countdown):
        '''
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        '''
        self.fully_grown = fully_grown
        self.countdown = countdown

    def step(self, model):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = model.grass_regrowth_time
            else:
                self.countdown -= 1


class RandomActivationByBreed(RandomActivation):
    '''
    A scheduler which activates each type of agent once per step, in random 
    order, with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step(model) method.
    '''
    agents_by_breed = defaultdict(list)

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_breed = defaultdict(list)

    def add(self, agent):
        '''
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        '''

        self.agents.append(agent)
        agent_class = type(agent)
        self.agents_by_breed[agent_class].append(agent)

    def remove(self, agent):
        '''
        Remove all instances of a given agent from the schedule.
        '''

        while agent in self.agents:
            self.agents.remove(agent)

        agent_class = type(agent)
        while agent in self.agents_by_breed[agent_class]:
            self.agents_by_breed[agent_class].remove(agent)

    def step(self, by_breed=True):
        '''
        Executes the step of each agent breed, one at a time, in random order.

        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        '''
        if by_breed:
            for agent_class in  self.agents_by_breed:
                self.step_breed(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_breed(self, breed):
        '''
        Shuffle order and run all agents of a given breed.

        Args:
            breed: Class object of the breed to run.
        '''
        agents = self.agents_by_breed[breed]
        random.shuffle(agents)
        for agent in agents:
            agent.step(self.model)

    def get_breed_count(self, breed_class):
        '''
        Returns the current number of agents of certain breed in the queue.
        '''
        return len(self.agents_by_breed[breed_class])
