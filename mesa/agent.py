# -*- coding: utf-8 -*-
"""
The agent class for Mesa framework.

Core Objects: Agent

"""


class Agent:
    """ Base class for a model agent. 

    Properties:
        unique_id: Unique identifer for the agent
        model: Model that the agent is situated in
        pos: Position of the agent in the parameter space (if exists)
    """

    def __init__(self, unique_id, model):
        """ Create a new agent. 

        Args: 
            unique_id: Unique identifer for the agent
            model: Model that the agent is situated in
        """
        self.unique_id = unique_id
        self.model = model
        self.pos = None

    def step(self):
        """ A single step of the agent. """
        pass

    @property
    def random(self):
        return self.model.random
