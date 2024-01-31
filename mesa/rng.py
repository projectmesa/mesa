import random
from numbers import Number

import numpy.random as np_random

_rng = None


def get_default_rng():
    """get the default random number generator"""
    global _rng
    if _rng is None:
        _rng = random.Random()
        # raise ValueError("random number generator not initialized")
    return _rng


def set_default_rng(seed):
    """Set the default random number generation

    Args:
         seed (int): value with which to seed the random number generator

    """

    global _rng
    _rng = random.Random(seed)


class RandomDescriptor:
    # solve the problem through a descriptor

    def __set__(self, instance, value):
        # check if value is instance of Random
        # or number
        if value is None:
            value = get_default_rng()
        elif isinstance(value, Number):
            value = random.Random(value)
        elif (not isinstance(value, random.Random)) and (
            not isinstance(value, np_random.Generator)
        ):
            raise ValueError("some descriptive text")
        setattr(instance, self.private_name, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
