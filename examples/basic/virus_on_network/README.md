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

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model (network layout) in the browser via Mesa's modular server, and instantiates a visualization server.

## Further Reading

The full tutorial describing how the model is built can be found at:
https://mesa.readthedocs.io/en/latest/tutorials/intro_tutorial.html


[Stonedahl, F. and Wilensky, U. (2008). NetLogo Virus on a Network model](http://ccl.northwestern.edu/netlogo/models/VirusonaNetwork).
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.


[Wilensky, U. (1999). NetLogo](http://ccl.northwestern.edu/netlogo/)
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.
