import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector


class TreeCell(Agent):
    '''
    A tree cell.

    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple.

    unique_id isn't strictly necessary here, but it's good
    practice to give one to each agent anyway.
    '''
    def __init__(self, pos):
        '''
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid.
        '''
        self.pos = pos
        self.unique_id = pos
        self.condition = "Fine"

    def step(self, model):
        '''
        If the tree is on fire, spread it to fine trees nearby.
        '''
        if self.condition == "On Fire":
            for neighbor in model.grid.neighbor_iter(self.pos):
                if neighbor.condition == "Fine":
                    neighbor.condition = "On Fire"
            self.condition = "Burned Out"

    def get_pos(self):
        return self.pos


class ForestFire(Model):
    '''
    Simple Forest Fire model.
    '''
    def __init__(self, height, width, density):
        '''
        Create a new forest fire model.

        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        '''
        # Initialize model parameters
        self.height = height
        self.width = width
        self.density = density

        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=False)

        self.datacollector = DataCollector(
            {"Fine": lambda m: self.count_type(m, "Fine"),
             "On Fire": lambda m: self.count_type(m, "On Fire"),
             "Burned Out": lambda m: self.count_type(m, "Burned Out")})

        # Place a tree in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.density:
                # Create a tree
                new_tree = TreeCell((x, y))
                # Set all trees in the first column on fire.
                if x == 0:
                    new_tree.condition = "On Fire"
                self.grid._place_agent((x, y), new_tree)
                self.schedule.add(new_tree)
        self.running = True

    def step(self):
        '''
        Advance the model by one step.
        '''
        self.schedule.step()
        self.datacollector.collect(self)

        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        '''
        Helper method to count trees in a given condition in a given model.
        '''
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
