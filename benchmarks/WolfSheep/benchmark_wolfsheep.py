# Use Python 3

# Only collect the number of wolves and sheeps per step.

import timeit
import gc

setup = """
gc.enable()
import os, sys
sys.path.insert(0, os.path.abspath("."))

from agents import Sheep, Wolf, GrassPatch
from WolfSheep import WolfSheep

import random
random.seed(42)

def runthemodel(seed, height, width, initial_sheep, initial_wolves, sheep_reproduce, wolf_reproduce, grass_regrowth_time):
    wolfsheep = WolfSheep(seed, height, width, initial_sheep, initial_wolves, sheep_reproduce, wolf_reproduce, grass_regrowth_time)
    for i in range(0, 100):
      wolfsheep.step()

seed = random.randint(1, 10000)
height = {}
width = {}
initial_sheep = {}
initial_wolves = {}
sheep_reproduce = {}
wolf_reproduce = {}
grass_regrowth_time = {}
"""

n_run = 100

tt = timeit.Timer('runthemodel(seed, height, width, initial_sheep, initial_wolves, sheep_reproduce, wolf_reproduce, grass_regrowth_time)', 
                  setup=setup.format(25, 25, 60, 40, 0.2, 0.1, 20))
a = tt.repeat(n_run, 1)
median_time = sorted(a)[n_run // 2 + n_run % 2]
print("Mesa WolfSheep-small (ms):", median_time*1e3)

tt = timeit.Timer('runthemodel(seed, height, width, initial_sheep, initial_wolves, sheep_reproduce, wolf_reproduce, grass_regrowth_time)', 
                  setup=setup.format(100, 100, 1000, 500, 0.4, 0.2, 10))
a = tt.repeat(n_run, 1)
median_time = sorted(a)[n_run // 2 + n_run % 2]
print("Mesa WolfSheep-large (ms):", median_time*1e3)