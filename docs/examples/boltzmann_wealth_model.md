
# Boltzmann Wealth Model (Tutorial)

## Summary

A simple model of agents exchanging wealth. All agents start with the same amount of money. Every step, each agent with one unit of money or more gives one unit of wealth to another random agent. This is the model described in the [Intro Tutorial](https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html), with the completed code.

If you want to go over the step-by-step tutorial, please go and run the [Jupyter Notebook](https://github.com/projectmesa/mesa/blob/main/docs/tutorials/intro_tutorial.ipynb). The code here runs the finalized code in the last cells directly.

As the model runs, the distribution of wealth among agents goes from being perfectly uniform (all agents have the same starting wealth), to highly skewed -- a small number have high wealth, more have none at all.

## How to Run

To follow the tutorial example, launch the Jupyter Notebook and run the code in ``Introduction to Mesa Tutorial Code.ipynb`` which you can find in the main mesa repo [here](https://github.com/projectmesa/mesa/blob/main/docs/tutorials/intro_tutorial.ipynb)

Make sure to install the requirements first:

```
    $ pip install -r requirements.txt
```

To launch the interactive server, as described in the [last section of the tutorial](https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html#adding-visualization), run:

```
    $ solara run app.py
```

If your browser doesn't open automatically, point it to [http://127.0.0.1:8765/](http://127.0.0.1:8765/). When the visualization loads, click on the Play button.


## Files

* ``model.py``: Final version of the model.
* ``app.py``: Code for the interactive visualization.

## Optional

An optional visualization is also provided using Streamlit, which is another popular Python library for creating interactive web applications.

To run the Streamlit app, you will need to install the `streamlit` and `altair` libraries:

```
    $ pip install streamlit altair
```

Then, you can run the Streamlit app using the following command:

```
    $ streamlit run st_app.py
```

## Further Reading

The full tutorial describing how the model is built can be found at:
https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)


# Agents

```python
from mesa import Agent


class MoneyAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        super().__init__(model)
        self.wealth = 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(
            cellmates.index(self)
        )  # Ensure agent is not giving money to itself
        if len(cellmates) > 0:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()

```


# Model

```python
from agents import MoneyAgent

import mesa


class BoltzmannWealthModel(mesa.Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, n=100, width=10, height=10):
        super().__init__()
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, True)

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": self.compute_gini},
            agent_reporters={"Wealth": "wealth"},
        )
        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

    def compute_gini(self):
        agent_wealths = [agent.wealth for agent in self.agents]
        x = sorted(agent_wealths)
        n = self.num_agents
        b = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
        return 1 + (1 / n) - 2 * b

```