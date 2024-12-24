---
title: 'Mesa 3: Agent-based modelling with Python in 2024'
tags:
  - Python
  - agent-based modeling
  - simulation
  - complex systems
  - social science
  - complexity science
  - modeling
authors:
  - name: Ewout ter Hoeven
    orcid: 0009-0002-0805-3425
    affiliation: "1"
  - name: Jan Kwakkel
    orcid: 0000-0001-9447-2954
    affiliation: "1"
  - name: Vincent Hess
    affiliation: "2"
  - name: Thomas D. Pike
    orcid: 0000-0003-1576-0283
    affiliation: "3"
  - name: Boyu Wang
    orcid: 0000-0001-9879-2138
    affiliation: "4"
  - name: rht
    affiliation: "5"
  - name: Jackie Kazil
    orcid: 0000-0002-6666-8506
    affiliation: "6"
affiliations:
  - name: Delft University of Technology (Faculty of Technology, Policy and Management)
    index: 1
  - name: Independent Researcher, Germany
    index: 2
  - name: Independent Researcher, USA
    index: 3
  - name: University at Buffalo (Department of Geography)
    index: 4
  - name: Independent Researcher
    index: 5
  - name: George Mason University (Department of Computational Social Science)
    index: 6
date: 5 December 2024
bibliography: paper.bib

# Optional fields
repository-code: https://github.com/projectmesa/mesa
repository-docs: https://mesa.readthedocs.io/
url: https://github.com/projectmesa
license: Apache-2.0
keywords: agent-based modeling, complex systems, Python, simulation
preferred-citation: article
---

# Summary
Mesa is an open-source Python framework for agent-based modeling (ABM) that enables researchers to create, analyze, and visualize agent-based simulations. Mesa provides a comprehensive set of tools and abstractions for modeling complex systems, with capabilities spanning from basic agent management to sophisticated representation of spaces within which agents interact. By leveraging Python's scientific computing ecosystem, Mesa offers a powerful yet accessible platform for researchers across disciplines. This paper presents Mesa in its current version (3.1.1) as of late 2024.

# Statement of need
Agent-based models, or artificial societies, are composed of autonomous heteregouneous agents that are positioned in one or more space(s). Given a space, agents have *local* interactions with their neighbors. The aggregate dynamics of a system under study emerges from these local interactions (Epstein, chapter 2, AGENT-BASED COMPUTATIONAL MODELS AND GENERATIVE SOCIAL SCIENCE; Epstein Axtel (1996)). That is, "*situate an initial population of autonomous heterogeneous agents in a relevant spatial environment; allow them to interact according to simple local rules, and thereby generate—or “grow”—the macroscopic regularity from the bottom up*" (Epstein, axtel 1996; add page number!).

Agent-based modeling is a powerful approach for studying complex systems across many disciplines, from economics and sociology to ecology and epidemiology. As simulations grow more sophisticated, researchers need frameworks that can efficiently handle complex agents and their environments, while remaining approachable and flexible. While established platforms like NetLogo and MASON exist, there is a clear need for a modern, Python-based framework for ABM that integrates with the scientific Python ecosystem.

# Core capabilities
Mesa offers a Python based framework for ABM that integrates with the wider scientific python ecosystem. Mesa provides a comprehensive set of tools for creating, running, and analyzing agent-based models while maintaining Python's emphasis on readability and simplicity. Mesa is implemented in pure Python (3.11+) with a modular architecture separating:
1. Core ABM components (*i.e.,* agents, spaces, agent activation, control over random numbers)
2. Data collection and support for model experimentation
3. Visualization systems

This design allows selective use of components while enabling extension and customization. The framework integrates with the scientific Python ecosystem including NumPy, pandas, and Matplotlib.

## Core ABM components
The central class in MESA is the Model. Mesa provides a base model class that the user is expected to extend. Within this model, the user instantiates the space and populates it with agent instances. Since ABMs are typically stochastic simulations, the model also controls the random number generation.

