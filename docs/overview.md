# Mesa Overview

Mesa is a modular framework for building, analyzing and visualizing agent-based models.

**Agent-based models** are computer simulations involving multiple entities (the agents) acting and interacting with one another based on their programmed behavior. Agents can be used to represent living cells, animals, individual humans, even entire organizations or abstract entities. Sometimes, we may have an understanding of how the individual components of a system behave, and want to see what system-level behaviors and effects emerge from their interaction. Other times, we may have a good idea of how the system overall behaves, and want to figure out what individual behaviors explain it. Or we may want to see how to get agents to cooperate or compete most effectively. Or we may just want to build a cool toy with colorful little dots moving around.

## Mesa Modules

Mesa is modular, meaning that its modeling, analysis and visualization components are kept separate but intended to work together. The modules are grouped into three categories:

1. **Modeling:** Modules used to build the models themselves: a model and agent classes, a scheduler to determine the sequence in which the agents act, and space for them to move around on.
2. **Analysis:** Tools to collect data generated from your model, or to run it multiple times with different parameter values.
3. **Visualization:** Classes to create and launch an interactive model visualization, using a server with a JavaScript interface.

### Modeling modules

Most models consist of one class to represent the model itself; one class (or more) for agents; a scheduler to handle time (what order the agents act in), and possibly a space for the agents to inhabit and move through. These are implemented in Mesa's modeling modules:

- `mesa.Model`, `mesa.Agent`
- [mesa.time](apis/time.html)
- [mesa.space](apis/space.html)

The skeleton of a model might look like this:

```python
import mesa

class MyAgent(mesa.Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name

    def step(self):
        print("{} activated".format(self.name))
        # Whatever else the agent does when activated

class MyModel(mesa.Model):
    def __init__(self, n_agents):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(10, 10, torus=True)
        for i in range(n_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)
            coords = (self.random.randrange(0, 10), self.random.randrange(0, 10))
            self.grid.place_agent(a, coords)

    def step(self):
        self.schedule.step()
```

If you instantiate a model and run it for one step, like so:

```python
model = MyModel(5)
model.step()
```

You should see agents 0-4, activated in random order. See the [tutorial](tutorials/intro_tutorial.html) or API documentation for more detail on how to add model functionality.

To bootstrap a new model install mesa and run `mesa startproject`

### Analysis modules

If you're using modeling for research, you'll want a way to collect the data each model run generates. You'll probably also want to run the model multiple times, to see how some output changes with different parameters. Data collection and batch running are implemented in the appropriately-named analysis modules:

- [mesa.datacollection](apis/datacollection.html)
- [mesa.batchrunner](apis/batchrunner.html)

You'd add a data collector to the model like this:

```python
import mesa

# ...

class MyModel(mesa.Model):
    def __init__(self, n_agents):
        # ...
        self.dc = mesa.DataCollector(model_reporters={"agent_count":
                                    lambda m: m.schedule.get_agent_count()},
                                agent_reporters={"name": lambda a: a.name})

    def step(self):
        self.schedule.step()
        self.dc.collect(self)
```

The data collector will collect the specified model- and agent-level data at each step of the model. After you're done running it, you can extract the data as a [pandas](http://pandas.pydata.org/) DataFrame:

```python
model = MyModel(5)
for t in range(10):
    model.step()
model_df = model.dc.get_model_vars_dataframe()
agent_df = model.dc.get_agent_vars_dataframe()
```

To batch-run the model while varying, for example, the n_agents parameter, you'd use the `batch_run` function:

```python
import mesa

parameters = {"n_agents": range(1, 20)}
mesa.batch_run(
    MyModel,
    parameters,
    max_steps=10,
)
```

As with the data collector, once the runs are all over, you can extract the data as a data frame.

```python
batch_df = batch_run.get_model_vars_dataframe()
```
