# Bank Reserves Model

## Summary

A highly abstracted, simplified model of an economy, with only one type of agent and a single bank representing all banks in an economy. People (represented by circles) move randomly within the grid. If two or more people are on the same grid location, there is a 50% chance that they will trade with each other. If they trade, there is an equal chance of giving the other agent $5 or $2. A positive trade balance will be deposited in the bank as savings. If trading results in a negative balance, the agent will try to withdraw from its savings to cover the balance. If it does not have enough savings to cover the negative balance, it will take out a loan from the bank to cover the difference. The bank is required to keep a certain percentage of deposits as reserves. If run.py is used to run the model, then the percent of deposits the bank is required to retain is a user settable parameter. The amount the bank is able to loan at any given time is a function of the amount of deposits, its reserves, and its current total outstanding loan amount. 

The model demonstrates the following Mesa features:
 - MultiGrid for creating shareable space for agents
 - DataCollector for collecting data on individual model runs
 - UserSettableParameters for adjusting initial model parameters
 - ModularServer for visualization of agent interaction
 - Agent object inheritance
 - Using a BatchRunner to collect data on multiple combinations of model parameters

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

## Batch Run

To run the model as a batch run to collect data on multiple combinations of model parameters, run "batch_run.py" in this directory. 

```
    $ python batch_run.py
```
A progress status bar will display.

To update the parameters to test other parameter sweeps, edit the list of parameters in the dictionary named "br_params" in "batch_run.py".

## Files

* ``bank_reserves/random_walker.py``: This defines a class that inherits from the Mesa Agent class. The main purpose is to provide a method for agents to move randomly one cell at a time.
* ``bank_reserves/agents.py``: Defines the People and Bank classes.
* ``bank_reserves/model.py``: Defines the Bank Reserves model and the DataCollector functions.
* ``bank_reserves/server.py``: Sets up the interactive visualization server.
* ``run.py``: Launches a model visualization server.
* ``batch_run.py``: Basically the same as model.py, but includes a Mesa BatchRunner. The result of the batch run will be a .csv file with the data from every step of every run. 

## Further Reading

This model is a Mesa implementation of the Bank Reserves model from NetLogo:

Wilensky, U. (1998). NetLogo Bank Reserves model. http://ccl.northwestern.edu/netlogo/models/BankReserves. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.

