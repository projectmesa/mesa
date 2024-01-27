
import random
from numpy.random import default_rng
from typing import Any

class RNG():
    def __new__(cls, *args: Any, **kwargs: Any):
        seed = kwargs.get("seed")

        # return singleton
        if seed is None:
            if not hasattr(cls, 'instances'):
                cls.instance = super(RNG, cls).__new__(cls)
            return cls.instance
        else:
            super(RNG, cls).__new__(cls)

    def from_seed(self, seed):
    def __init__(self, seed=None) -> None:
        self.random = random.Random(seed=seed)
        self.np_random = default_rng(seed=seed)



        # RNG() should just return the same as model.random
        # RNG(seed=42) should return a new random.Random(seed=seed)
        # how to intercept calls so they get redirected