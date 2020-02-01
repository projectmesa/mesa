# Conway's Game Of "Life" on a hexagonal grid

## Summary

In this model, each dead cell will become alive if it has exactly one neighbor. Alive cells stay alive forever.  


## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press ``run``.

## Files

* ``hex_snowflake/cell.py``: Defines the behavior of an individual cell, which can be in two states: DEAD or ALIVE.
* ``hex_snowflake/model.py``: Defines the model itself, initialized with one alive cell at the center.
* ``hex_snowflake/portrayal.py``: Describes for the front end how to render a cell.
* ``hex_snowflake/server.py``: Defines an interactive visualization.
* ``run.py``: Launches the visualization

## Further Reading
[Explanation of how hexagon neighbors are calculated. (The method is slightly different for Cartesian coordinates)](http://www.redblobgames.com/grids/hexagons/#neighbors-offset)
