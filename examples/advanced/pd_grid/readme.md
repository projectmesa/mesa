# Demographic Prisoner's Dilemma on a Grid

## Summary

The Demographic Prisoner's Dilemma is a family of variants on the classic two-player [Prisoner's Dilemma]. The model consists of agents, each with a strategy of either Cooperate or Defect. Each agent's payoff is based on its strategy and the strategies of its spatial neighbors. After each step of the model, the agents adopt the strategy of their neighbor with the highest total score.

The model payoff table is:

|               | Cooperate | Defect|
|:-------------:|:---------:|:-----:|
| **Cooperate** | 1, 1      | 0, D  |
| **Defect**    | D, 0      | 0, 0  |

Where *D* is the defection bonus, generally set higher than 1. In these runs, the defection bonus is set to $D=1.6$.

The Demographic Prisoner's Dilemma demonstrates how simple rules can lead to the emergence of widespread cooperation, despite the Defection strategy dominating each individual interaction game. However, it is also interesting for another reason: it is known to be sensitive to the activation regime employed in it.

## How to Run

##### Web based model simulation

To run the model interactively, run ``mesa runserver`` in this directory.

##### Jupyter Notebook

Launch the ``Demographic Prisoner's Dilemma Activation Schedule.ipynb`` notebook and run the code.

## Files

* ``run.py`` is the entry point for the font-end simulations.
* ``pd_grid/``: contains the model and agent classes; the model takes a ``schedule_type`` string as an argument, which determines what schedule type the model uses: Sequential, Random or Simultaneous.
* ``Demographic Prisoner's Dilemma Activation Schedule.ipynb``: Jupyter Notebook for running the scheduling experiment. This runs the model three times, one for each activation type, and demonstrates how the activation regime drives the model to different outcomes.

## Further Reading

This model is adapted from:

Wilensky, U. (2002). NetLogo PD Basic Evolutionary model. http://ccl.northwestern.edu/netlogo/models/PDBasicEvolutionary. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.

The Demographic Prisoner's Dilemma originates from:

[Epstein, J. Zones of Cooperation in Demographic Prisoner's Dilemma. 1998.](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.8.8629&rep=rep1&type=pdf)
