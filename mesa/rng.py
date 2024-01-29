import numpy.random as np_random
import random

_rng = None

def get_default_rng():
    """get the default random number generator"""
    global _rng
    if _rng is None:
        raise ValueError("random number generator not initialized")
    return _rng


def set_default_rng(seed):
    """Set the default random number generation

    Args:
         seed (int): value with which to seed the random number generator

    """

    global _rng
    _rng = random.Random(seed)


def get_rng(seed=None):
    """get a random number generator. If seed is None, return
    the default random number generator.

    Args:
        seed (int, optional):

    """

    if seed is None:
        return get_default_rng()
    else:
        return random.Random(seed)



from typing import Any, Callable, List, String

class Collector:
    def __init__(self, name : str, obj : Any, attrs: str | List[str], func: Callable = None ):
        ...