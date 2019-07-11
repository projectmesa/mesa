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

        Args:
            filter: Whether to filter out unserializable objects and private attributes

        Returns:
            string representation of attributes and properties

        Notes:
            If an attribute is not JSON-serializable, it is replaced by its
            string representation unless `filter` is set to True.

            The JSON representation also includes attributes of base classes, but
            properties of base classes are currently not supported.
        """

        attributes = json.dumps(self.__dict__, default=lambda a: str(a))
        return attributes