### Agents
Central to ABMs are the autonomous heterogeneous agents. Mesa provides a variety of base agent classes which the user can subclass. In its most basic implementation, such an agent subclass specifies the  `__init__` and `step` method. Any subclass of the basic mesa agent subclass registers itself with the specified model instance, and via `agent.remove` it will remove itself from the model. It is strongly encouraged to rely on `remove`, and even extent it if needed to ensure agents are fully removed from the simulation.

### Agent management
The management of large groups of agents is criticical in ABMs. Mesa's agent management system is built around the central concept of AgentSet, which provide intuitive ways to organize and manipulate collections of agents:

```python
# Select wealthy agents and calculate average wealth
wealthy = model.agents.select(lambda a: a.wealth > 1000)
avg_wealth = wealthy.agg("wealth", func=np.mean)

# Group agents by type and apply behaviors
grouped = model.agents.groupby("species")
for species, agents in grouped:
    agents.shuffle_do("reproduce")
```

### Spaces
Mesa offers a variety of spaces within which agents can be located. A basic distinction is between discrete or cell-based spaces, and continuous space. In discrete spaces, the space consists of a collection of cells and agents occupy a cell. Examples of this include orthogonal grids, hexgrids, voroinoi meshes, or networks. In a continuous space, in contrast, an agent has a location.

Mesa comes with a wide variety of discrete spaces, including OrthogonalMooreGrid, OrthogonalVonNeumanGrid, Hexgrid, Network, and VoroinoiMesh. These are all implemented using a doubly linked data structure where each cell has connections to its neighboring cells. The different discrete spaces differ with respect to how they are "wired-up", but the API is uniform across all of them.

Mesa also offers 3 subclasses of the Agent class that are designed to be used in conjunction with these discrete spaces: FixedAgent, CellAgent, and Grid2DMovingAgent. FixedAgent is assigned to a given cell and can access this cell via `self.cell`. However, once assigned to a given cell, it can not be moved. A CellAgent, like a FixedAgent, has access to the cell it currently occupies. However, it can update this attribute making it possible to move around. A Grid2DMovingAgent extends CellAgent by offering a move method with short hand for the direction of movement.

. Grid-based spaces:
```python
grid = OrthogonalVonNeumannGrid(
    (width, height), torus=False, random=model.random
)

# create a network space with a capacity of 1 agent per node
grid = Network(networkx_graph, capacity=1, random=model.random)
```

2. Network spaces:
```python
network = NetworkGrid(networkx_graph)
network.get_neighbors(agent, include_center=False)
```

The OrthogonalMooreGrid, OrthogonalVonNeumanGrid and Hexgrid come with support for numpy based layers with additional data: PropertyLayers. Cells have attribute access to their value in each of these property layers, while the entire layer can be accessed from the space itself.

```python
# initialize a property layer with a default value
grid.create_property_layer("elevation", default_value=10)

# get indices for cells with elevation above 50
high_ground = grid.elevation.select_cells(lambda x: x > 50)
```


2. Continuous spaces:

```python
space = ContinuousSpace(x_max, y_max, torus=True)
space.move_agent(agent, (new_x, new_y))
```




### Time advancement
Typically agent based models rely on discrete time advancement, or ticks. For each tick, the step method of the model is called. This in turn activates activates the agents in some way. The most frequent encountered approach is shown below, which runs a model for 100 ticks.

```python

model = Model(seed=42)

for _ in range(100):
    model.step()

```

Generally, within the step method of the model, one activates all the agents. The AgentSet class can be used for this. Some common agent activation patterns are shown below. Evidently, these activation patterns can be combined to create more sophisticated and complex activation patterns.

1. Deterministic activation of agent
```python
model.agents.do("step")  # Random activation

model.agents.shuffle_do("step")  # Random activation

# Multi-stage activation:
for stage in ["move", "eat", "reproduce"]:
    model.agents.do(stage)

# Activation by agent subclass:
for klass in model.agent_types:
    model.agents_by_type[klass].do("step")
```

