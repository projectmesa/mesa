# Schelling Segregation Model
=========================================

A simple implementation of a Schelling segregation model.

This version demonstrates the ASCII renderer.
To use, run this code from the command line, e.g.
    `$ ipython -i Schelling.py`

viz is the visualization wrapper around
To print the current state of the model:
    `viz.render()`

To advance the model by one step and print the new state:
    `viz.step()`

To advance the model by e.g. 10 steps and print the new state:
    `viz.step_forward(10)`
