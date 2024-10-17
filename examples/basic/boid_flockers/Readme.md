# Boids Flockers

## Summary

An implementation of Craig Reynolds's Boids flocker model. Agents (simulated birds) try to fly towards the average position of their neighbors and in the same direction as them, while maintaining a minimum distance. This produces flocking behavior.

This model tests Mesa's continuous space feature, and uses numpy arrays to represent vectors. It also demonstrates how to create custom visualization components.

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

* To launch the visualization interactively, run ``mesa runserver`` in this directory. e.g.

```
$ mesa runserver
```

or

Directly run the file ``run.py`` in the terminal. e.g.

```
    $ python run.py
```

* Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* [model.py](model.py): Core model file; contains the Boid Model and Boid Agent class.
* [app.py](app.py): Visualization code.

## Further Reading

The following link can be visited for more information on the boid flockers model:
https://cs.stanford.edu/people/eroberts/courses/soco/projects/2008-09/modeling-natural-systems/boids.html
