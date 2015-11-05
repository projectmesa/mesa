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

Now it's time to start writing the code. The model is going to need two core classes: one for the overall model, the other for the agents. The model class holds the model-level parameters, manages the agents, and generally handle the global level of our model. Each instantiation of the model class will be a specific model run. Each model will contain multiple agents, all of which are instantiations of the agent class. Both the model and agent classes are child classes of Mesa's generic ``Model`` and ``Agent`` classes.

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
                self.schedule.add(a)

        def step(self):
            '''Advance the model by one step.'''
            self.schedule.step()

At this point, we have a model which runs -- it just doesn't do anything. You can see for yourself with a few easy lines. If you've been working in an interactive session, you can create a model object directly. Otherwise, you need to open an interactive session in the same directory as your source code file, and import the classes. For example, if your code is in ``MoneyModel.py``:

.. code-block::python

    from MoneyModel import MoneyModel

Then create the model object, and run it for one step:

.. code-block:: python

    empty_model = MoneyModel(10)
    empty_model.step()

**Exercise:** If you want, modify the code above to have every agent print out its ``unique_id`` when it is activated. Run a few steps of the model to see how the agent activation order is shuffled each step.

Agent step
~~~~~~~~~~

Now we just need to have the agents do what we intend for them to do: check their wealth, and if they have the money, give one unit of it away to another random agent.

To pick an agent at random, we need a list of all agents. Notice that there isn't such a list explicitly in the model. The scheduler, however, does have an internal list of all the agents it is scheduled to activate. 

With that in mind, we rewrite the agent's ``step`` method, like this:

.. code-block:: python

    class MoneyAgent(Agent):
      # ...
      def step(self, model):
          if self.wealth == 0:
              return
          other_agent = random.choice(model.schedule.agents)
          other_agent.wealth += 1
          self.wealth -= 1


Running your first model
~~~~~~~~~~~~~~~~~~~~~~~~~

With that last piece in hand, it's time for the first rudimentary run of the model. Let's create a model with 10 agents, and run it for 10 steps. 

.. code-block:: python

    model = MoneyModel(10)
    for i in range(10):
        model.step()

Now we need to get some data out of the model. Specifically, we want to see the distribution of the agent's wealth. We can get the wealth values with list comprehension, and then use matplotlib (or the graphics library of your choice) to visualize a histogram.

.. code-block:: python

    agent_wealth = [a.wealth for a in model.schedule.agents]
    plt.hist(agent_wealth)


You'll probably see something like the distribution shown below. Yours will almost certainly look at least slightly different, since each run of the model is random, after all. 

To get a better idea of how a model behaves, we can create multiple model runs, and see the distribution that emerges from all of them. We can do this with a nested for loop:

.. code-block:: python
    all_wealth = []
    for j in range(100):
        # Run the model
        model = MoneyModel(10)
        for i in range(10):
            model.step()
        # Store the results
        for agent in model.schedule.agents:
            all_wealth.append(agent.wealth)

    plt.hist(all_wealth, bins=range(max(all_wealth)+1))

This runs 100 instantiations of the model, and runs each for 10 steps. (Notice that we set the histogram bins to be integers, since agents can only have whole numbers of wealth). This distribution looks a lot smoother. By running the model 100 times, we smooth out some of the 'noise' of randomness, and get to the model's overall expected behavior.

This outcome might be surprising. Despite the fact that all agents, on average, give and receive one unit of money every step, the model converges to a state where most agents have a small amount of money and a small number have a lot of money.

Adding space
~~~~~~~~~~~~~

Many ABMs have a spatial element, with agents moving around and interacting with nearby neighbors. Mesa currently supports two overall kinds of spaces: grid, and continuous. Grids are divided into cells, and agents can only be on a particular cell, like pieces on a chess board. Continuous space, in contrast, allows agents to have any arbitrary position. Both grids and continuous spaces are frequently toroidal, meaning that the edges wrap around, with cells on the right edge connected to those on the left edge, and the top to the bottom. This prevents some cells having fewer neighbors than others, or agents being able to go off the edge of the environment.

Let's add a simple spatial element to our model: we'll have the agents live on a grid and walk around at random. Instead of giving their unit of money to any random agent, they'll give it to an agent on the same cell.

Mesa has two main types of grids: ``SingleGrid`` and ``MultiGrid``. ``SingleGrid`` enforces at most one agent per cell; ``MultiGrid`` allows multiple agents to be in the same cell. Since we want agents to be able to share a cell, we use ``MultiGrid``.

.. code-block:: python

    from mesa.space import MultiGrid

We instantiate a grid with height and width parameters, and a boolean as to whether the grid is toriodal. Let's make width and height model parameters, in addition to the number of agents, and have the grid always be toriodal. We can place agents on a grid with the grid's ``place_agent`` method, which takes an agent and an (x, y) tuple of the coordinates to place the agent.

.. code-block:: python

   class MoneyModel(Model):
        """A model with some number of agents."""
        def __init__(self, N, width, height):
            self.num_agents = N
            self.grid = MultiGrid(height, width, True)
            self.schedule = RandomActivation(self)
            # Create agents
            for i in range(self.num_agents):
                a = MoneyAgent(i)
                self.schedule.add(a)
                # Add the agent to a random grid cell
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(a, (x, y))

Under the hood, each agent's position is stored in two ways: the agent is contained in the grid in the cell it is currently in, and the agent has a ``pos`` variable with an (x, y) coordinate tuple. The ``place_agent`` method adds the coordinate to the agent automatically.

Now we need to add to the agents' behaviors, letting them move around and only give money to their cell-mates (as it were).


** THIS DOC IS IN PROGRESS **




.. _`virtual environment`: http://docs.python-guide.org/en/latest/dev/virtualenvs/

.. [Dragulescu2002] Drăgulescu, Adrian A., and Victor M. Yakovenko. “Statistical Mechanics of Money, Income, and Wealth: A Short Survey.” arXiv Preprint Cond-mat/0211175, 2002. http://arxiv.org/abs/cond-mat/0211175.



