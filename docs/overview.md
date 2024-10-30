# Mesa Overview
Mesa is a modular framework for building, analyzing and visualizing agent-based models.

**Agent-based models** are computer simulations involving multiple entities (the agents) acting and interacting with one another based on their programmed behavior. Agents can be used to represent living cells, animals, individual humans, even entire organizations or abstract entities. Sometimes, we may have an understanding of how the individual components of a system behave, and want to see what system-level behaviors and effects emerge from their interaction. Other times, we may have a good idea of how the system overall behaves, and want to figure out what individual behaviors explain it. Or we may want to see how to get agents to cooperate or compete most effectively. Or we may just want to build a cool toy with colorful little dots moving around.

## Mesa Modules

Mesa is modular, meaning that its modeling, analysis and visualization components are kept separate but intended to work together. The modules are grouped into three categories:

1. **Modeling:** Classes used to build the models themselves: a model and agent classes, space for them to move around in, and built-in functionality for managing agents.
2. **Analysis:** Tools to collect data generated from your model, or to run it multiple times with different parameter values.
3. **Visualization:** Classes to create and launch an interactive model visualization, using a browser-based interface.

### Modeling modules

Most models consist of one class to represent the model itself and one or more classes for agents. Mesa provides built-in functionality for managing agents and their interactions. These are implemented in Mesa's modeling modules:

- [mesa.model](apis/model)
- [mesa.agent](apis/agent)
- [mesa.space](apis/space)

The skeleton of a model might look like this:

```python
import mesa

class MyAgent(mesa.Agent):
    def __init__(self, model, age):
        super().__init__(model)
        self.age = age

    def step(self):
        self.age += 1
        print(f"Agent {self.unique_id} now is {self.age} years old")
        # Whatever else the agent does when activated

class MyModel(mesa.Model):
    def __init__(self, n_agents):
        super().__init__()
        self.grid = mesa.space.MultiGrid(10, 10, torus=True)
        for _ in range(n_agents):
            initial_age = self.random.randint(0, 80)
            a = MyAgent(self, initial_age)
            coords = (self.random.randrange(0, 10), self.random.randrange(0, 10))
            self.grid.place_agent(a, coords)

    def step(self):
        self.agents.shuffle_do("step")
```

If you instantiate a model and run it for one step, like so:

```python
model = MyModel(5)
model.step()
```

You should see agents 1-5, activated in random order. See the [tutorial](tutorials/intro_tutorial) or API documentation for more detail on how to add model functionality.

To bootstrap a new model install mesa and run `mesa startproject`

### AgentSet and model.agents
Mesa 3.0 makes `model.agents` and the AgentSet class central in managing and activating agents.

#### model.agents
`model.agents` is an AgentSet containing all agents in the model. It's automatically updated when agents are added or removed:

```python
# Get total number of agents
num_agents = len(model.agents)

# Iterate over all agents
for agent in model.agents:
    print(agent.unique_id)
```

#### AgentSet Functionality
AgentSet offers several methods for efficient agent management:

1. **Selecting**: Filter agents based on criteria.
   ```python
   high_energy_agents = model.agents.select(lambda a: a.energy > 50)
   ```
2. **Shuffling and Sorting**: Randomize or order agents.
   ```python
   shuffled_agents = model.agents.shuffle()
   sorted_agents = model.agents.sort(key="energy", ascending=False)
   ```
3. **Applying methods**: Execute methods on all agents.
   ```python
   model.agents.do("step")
   model.agents.shuffle_do("move")  # Shuffle then apply method
   ```
4. **Aggregating**: Compute aggregate values across agents.
   ```python
   avg_energy = model.agents.agg("energy", func=np.mean)
   ```
5. **Grouping**: Group agents by attributes.
   ```python
   grouped_agents = model.agents.groupby("species")

   for _, agent_group in grouped_agents:
      agent_group.shuffle_do()
   species_counts = grouped_agents.count()
   mean_age_by_group = grouped_agents.agg("age", np.mean)
   ```
