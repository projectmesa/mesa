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

The first thing you need to do is to install Mesa. We recommend doing this in a `virtual environment`_. Make sure your work space is pointed to Python 3. Mesa requires Python3 and does not work in < Python 3 environments.

To install Mesa, simply:

.. code-block:: bash

    $ pip install mesa

When you do that, it will install the following packages and dependencies.

- mesa
- tornado
- numpy
- pandas


Overview of Modules
------------

There are three module types in Mesa.

1. modeling
2. analysis
3. visualization

TODO: Insert image


Modeling modules
~~~~~~~~~~~~~~

To build a model, you need the following:

* **Model class** to store the model-level parameters and serve as a container for the rest of the components.

* **Agent class(es)** which describe the model agents.

* **Scheduler** which controls the agent activation regime, and handles time in the model in general.

* **space** components describing the space and/or network the agents are situated in (if any).


Analysis modules
~~~~~~~~~~~~~~

Not every model *needs* these modules, but they provide useful tools for getting data out of your model runs to study more systematically.

* **Data collectors** are used to record data from each model run.
* **Batch runners** automate multiple runs and parameter sweeps -- running the model with different parameters, to see how they change its behavior.


Visualization modules
~~~~~~~~~~~~~~

A visualization lets you directly observe model runs, seeing the dynamics that emerge from it and making sure that it's behaving in the way you want it to. Mesa handles visualizations in a browser window, using JavaScript. It provides a set of pre-built components, which can be instantiated for a particular model in Python and automatically generate the corresponding objects in the browser window. It's also easy to write your own components with some basic JavaScript knowledge.

Some visualization modules we'll use here include:

* **Grid** visualization,
* **Chart** display module,
* The **ModularServer** itself.

Building a sample model
------------

Now that we understand a little bit about the components, let's use those components to build a model.

First, we need a place to put our model. Let's create a directory for our model for good practice. In this tutorial, we will call this 'mesa-example'.

.. code-block:: bash

    mkdir mesa-example
    cd mesa-example

Create a file to store your sample model. Let's call it money.py.

.. code-block:: bash

    touch moneymodel.py

In the editor of your choice, open moneymodel.py.

To begin building the example model described at the top of this page -- we first *subclass two classes: one for the model object itself and one the model agents*.


Creating the model
~~~~~~~~~~~~~~

The first we do is import the ``Model`` base class.

.. code-block:: python

    from mesa import Model

Then we subclass and instance of the Money Model. The model itself will have some number of agents and will have a funtion to create our agents.

.. code-block:: python

   class MoneyModel(Model):
        """A model with some number of agents."""
        def __init__(self, N):
             self.num_agents = N

Creating Agents
~~~~~~~~~~~~~~

In our example, each agent has a single ...

* variable: How much money it currently has
* action: Give a unit of money to another agent

The first we do is import the ``Agent`` base class. Update the import statement to reflect this.

.. code-block:: python

    from mesa import Model, Agent

Then subclass Agent to create a class that is specific to our sample model. (You will want to put this above the Model class, because the model is going to need to reference it.)

Each agent should have a unique identifier and start with a wealth of 1.

.. code-block:: python

    class MoneyAgent(Agent):
        """ An agent with fixed initial wealth."""
        def __init__(self, unique_id):
            self.unique_id = unique_id
            self.wealth = 1

    class MoneyModel(Model):
        ....

We have an Agent object and a Model Object, but we have no Agents in our Model. Let's add those.

Adding Agents to Model
~~~~~~~~~~~~~~

Add create_agents function to the MoneyModel. We need to loop over the num_agents and instantiate an our agent and store the agent into a variable.

.. code-block:: python

    class MoneyModel(Model):
        ...

        def create_agents(self):
            """Method to create all the agents."""
            for i in range(self.num_agents):
                a = MoneyAgent(i)

Then, we need to call this function when the object is initiated.

.. code-block:: python

   class MoneyModel(Model):
        """A model with some number of agents."""
        def __init__(self, N):
             self.num_agents = N
             self.create_agents()

At this point, your code should look like the code below.

.. code-block:: python

  from mesa import Model, Agent

  class MoneyAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id):
      self.unique_id = unique_id
      self.wealth = 1

  class MoneyModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):
      self.num_agents = N
      # The scheduler will be added here
      self.create_agents()

    def create_agents(self):
      """Method to create all the agents."""
      for i in range(self.num_agents):
        a = MoneyAgent(i)
        # Now what? See below.


** THIS DOC IS IN PROGRESS **




.. _`virtual environment`: http://docs.python-guide.org/en/latest/dev/virtualenvs/

.. [Dragulescu2002] Drăgulescu, Adrian A., and Victor M. Yakovenko. “Statistical Mechanics of Money, Income, and Wealth: A Short Survey.” arXiv Preprint Cond-mat/0211175, 2002. http://arxiv.org/abs/cond-mat/0211175.



