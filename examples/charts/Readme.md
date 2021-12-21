# Mesa Charts Example

## Summary

A modified version of the "bank_reserves" example made to provide examples of mesa's charting tools.

The chart types included in this example are:
- Line Charts for time-series data of multiple model parameters
- Pie Charts for model parameters
- Bar charts for both model and agent-level parameters

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## Interactive Model Run

To run the model interactively, use `mesa runserver` in this directory:

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/), select the model parameters, press Reset, then Start.

## Files

* ``bank_reserves/random_walker.py``: This defines a class that inherits from the Mesa Agent class. The main purpose is to provide a method for agents to move randomly one cell at a time.
* ``bank_reserves/agents.py``: Defines the People and Bank classes.
* ``bank_reserves/model.py``: Defines the Bank Reserves model and the DataCollector functions.
* ``bank_reserves/server.py``: Sets up the interactive visualization server.
* ``run.py``: Launches a model visualization server.

## Further Reading

See the "bank_reserves" model for more information.
