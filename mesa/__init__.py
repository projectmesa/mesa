# -*- coding: utf-8 -*-
"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.

"""
import datetime as dt
import random

__title__ = 'mesa'
__version__ = '0.7.5'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Project Mesa Team'


class Model:
    """ Base class for models. """
    def __init__(self, seed=None):
        """ Create a new model. Overload this method with the actual code to
        start the model.

        Args:
            seed: seed for the random number generator

        Attributes:
            schedule: schedule object
            running: a bool indicating if the model should continue running

        """
        if seed is None:
            self.seed = dt.datetime.now()
        else:
            self.seed = seed
        random.seed(seed)
        self.running = True
        self.schedule = None

    def run_model(self):
        """ Run the model until the end condition is reached. Overload as
        needed.

        """
        while self.running:
            self.step()

    def step(self):
        """ A single step. Fill in here. """
        pass


class Agent:
    """ Base class for a model agent. """
    def __init__(self, unique_id, model):
        """ Create a new agent. """
        self.unique_id = unique_id
        self.model = model

    def step(self, model):
        """ A single step of the agent. """
        pass
