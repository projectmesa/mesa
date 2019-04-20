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

        Notes:
            If an attribute is not JSON-serializable, it is replaced by its
            string representation unless `filter` is set to True.
        """

        attributes = json.loads(
            json.dumps(
                self.__dict__, default=lambda a: "__REMOVE_ATR" if filter else str(a)
            )
        )

        if filter:
            attributes = {
                key: value
                for key, value in attributes.items()
                if value != "__REMOVE_ATR" and not key.startswith("_")
            }

        properties = {
            key: getattr(self, key)
            for key, value in type(self).__dict__.items()
            if type(value) == property
        }

        agent_json = json.dumps({**attributes, **properties})

        return agent_json
