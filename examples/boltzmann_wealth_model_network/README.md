# Boltzmann Wealth Model with Network

## Summary

This is the same Boltzmann Wealth Model, but with a network grid implementation.

A simple model of agents exchanging wealth. All agents start with the same amount of money. Every step, each agent with one unit of money or more gives one unit of wealth to another random agent. This is the model described in the [Intro Tutorial](http://mesa.readthedocs.io/en/latest/intro-tutorial.html).

In this network implementation, agents must be located on a node, with a limit of one agent per node. In order to give or receive the unit of money, the agent must be directly connected to the other agent (there must be a direct link between the nodes).

As the model runs, the distribution of wealth among agents goes from being perfectly uniform (all agents have the same starting wealth), to highly skewed -- a small number have high wealth, more have none at all.

JavaScript library used in this example to render the network: [sigma.js](http://sigmajs.org/).

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

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model (network layout) in the browser via Mesa's modular server, and instantiates a visualization server.

## Further Reading

The full tutorial describing how the model is built can be found at:
http://mesa.readthedocs.io/en/master/tutorials/intro_tutorial.html

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
