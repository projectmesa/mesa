# -*- coding: utf-8 -*-
"""
The model class for Mesa framework.

Core Objects: Model

"""
import datetime as dt
import random
import numpy


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
        # seed both the numpy and Python random number generators
        if seed is None:
            self.seed = dt.datetime.now()
        else:
            self.seed = seed
        random.seed(seed)
        numpy.random.seed(seed)

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
