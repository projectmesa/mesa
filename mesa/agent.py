# -*- coding: utf-8 -*-
"""
The agent class for Mesa framework.

Core Objects: Agent

"""
import json


class Agent:
    """ Base class for a model agent. """

    def __init__(self, unique_id, model):
        """ Create a new agent. """
        self.unique_id = unique_id
        self.model = model

    def step(self):
        """ A single step of the agent. """
        pass

    @property
    def random(self):
        return self.model.random

    def as_json(self, filter: bool = True) -> str:
        """Convert Agent attributes to JSON string.

        Returns:
            string representation of attributes and properties

        Notes:
            If an attribute is not JSON-serializable, it is replaced by its
            string representation.

            The JSON representation also includes attributes of base classes, but
            properties of base classes are currently not supported.
        """

        attributes_str = json.dumps(self.__dict__, default=lambda a: str(a))

        properties = {
            key: getattr(self, key)
            for key, value in type(self).__dict__.items()
            if type(value) == property
        }

        properties_str = json.dumps(properties, default=lambda a: str(a))

        agent_json = attributes_str[:-1] + ", " + properties_str[1:]

        return agent_json
