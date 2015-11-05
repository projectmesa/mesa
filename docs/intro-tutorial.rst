Introduction to Mesa - Tutorial
================================

Getting started with Mesa is easy. In this doc, we will present Mesa’s architecture and core features. To illustrate them, we'll walk you through building a simple agent-based model, drawn from econophysics and presenting a statistical mechanics approach to wealth distribution [Dragulescu2002]_.

The rules of our tutorial model:

- There are some number of agents.
- All agents begin with 1 unit of money.
- Every step of the model, an agent gives 1 unit of money (if they have it) to some other agent.

Despite its simplicity, this model yields results that are often unexpected to those not familiar with it. For our purposes, it also easily demonstrates Mesa's core features.

Let's get started.


Installation
------------

The first thing you need to do is to install Mesa. We recommend doing this in a `virtual environment <https://virtualenvwrapper.readthedocs.org/en/stable/>`_, but make sure your environment is set up with Python 3. Mesa requires Python3 and does not work in < Python 2 environments.

To install Mesa, simply:

.. code-block:: bash

    $ pip install mesa

When you do that, it will install Mesa itself, as well as any dependencies that aren't in your setup yet.


Building a sample model
------------------------

With Mesa all installed, let's go ahead and start building our model. There are two ways to go about it: you can write the code in its own file with your favorite text editor or IDE, or interactively in Jupyter Notebook cells. 

Either way, it's good practice to put your model in its own folder -- especially if the project will end up consisting of multiple files (for example, Python files for the model and the visualization,  a Notebook for analysis, and a Readme with some documentation and discussion). 

Go ahead and create a folder, and either launch a Notebook or create a new Python source file.


Setting up the model
~~~~~~~~~~~~~~~~~~~~~

Now it's time to start writing the code. The model is going to need two core classes: one for the overall model, the other for the agents. The model class holds the model-level parameters, manages the agents, and generally handle the global level of our model. Each instantiation of the model class will be a specific model run. Each model will contain multiple agents, all of which are instantiations of the agent class. Both the model and agent classes are child classes of Mesa's generic Model and Agent classes.

Each agent has only one variable: how much wealth it currently has. It's also good practice to give agents a unique identifier (i.e. a name), stored in the ``unique_id`` variable.

There is only one model-level parameter: how many agents the model contains. When a new model is started, we want it to populate itself with the given number of agents.

The beginning of both classes looks like this:

.. code-block:: python

   from mesa import Agent, Model

    class MoneyAgent(Agent):
        """ An agent with fixed initial wealth."""
        def __init__(self, unique_id):
            self.unique_id = unique_id
            self.wealth = 1

   class MoneyModel(Model):
        """A model with some number of agents."""
        def __init__(self, N):
             self.num_agents = N
             # Create agents
             for i in range(self.num_agents):
                a = MoneyAgent(i)
                # Now what? See below.

Adding the scheduler
~~~~~~~~~~~~~~~~~~~~~

Time in most agent-based models moves in steps, sometimes also called ticks. Each step of the model, one or more of the agents -- usually all of them -- are activated and take their own step, changing internally and/or interacting with one another or the environment. 

The ``scheduler`` is a special model component which controls the order in which agents are activated. For example, all the agents may activate in the same order every step; their order might be shuffled; we may try to simulate all the agents acting at the same time; and more. Mesa offers a few different built-in scheduler classes, with a common interface. That makes it easy to change the activation regime a given model uses, and see whether it changes the model behavior.

For now, let's use one of the simplest ones: ``RandomActivation``, which activates all the agents once per step, in random order. Every agent is expected to have a ``step`` method, which takes a model object as its only argument -- this is the agent's action when it is activated. We add an agent to the schedule using the ``add`` method; when we call the schedule's ``step`` method, it shuffles the order of the agents, then activates them all, one at a time.

With that in mind, the model code with the scheduler added looks like this: 

.. code-block:: python

   from mesa import Agent, Model
   from mesa.time import RandomActivation

    class MoneyAgent(Agent):
        """ An agent with fixed initial wealth."""
        def __init__(self, unique_id):
            self.unique_id = unique_id
            self.wealth = 1

        def step(self, model):
            # The agent's step will go here.
            pass

   class MoneyModel(Model):
        """A model with some number of agents."""
        def __init__(self, N):
             self.num_agents = N
             self.schedule = RandomActivation(self)
             # Create agents
             for i in range(self.num_agents):
                a = MoneyAgent(i)
                self.schedule.add(self)

        def step(self):
            '''Advance the model by one step.'''
            self.schedule.step()

At this point, we have a model which runs -- it just doesn't do anything. You can see for yourself with a few easy lines:

.. code-block:: python

    empty_model = MoneyModel(10)
    empty_model.step()

**Exercise:** If you want, modify the code above to have every agent print out its ``unique_id`` when it is activated. Run a few steps of the model to see how the agent activation order is shuffled each step.

Agent step
~~~~~~~~~~

Now we just need to have the agents do what we intend for them to do: check their wealth, and if they have the money, give one unit of it away to another random agent.


** THIS DOC IS IN PROGRESS **




.. _`virtual environment`: http://docs.python-guide.org/en/latest/dev/virtualenvs/

.. [Dragulescu2002] Drăgulescu, Adrian A., and Victor M. Yakovenko. “Statistical Mechanics of Money, Income, and Wealth: A Short Survey.” arXiv Preprint Cond-mat/0211175, 2002. http://arxiv.org/abs/cond-mat/0211175.



