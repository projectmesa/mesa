## Color Patches:
Is a cellulat automaton model where each agent lives in a cell on a 2D grid, and never moves.<br>
An agent's state represents its "opinion" and is shown by the color of the cell the agent lives in. Each color represents an opinion - there are 16 of them.<br>
At each time step, an agent's opinion is influenced by that of its neighbors, and changes to the most common one found; ties are randomly arbitrated.<br>
As an agent adapts its thinking to that of its neighbors, the cell color changes.


### Parameters you can play with:
(you must change the code to alter the parameters at this stage)
* Vary the number of opinions.
* Vary the size of the grid
* Change the grid from fixed borders to a torus continuum


### Observe
* how groups of like minded agents form and evolve
* how sometimes a single opinion prevails
* how some minority or fragmented opinions rapidly disappear


### Sources and Attribution
Inspired from [this model](http://www.cs.sjsu.edu/~pearce/modules/lectures/abs/as/ca.htm) from San Jose University<br>
Other similar models: [Schelling Segregation Model](https://github.com/projectmesa/mesa/tree/master/examples/Schelling)


### To run this example

* Launch the model
```python
python color_patches.py
```
* Visit your browser: http://127.0.0.1:8888/
* In your browser hit *reset*, then *run*
