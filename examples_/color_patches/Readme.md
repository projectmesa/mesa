# Color Patches


This is a cellular automaton model where each agent lives in a cell on a 2D grid, and never moves.

An agent's state represents its "opinion" and is shown by the color of the cell the agent lives in. Each color represents an opinion - there are 16 of them. At each time step, an agent's opinion is influenced by that of its neighbors, and changes to the most common one found; ties are randomly arbitrated. As an agent adapts its thinking to that of its neighbors, the cell color changes.

### Parameters you can play with:
(you must change the code to alter the parameters at this stage)
* Vary the number of opinions.
* Vary the size of the grid
* Change the grid from fixed borders to a torus continuum

### Observe
* how groups of like minded agents form and evolve
* how sometimes a single opinion prevails
* how some minority or fragmented opinions rapidly disappear

## How to Run

To run the model interactively, run ``mesa runserver` in this directory. e.g.

```
    $ mesa runserver
``` 

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run. 

## Files

* ``color_patches/model.py``: Defines the cell and model classes. The cell class governs each cell's behavior. The model class itself controls the lattice on which the cells live and interact.
* ``color_patches/server.py``: Defines an interactive visualization.
* ``run.py``: Launches an interactive visualization

## Further Reading

Inspired from [this model](http://www.cs.sjsu.edu/~pearce/modules/lectures/abs/as/ca.htm) from San Jose University<br>
Other similar models: [Schelling Segregation Model](https://github.com/projectmesa/mesa/tree/master/examples/Schelling)
