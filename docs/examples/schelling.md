
## Description
# Schelling Segregation Model

## Summary

The Schelling segregation model is a classic agent-based model, demonstrating how even a mild preference for similar neighbors can lead to a much higher degree of segregation than we would intuitively expect. The model consists of agents on a square grid, where each grid cell can contain at most one agent. Agents come in two colors: red and blue. They are happy if a certain number of their eight possible neighbors are of the same color, and unhappy otherwise. Unhappy agents will pick a random empty cell to move to each step, until they are happy. The model keeps running until there are no unhappy agents.

By default, the number of similar neighbors the agents need to be happy is set to 3. That means the agents would be perfectly happy with a majority of their neighbors being of a different color (e.g. a Blue agent would be happy with five Red neighbors and three Blue ones). Despite this, the model consistently leads to a high degree of segregation, with most agents ending up with no neighbors of a different color.

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, in this directory, run the following command

```
    $ solara run app.py
```

Then open your browser to [http://127.0.0.1:8765/](http://127.0.0.1:8765/) and click the Play button.

To view and run some example model analyses, launch the IPython Notebook and open ``analysis.ipynb``. Visualizing the analysis also requires [matplotlib](http://matplotlib.org/).

## How to Run without the GUI

To run the model with the grid displayed as an ASCII text, run `python run_ascii.py` in this directory.

## Files

* ``app.py``: Code for the interactive visualization.
* ``schelling.py``: Contains the agent class, and the overall model class.
* ``analysis.ipynb``: Notebook demonstrating how to run experiments and parameter sweeps on the model.

## Further Reading

Schelling's original paper describing the model:

[Schelling, Thomas C. Dynamic Models of Segregation. Journal of Mathematical Sociology. 1971, Vol. 1, pp 143-186.](https://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf)

An interactive, browser-based explanation and implementation:

[Parable of the Polygons](http://ncase.me/polygons/), by Vi Hart and Nicky Case.


## Agents

```python
from mesa import Agent, Model


class SchellingAgent(Agent):
    """Schelling segregation agent."""

    def __init__(self, model: Model, agent_type: int) -> None:
        """Create a new Schelling agent.

        Args:
           agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(model)
        self.type = agent_type

    def step(self) -> None:
        neighbors = self.model.grid.iter_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )
        similar = sum(1 for neighbor in neighbors if neighbor.type == self.type)

        # If unhappy, move:
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1

```


## Model

```python
import mesa
from mesa import Model

from .agents import SchellingAgent


class Schelling(Model):
    """Model class for the Schelling segregation model."""

    def __init__(
        self,
        height=20,
        width=20,
        homophily=3,
        radius=1,
        density=0.8,
        minority_pc=0.2,
        seed=None,
    ):
        """Create a new Schelling model.

        Args:
            width, height: Size of the space.
            density: Initial Chance for a cell to populated
            minority_pc: Chances for an agent to be in minority class
            homophily: Minimum number of agents of same class needed to be happy
            radius: Search radius for checking similarity
            seed: Seed for Reproducibility
        """
        super().__init__(seed=seed)
        self.homophily = homophily
        self.radius = radius

        self.grid = mesa.space.SingleGrid(width, height, torus=True)

        self.happy = 0
        self.datacollector = mesa.DataCollector(
            model_reporters={"happy": "happy"},  # Model-level count of happy agents
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for _, pos in self.grid.coord_iter():
            if self.random.random() < density:
                agent_type = 1 if self.random.random() < minority_pc else 0
                agent = SchellingAgent(self, agent_type)
                self.grid.place_agent(agent, pos)

        self.datacollector.collect(self)

    def step(self):
        """Run one step of the model."""
        self.happy = 0  # Reset counter of happy agents
        self.agents.shuffle_do("step")

        self.datacollector.collect(self)

        self.running = self.happy != len(self.agents)

```


## App

```python
import solara

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_measure,
    make_space_matplotlib,
)

from .model import Schelling


def get_happy_agents(model):
    """Display a text count of how many happy agents there are."""
    return solara.Markdown(f"**Happy agents: {model.happy}**")


def agent_portrayal(agent):
    return {"color": "tab:orange" if agent.type == 0 else "tab:blue"}


model_params = {
    "density": Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": Slider("Fraction minority", 0.2, 0.0, 1.0, 0.05),
    "homophily": Slider("Homophily", 3, 0, 8, 1),
    "width": 20,
    "height": 20,
}

model1 = Schelling(20, 20, 0.8, 0.2, 3)

HappyPlot = make_plot_measure("happy")

page = SolaraViz(
    model1,
    components=[
        make_space_matplotlib(agent_portrayal),
        make_plot_measure("happy"),
        get_happy_agents,
    ],
    model_params=model_params,
)
page  # noqa

```