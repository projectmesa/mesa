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

* ``conways_game_of_life/cell.py``: Defines the behavior of an individual cell, which can be in two states: DEAD or ALIVE.
* ``conways_game_of_life/model.py``: Defines the model itself, initialized with a random configuration of alive and dead cells.
* ``conways_game_of_life/portrayal.py``: Describes for the front end how to render a cell.
* ``conways_game_of_life/server.py``: Defines an interactive visualization.
* ``run.py``: Launches the visualization

## Optional

*  ``conways_game_of_life/app.py``: can be used to run the simulation via the streamlit interface.
* For this some additional packages like ``streamlit`` and ``altair`` needs to be installed.
* Once installed, the app can be opened in the browser using : ``streamlit run app.py``


## Further Reading
[Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)

