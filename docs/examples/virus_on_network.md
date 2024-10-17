
# Virus on a Network

## Summary

This model is based on the NetLogo model "Virus on Network". It demonstrates the spread of a virus through a network and follows the SIR model, commonly seen in epidemiology.

The SIR model is one of the simplest compartmental models, and many models are derivatives of this basic form. The model consists of three compartments:

S: The number of susceptible individuals. When a susceptible and an infectious individual come into "infectious contact", the susceptible individual contracts the disease and transitions to the infectious compartment.
I: The number of infectious individuals. These are individuals who have been infected and are capable of infecting susceptible individuals.
R for the number of removed (and immune) or deceased individuals. These are individuals who have been infected and have either recovered from the disease and entered the removed compartment, or died. It is assumed that the number of deaths is negligible with respect to the total population. This compartment may also be called "recovered" or "resistant".

For more information about this model, read the NetLogo's web page: http://ccl.northwestern.edu/netlogo/models/VirusonaNetwork.

JavaScript library used in this example to render the network: [d3.js](https://d3js.org/).

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

or

Directly run the file ``run.py`` in the terminal. e.g.

```
    $ python run.py
```


## Files

* ``model.py``: Contains the agent class, and the overall model class.
* ``agents.py``: Contains the agent class.
* ``app.py``: Contains the code for the interactive Solara visualization.

## Further Reading

The full tutorial describing how the model is built can be found at:
https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html


[Stonedahl, F. and Wilensky, U. (2008). NetLogo Virus on a Network model](http://ccl.northwestern.edu/netlogo/models/VirusonaNetwork).
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.


[Wilensky, U. (1999). NetLogo](http://ccl.northwestern.edu/netlogo/)
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.


# Agents

```python
from enum import Enum

from mesa import Agent


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


class VirusAgent(Agent):
    """Individual Agent definition and its properties/interaction methods."""

    def __init__(
        self,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        recovery_chance,
        gain_resistance_chance,
    ):
        super().__init__(model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighborhood(
            self.pos, include_center=False
        )
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            if self.random.random() < self.virus_spread_chance:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        if (self.random.random() < self.virus_check_frequency) and (
            self.state is State.INFECTED
        ):
            self.try_remove_infection()

    def step(self):
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation()

```


# Model

```python
import math

import networkx as nx
from agents import State, VirusAgent

import mesa
from mesa import Model


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


class VirusOnNetwork(Model):
    """A virus model with some number of agents."""

    def __init__(
        self,
        num_nodes=10,
        avg_node_degree=3,
        initial_outbreak_size=1,
        virus_spread_chance=0.4,
        virus_check_frequency=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.5,
    ):
        super().__init__()
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = mesa.space.NetworkGrid(self.G)

        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

        self.datacollector = mesa.DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
            }
        )

        # Create agents
        for node in self.G.nodes():
            a = VirusAgent(
                self,
                State.SUSCEPTIBLE,
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.recovery_chance,
                self.gain_resistance_chance,
            )

            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(list(self.G), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.agents.shuffle_do("step")
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for _ in range(n):
            self.step()

```