# Use Python 3

# Only collect the number of wolves and sheeps per step.

import timeit
import gc

setup = """
gc.enable()
import os, sys
sys.path.insert(0, os.path.abspath("."))

from Flocking import BoidFlockers

import random
random.seed(42)

def runthemodel(seed, population, width, height, vision):
    flock = BoidFlockers(seed, population, width, height, vision)
    for i in range(0, 100):
      flock.step()

seed = random.randint(1, 10000)
population={}
width={}
height={}
vision={}
"""

n_run = 100

tt = timeit.Timer('runthemodel(seed, population, width, height, vision)', setup=setup.format(200, 100, 100, 5))
a = tt.repeat(n_run, 1)
median_time = sorted(a)[n_run // 2 + n_run % 2]
print("Mesa Flocking-small (ms):", median_time*1e3)

tt = timeit.Timer('runthemodel(seed, population, width, height, vision)', setup=setup.format(400, 150, 150, 15))
a = tt.repeat(n_run, 1)
median_time = sorted(a)[n_run // 2 + n_run % 2]
print("Mesa Flocking-large (ms):", median_time*1e3)