`model.agents` can also be accessed within a model instance using `self.agents`.

These are just some examples of using the AgentSet, there are many more possibilities, see the [AgentSet API docs](apis/agent).

### Analysis modules

If you're using modeling for research, you'll want a way to collect the data each model run generates. You'll probably also want to run the model multiple times, to see how some output changes with different parameters. Data collection and batch running are implemented in the appropriately-named analysis modules:

- [mesa.datacollection](apis/datacollection)
- [mesa.batchrunner](apis/batchrunner)

You'd add a data collector to the model like this:

```python
import mesa
import numpy as np

# ...

class MyModel(mesa.Model):
    def __init__(self, n_agents):
        super().__init__()
        # ... (model initialization code)
        self.datacollector = mesa.DataCollector(
            model_reporters={"mean_age": lambda m: m.agents.agg("age", np.mean)},
            agent_reporters={"age": "age"}
        )

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
```

The data collector will collect the specified model- and agent-level data at each step of the model. After you're done running it, you can extract the data as a [pandas](http://pandas.pydata.org/) DataFrame:

```python
model = MyModel(5)
for t in range(10):
    model.step()
model_df = model.datacollector.get_model_vars_dataframe()
agent_df = model.datacollector.get_agent_vars_dataframe()
```

To batch-run the model while varying, for example, the n_agents parameter, you'd use the [`batch_run`](apis/batchrunner) function:

```python
import mesa

parameters = {"n_agents": range(1, 6)}
results = mesa.batch_run(
    MyModel,
    parameters,
    iterations=5,
    max_steps=100,
    data_collection_period=1,
)
```

The results are returned as a list of dictionaries, which can be easily converted to a pandas DataFrame for further analysis.

### Visualization
Mesa now uses a new browser-based visualization system called SolaraViz. This allows for interactive, customizable visualizations of your models. Here's a basic example of how to set up a visualization:

```python
from mesa.visualization import SolaraViz, make_space_component, make_plot_measure


def agent_portrayal(agent):
    return {"color": "blue", "size": 50}


model_params = {
    "N": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    }
}

page = SolaraViz(
    MyModel,
    [
        make_space_component(agent_portrayal),
        make_plot_measure("mean_age")
    ],
    model_params=model_params
)
page
```
This will create an interactive visualization of your model, including:

- A grid visualization of agents
- A plot of a model metric over time
- A slider to adjust the number of agents

You can also create custom visualization components using Matplotlib. For more advanced usage and customization options, please refer to the [visualization tutorial](tutorials/visualization_tutorial).

### Further resources
To further explore Mesa and its features, we have the following resources available:

#### Tutorials
- [Introductory Tutorial](tutorials/intro_tutorial): Learn how to create your first Mesa model.
- [Visualization Tutorial](tutorials/visualization_tutorial.html): Learn how to create interactive visualizations for your models.

#### API documentation
- [Mesa API reference](apis): Detailed documentation of Mesa's classes and functions.

#### Example models
- [Mesa Examples repository](https://github.com/projectmesa/mesa-examples): A collection of example models demonstrating various Mesa features and modeling techniques.

#### Migration guide
- [Mesa 3.0 Migration guide](migration_guide): If you're upgrading from an earlier version of Mesa, this guide will help you navigate the changes in Mesa 3.0.

#### Source Ccode and development
- [Mesa GitHub repository](https://github.com/projectmesa/mesa): Access the full source code of Mesa, contribute to its development, or report issues.
- [Mesa release notes](https://github.com/projectmesa/mesa/releases): View the detailed changelog of Mesa, including all past releases and their features.

#### Community and support
- [Mesa GitHub Discussions](https://github.com/projectmesa/mesa/discussions): Join discussions, ask questions, and connect with other Mesa users.
- [Matrix Chat](https://matrix.to/#/#project-mesa:matrix.org): Real-time chat for quick questions and community interaction.

Enjoy modelling with Mesa, and feel free to reach out!