A more advanced alternative to discrete time advancement is discrete event simulation. Here, the simulation consists of a series of time stamped events. The simulation executes the events for a given timestep, Next, the simulation clock is advanced to the time stamp of the next event. Mesa offers basic support for discrete event simulation using a Discrete event simulator. The design is inspired by Ziegler (add ref), and the java-based DSOL library (add ref).


1. Event-based scheduling for non-uniform time steps:
```python
devs_simulator = DiscreteEventSimulator()
model = Model(seed=42, simulator=devs_simulator)

devs_simulator.schedule_event_relative(some_function_to_execute, 3.1415)
devs_simulator.run_until(end_time)
```

It is also possible to create hybrid models that combine discrete time advancement as typically seen in agent based models, with event scheduling. For this, MESA comes with an ABMSimulator. This simulator has integer based time steps. It automatically schedules the step method of the model for each time tick. However, it is also possible to schedule events on these ticks. This allows for hybrid models combining the ease of discrete time advancement seen in typical ABMs, with the power, flexibility, and potential for substantial runtime reductions of event scheduling.

2. Hybrid discrete time advancement with event scheduling
```python
abm_simulator = ABMSimulator()
model = Model(seed=42, simulator=abm_simulator)

abm_simulator.schedule_event_next_tick(some_function_to_execute)
abm_simulator.run_until(end_time)
```


## Visualization
Mesa's visualization system, SolaraViz, provides interactive browser-based model exploration:

```python
visualization = SolaraViz(
    model,
    [
        make_space_component(agent_portrayal),
        make_plot_component(["population", "average_wealth"]),
        lambda m: f"Step {m.steps}: {len(m.agents)} agents"
    ],
    model_params=parameter_controls
)
```

![A screenshot of the WolfSheep Model in Mesa](../docs/images/wolf_sheep.png)

Key features include:
- Interactive model controls
- Real-time data visualization
- Customizable agent and space portrayal
- Support for multiple visualization types including grids, networks, and charts

## Experimentation and analysis

### Data collection
Mesa's DataCollector enables systematic data gathering during simulations:

```python
collector = DataCollector(
    model_reporters={"population": lambda m: len(m.agents)},
    agent_reporters={"wealth": "wealth"},
    agenttype_reporters={
        Predator: {"kills": "kills_count"},
        Prey: {"distance_fled": "flight_distance"}
    }
)
```

The collected data integrates seamlessly with pandas for analysis:
```python
model_data = collector.get_model_vars_dataframe()
agent_data = collector.get_agent_vars_dataframe()
```

### Parameter sweeps
Mesa supports systematic parameter exploration:

```python
parameters = {
    "num_agents": range(10, 100, 10),
    "growth_rate": [0.1, 0.2, 0.3]
}
results = mesa.batch_run(
    MyModel,
    parameters,
    iterations=5,
    max_steps=100
)
```

### Reactive programming
The experimental Mesa Signals system enables reactive programming patterns:

```python
class ReactiveAgent(Agent):
    wealth = Observable(initial=1)
    happiness = Computed(lambda self: self.wealth > 10)
```

# Applications
Mesa has been applied across diverse domains including:
- Epidemiology and public health modeling
- Economic and market simulations
- Social network analysis
- Urban planning and transportation
- Ecological modeling

The framework is particularly suited for:
- Models with heterogeneous agent populations
- Systems requiring sophisticated spatial interactions
- Interactive exploration of parameter spaces
- Teaching and learning agent-based modeling

# Community and ecosystem
Mesa has grown into a complete ecosystem with extensions including:
- [Mesa-Geo](https://github.com/projectmesa/mesa-geo) for geospatial modeling
- [Mesa-Frames](https://github.com/projectmesa/mesa-frames) for high-performance simulations
- A rich collection of example models and tutorials

The framework is developed by six maintainers (the authors) and an active community with over 130 contributors.

# Conclusions
Mesa provides a comprehensive Python framework for agent-based modeling that combines powerful capabilities with accessibility and extensibility. Its integration with the scientific Python ecosystem, modular architecture, and active community make it a valuable tool for researchers across disciplines who need to create and analyze agent-based models.
