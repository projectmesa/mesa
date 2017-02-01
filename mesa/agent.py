# -*- coding: utf-8 -*-
"""
The agent class for Mesa framework.

Core Objects: Agent

"""


class Agent:
    """ Base class for a model agent. """
    def __init__(self, unique_id, model):
        """ Create a new agent. """
        self.unique_id = unique_id
        self.model = model

    def step(self):
        """ A single step of the agent. """
        pass
