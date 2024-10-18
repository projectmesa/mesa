
## Description
# Conway's Game Of "Life"

## Summary

[The Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life), also known simply as "Life", is a cellular automaton devised by the British mathematician John Horton Conway in 1970.

The "game" is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input by a human. One interacts with the Game of "Life" by creating an initial configuration and observing how it evolves, or, for advanced "players", by creating patterns with particular properties.


## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press ``run``.

## Files

* ``agents.py``: Defines the behavior of an individual cell, which can be in two states: DEAD or ALIVE.
* ``model.py``: Defines the model itself, initialized with a random configuration of alive and dead cells.
* ``portrayal.py``: Describes for the front end how to render a cell.
* ``st_app.py``: Defines an interactive visualization using Streamlit.

## Optional

*  ``conways_game_of_life/st_app.py``: can be used to run the simulation via the streamlit interface.
* For this some additional packages like ``streamlit`` and ``altair`` needs to be installed.
* Once installed, the app can be opened in the browser using : ``streamlit run st_app.py``


## Further Reading
[Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)


## Agents

```python
from mesa import Agent


class Cell(Agent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    def __init__(self, pos, model, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.x, self.y = pos
        self.state = init_state
        self._nextState = None

    @property
    def isAlive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.model.grid.iter_neighbors((self.x, self.y), True)

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        live_neighbors = sum(neighbor.isAlive for neighbor in self.neighbors)

        # Assume nextState is unchanged, unless changed below.
        self._nextState = self.state
        if self.isAlive:
            if live_neighbors < 2 or live_neighbors > 3:
                self._nextState = self.DEAD
        else:
            if live_neighbors == 3:
                self._nextState = self.ALIVE

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._nextState

```


## Model

```python
from mesa import Model
from mesa.space import SingleGrid

from .agents import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50):
        """Create a new playing area of (width, height) cells."""
        super().__init__()
        # Use a simple grid, where edges wrap around.
        self.grid = SingleGrid(width, height, torus=True)

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for _contents, (x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self)
            if self.random.random() < 0.1:
                cell.state = cell.ALIVE
            self.grid.place_agent(cell, (x, y))

        self.running = True

    def step(self):
        """Perform the model step in two stages:
        - First, all cells assume their next state (whether they will be dead or alive)
        - Then, all cells change state to their next state.
        """
        self.agents.do("determine_state")
        self.agents.do("assume_state")

```


## App

```python
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from model import ConwaysGameOfLife

model = st.title("Conway's Game of Life")
num_ticks = st.slider("Select number of Steps", min_value=1, max_value=100, value=50)
height = st.slider("Select Grid Height", min_value=10, max_value=100, step=10, value=15)
width = st.slider("Select Grid Width", min_value=10, max_value=100, step=10, value=20)
model = ConwaysGameOfLife(height, width)

col1, col2, col3 = st.columns(3)
status_text = st.empty()
# step_mode = st.checkbox('Run Step-by-Step')
run = st.button("Run Simulation")


if run:
    tick = time.time()
    step = 0
    # init grid
    df_grid = pd.DataFrame()
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for x in range(width):
        for y in range(height):
            df_grid = pd.concat(
                [df_grid, pd.DataFrame({"x": [x], "y": [y], "state": [0]})],
                ignore_index=True,
            )

    heatmap = (
        alt.Chart(df_grid)
        .mark_point(size=100)
        .encode(x="x", y="y", color=alt.Color("state"))
        .interactive()
        .properties(width=800, height=600)
    )

    # init progress bar
    my_bar = st.progress(0, text="Simulation Progress")  # progress
    placeholder = st.empty()
    st.subheader("Agent Grid")
    chart = st.altair_chart(heatmap, use_container_width=True)
    color_scale = alt.Scale(domain=[0, 1], range=["red", "yellow"])
    for i in range(num_ticks):
        model.step()
        my_bar.progress((i / num_ticks), text="Simulation progress")
        placeholder.text("Step = %d" % i)
        for contents, (x, y) in model.grid.coord_iter():
            # print('x:',x,'y:',y, 'state:',contents)
            selected_row = df_grid[(df_grid["x"] == x) & (df_grid["y"] == y)]
            df_grid.loc[selected_row.index, "state"] = (
                contents.state
            )  # random.choice([1,2])

        heatmap = (
            alt.Chart(df_grid)
            .mark_circle(size=100)
            .encode(x="x", y="y", color=alt.Color("state", scale=color_scale))
            .interactive()
            .properties(width=800, height=600)
        )
        chart.altair_chart(heatmap)

        time.sleep(0.1)

    tock = time.time()
    st.success(f"Simulation completed in {tock - tick:.2f} secs")

```