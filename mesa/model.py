# -*- coding: utf-8 -*-
"""
The model class for Mesa framework.

Core Objects: Model

"""
import time
import random
import json


class Model:
    """ Base class for models. """

    def __new__(cls, *args, **kwargs):
        """Create a new model object and instantiate its RNG automatically."""

        model = object.__new__(cls)  # This only works in Python 3.3 and above
        model._seed = time.time()
        if "seed" in kwargs and kwargs["seed"] is not None:
            model._seed = kwargs["seed"]
        model.random = random.Random(model._seed)
        return model

    def __init__(self, *args, **kwargs):
        """ Create a new model. Overload this method with the actual code to
        start the model.

        Attributes:
            schedule: schedule object
            running: a bool indicating if the model should continue running

        """

        self.running = True
        self.schedule = None
        self.current_id = 0

    def run_model(self):
        """ Run the model until the end condition is reached. Overload as
        needed.

        """
        while self.running:
            self.step()

    def step(self):
        """ A single step. Fill in here. """
        pass

    def next_id(self):
        """ Return the next unique ID for agents, increment current_id"""
        self.current_id += 1
        return self.current_id

    def reset_randomizer(self, seed=None):
        """Reset the model random number generator.

        Args:
            seed: A new seed for the RNG; if None, reset using the current seed
        """

        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed

    def as_json(self, filter: bool = True, include_agents: bool = True) -> str:
        """Convert Model attributes to JSON.

        Args:
            filter: Whether to filter out unserializable objects and private attributes
            include_agents: Whether to include agents

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

        model_json = json.dumps({**attributes, **properties})

        if not include_agents:
            return model_json

        out = '{{"model": {model}, "agents": [{agents}]}}'.format(
            model=model_json,
            agents=",".join(
                [agent.as_json(filter=filter) for agent in self.schedule.agents]
            ),
        )
        return out
