# Sugarscape Constant Growback model

## Summary

This is Epstein & Axtell's Sugarscape Constant Growback model, with a detailed
description in the chapter 2 of Growing Artificial Societies: Social Science from the Bottom Up

A simple ecological model, consisting of two agent types: ants, and sugar
patches.

The ants wander around according to Epstein's rule M:
- Look out as far as vision pennies in the four principal lattice directions and identify the unoccupied site(s) having the most sugar. The order in which each agent search es the four directions is random.
- If the greatest sugar value appears on multiple sites then select the nearest one. That is, if the largest sugar within an agent s vision is four, but the value occurs twice, once at a lattice position two units away and again at a site three units away, the former is chosen. If it appears at multiple sites the same distance away, the first site encountered is selected (the site search order being random).
- Move to this site. Notice that there is no distinction between how far an agent can move and how far it can see. So, if vision equals 5, the agent can move up to 5 lattice positions north , south, east, or west.
- Collect all the sugar at this new position.

The sugar patches grow at a constant rate of 1 until it reaches maximum capacity. If ant metabolizes to the point it has zero or negative sugar, it dies.


The model is tests and demonstrates several Mesa concepts and features:
 - MultiGrid
 - Multiple agent types (ants, sugar patches)
 - Overlay arbitrary text (wolf's energy) on agent's shapes while drawing on CanvasGrid
 - Dynamically removing agents from the grid and schedule when they die

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* ``sugarscape/agents.py``: Defines the SsAgent, and Sugar agent classes.
* ``sugarscape/schedule.py``: This is exactly based on wolf_sheep/schedule.py.
* ``sugarscape/model.py``: Defines the Sugarscape Constant Growback model itself
* ``sugarscape/server.py``: Sets up the interactive visualization server
* ``run.py``: Launches a model visualization server.

## Further Reading

This model is based on the Netlogo Sugarscape 2 Constant Growback:

Li, J. and Wilensky, U. (2009). NetLogo Sugarscape 2 Constant Growback model.
http://ccl.northwestern.edu/netlogo/models/Sugarscape2ConstantGrowback.
Center for Connected Learning and Computer-Based Modeling,
Northwestern University, Evanston, IL.

The ant sprite is taken from https://openclipart.org/detail/229519/ant-silhouette, with CC0 1.0 license.
