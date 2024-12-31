# Alliance Formation Model

## Summary
This model demonstrates Mesa's ability to dynamically create new classes of agents that are composed of existing agents. These meta-agents  inherits functions and attributes from their sub-agents and users can specify new functionality or attributes they want the meta agent to have. For example, if a user is doing a factory simulation with autonomous systems, each major component of that system can be a sub-agent of the overall robot agent. Or, if someone is doing a simulation of an organization, individuals can be part of different organizational units that are working for some purpose.

To provide a simple demonstration of this capability is an alliance formation model.

In this simulation n agents are created, who have two attributes (1) power and (2) preference. Each attribute is a number between 0 and 1 over a gaussian distribution. Agents then randomly select other agents and use the [bilateral shapley value](https://en.wikipedia.org/wiki/Shapley_value) to determine if they should form an alliance. If the expected utility support an alliances, the agent creates a meta-agent. Subsequent steps may add agents to the meta-agent, create new instances of similar hierarchy, or create a new hierarchy level where meta-agents form an alliance of meta-agents. In this visualization of this model a new meta-agent hierarchy will be a larger node and a new color.

In its current configuration, agents being part of multiple meta-agents is not supported

## Installation

This model requires Mesa's recommended install and scipy
```
    $ pip install mesa[rec]
```

## How to Run

To run the model interactively, in this directory, run the following command

```
    $ solara run app.py
```

## Files

* ``model.py``: Contains creation of agents, the network and management of agent execution.
* ``agents.py``: Contains logic for forming alliances and creation of new agents
* ``app.py``: Contains the code for the interactive Solara visualization.

## Further Reading

The full tutorial describing how the model is built can be found at:
https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html

An example of the bilateral shapley value in another model:
[Techno-Social Energy Infrastructure Siting: Sustainable Energy Modeling Programming (SEMPro)](https://www.jasss.org/16/3/6.html)

