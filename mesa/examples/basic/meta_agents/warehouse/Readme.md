# Pseudo-Warehouse Model

## Summary

The  purpose of this model is to demonstrate Mesa's meta-agent capability and some of its implementation approaches, not to be an accurate warehouse simulation. In this simulations, robots are given tasks to take retrieve inventory items and then take those items to the loading docks.

Each `RobotAgent` is made up of sub-components that are treated as separate agents. FOr this simulation, each robot as a `SensorAgent`, `RouterAgent`, and `WorkerAgent`.

This model demonstrates deliberate meta-agent creation. It shows the basics of meta-agent creation and different ways to use and reference sub-agent and meta-agent functions and attributes. (The alliance formation demonstrates emergent meta-agent creation.)

In its current configuration, agents being part of multiple meta-agents is not supported

## Installation

This model requires Mesa's recommended install

```
    $ pip install mesa[rec]
```

## How to Run

To run the model interactively, in this directory, run the following command

```
    $ solara run app.py
```

## Files

- `model.py`: Contains creation of agents, the network and management of agent execution.
- `agents.py`: Contains logic for forming alliances and creation of new agents
- `app.py`: Contains the code for the interactive Solara visualization.
- `make_warehouse`: Generates a warehouse numpy array with loading docks, inventory, and charging stations.