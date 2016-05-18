# Conway's Game Of "Life"

## Summary

[The Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life), also known simply as "Life", is a cellular automaton devised by the British mathematician John Horton Conway in 1970.

The "game" is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input by a human. One interacts with the Game of "Life" by creating an initial configuration and observing how it evolves, or, for advanced "players", by creating patterns with particular properties.


## How to Run

To run the model interactively, run ``run.py`` in this directory. e.g.

```
    $ python cgol_main.py
``` 

Then open your browser to [http://127.0.0.1:8888/](http://127.0.0.1:8888/) and press Reset, then Run. 

## Files

* ``cgol_cell.py``: Defines the behavior of an individual cell, which can be in two states: DEAD or ALIVE.
* * ``cgol_model.py``: Defines the model itself, initialized with a random configuration of alive and dead cells.
* * ``cgol_main.py``: Defines and launches an interactive visualization.

## Further Reading


