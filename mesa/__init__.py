

# Model

#From schelling
#model.grid.get_neighbors(self.x, self.y, moore=True)
'''
empty
it may or may not have grid
it may have a scheduler; you can probably assume this

Scheduler maintains a list of agents
To kill and agent, you remove it from the scheduler
Then it won't exist. (You have to explicitly)
'''

import datetime as dt
import random

class Model(object):
    '''
    Base class for models.
    '''
    seed = None # Seed for the random number generator
    schedule = None # Schedule object
    running = None

    def __init__(self, seed=None):
        '''
        Create a new model. Overload this method with the actual code to start 
        the model.
        '''
        if seed is None:
            self.seed = dt.now()
        else:
            self.seed = seed
        random.seed(seed)
        self.running = True


    def run_model(self):
        '''
        Run the model until the end condition is reached. Overload as needed.
        '''
        while self.running:
            self.step()


    def step(self):
        '''
        A single step. Fill in here.
        '''
        pass


'''
# Agent
# What do agents have

Attributes:
    unique id
        starting at 1 and counting up

step()
    do this when you are activated
    this is a tick

__init__()
    set the unique id
'''

class Agent(object):
    '''
    Base class for a model agent.
    '''

    model = None
    unique_id = None

    def __init__(self, unique_id, model):
        '''
        Create a new agent.
        '''
        self.model = model

    def step(self, model):
        '''
        A single step of the agent.
        '''
        pass







