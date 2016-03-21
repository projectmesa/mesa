## Schelling Segregation Model

A simple implementation of a Schelling segregation model.


Implemented here to test / demonstrate several Mesa concepts and features:
 - This version demonstrates the ASCII renderer.


### To run this example

* Launch the model
```python
python Schelling.py
```
* Visit your browser: http://127.0.0.1:8888/
* In your browser hit *reset*, then *run*


To use with iPython, run this code from the command line, e.g.
    $ ipython -i Schelling.py

viz is the visualization wrapper around
To print the current state of the model:
    viz.render()

To advance the model by one step and print the new state:
    viz.step()

To advance the model by e.g. 10 steps and print the new state:
    viz.step_forward(10)