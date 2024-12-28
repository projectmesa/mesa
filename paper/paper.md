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
  - name: Jan Kwakkel
    orcid: 0000-0001-9447-2954
  - name: Vincent Hess
  - name: Thomas D. Pike
    orcid: 0000-0003-1576-0283
  - name: Boyu Wang
    orcid: 0000-0001-9879-2138
  - name: rht
  - name: Jackie Kazil
    orcid: 0000-0002-6666-8506
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
Mesa is an open-source Python framework for agent-based modeling (ABM) that enables researchers to create, analyze, and visualize agent-based simulations. Mesa provides a comprehensive set of tools and abstractions for modeling complex systems, with capabilities spanning from basic agent management to sophisticated representation of spaces within which agents interact. First introduced in 2014 [@masad2015], with updates published in [@kazil2020], this paper presents Mesa in its current version (3.1.1) as of late 2024.

# Statement of need
Agent-based models, or artificial societies, are composed of autonomous heterogeneous agents positioned in one or more space(s). Given a space, agents have *local* interactions with their neighbors. The aggregate dynamics of a system under study emerge from these local interactions [@epstein_axtell_1996][@epstein1999]. Simulations quickly grew more sophisticated, requiring frameworks to execute them. This led to the establishment of  NetLogo and MASON.

However, before Mesa, there was no modern Python-based framework for ABM that integrated with the scientific Python ecosystem. Mesa has been applied to modeling everything from economics and sociology to ecology and epidemiology and has been cited in more than 500 papers and 800 authors. As the adoption of Mesa grew, key features were added and present in Mesa 3.0+ to advance and stabilize functionality. These features include enhanced management of agents, data collection advancements, improved visualization framework, and making it easier for researchers to create and analyze complex simulations.

# Core capabilities
Mesa offers a Python-based framework for ABM that integrates with the wider scientific python ecosystem. Mesa provides a comprehensive set of tools for creating, running, and analyzing agent-based models while maintaining Python's emphasis on readability and simplicity. Mesa is implemented in pure Python (3.11+) with a modular architecture separating:
1. Core ABM components (*i.e.,* agents, spaces, agent activation, control over random numbers)
2. Data collection and support for model experimentation
3. Visualization systems

This design allows selective use of components while enabling extension and customization. The framework integrates with the scientific Python ecosystem including NumPy, pandas, and Matplotlib.

## Core ABM components
The central class in MESA is the Model. Mesa provides a base model class that the user is expected to extend. Within this model, the user instantiates the space and populates it with agent instances. Since (agent-based models) ABMs are typically stochastic simulations, the model also controls the random number generation.

### Agents
Central to ABMs are the autonomous heterogeneous agents. Mesa provides a variety of base agent classes which the user can subclass. In its most basic implementation, such an agent subclass specifies the `__init__` and `step` method. Any subclass of the basic mesa agent subclass registers itself with the specified model instance, and via `agent.remove` it will remove itself from the model. It is strongly encouraged to rely on `remove`, and even extend it if needed to ensure agents are fully removed from the simulation.

### Agent management
The management of large groups of agents is critical in ABMs. Mesa's agent management system is built around the concept of AgentSet, which provide intuitive ways to organize and manipulate collections of agents:

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
Mesa 3 provides multiple types of spaces for agent interactions, broadly categorized into discrete (cell-based) and continuous spaces. Each type serves different modeling needs while maintaining a consistent API.

#### Discrete Spaces
In discrete spaces, agents occupy specific cells or nodes. Mesa offers several implementations:

- Grid-based spaces (OrthogonalMooreGrid, OrthogonalVonNeumannGrid, Hexgrid)
- Network spaces where agents occupy nodes
- Voronoi meshes for irregular cell patterns

These spaces use a doubly-linked structure where cells maintain connections to their neighbors. A key feature is the PropertyLayer system, which enables efficient storage and manipulation of environmental data across the space:

```python
# Create a grid with an elevation layer
grid = OrthogonalMooreGrid((width, height), torus=False)
grid.create_property_layer("elevation", default_value=10)

# Select cells above a threshold
high_ground = grid.elevation.select_cells(lambda x: x > 50)
```

To facilitate agent-space interactions, Mesa provides specialized agent classes:
- FixedAgent: Remains at its assigned cell
- CellAgent: Can move between cells
- Grid2DMovingAgent: Adds directional movement shortcuts

#### Continuous Space
For models requiring precise positioning, continuous space allows agents to have any coordinate location:

```python
space = ContinuousSpace(x_max, y_max, torus=True)
space.move_agent(agent, (new_x, new_y))
```

All space types can be configured as toroidal (wrapping at edges) or bounded.

### Time advancement
Typically, agent-based models rely on incremental time progression or ticks. For each tick, the step method of the model is called. This activates the agents in some way. The most frequently implemented approach is shown below, which runs a model for 100 ticks.

```python

model = Model(seed=42)

for _ in range(100):
    model.step()

```

Generally, within the step method of the model, one activates all the agents. The AgentSet can be used for this. Some common agent activation patterns are shown below, which alsocan be combined to create more sophisticated and complex ones.

1. Deterministic activation of agent
```python
model.agents.do("step")  # Sequential activation

model.agents.shuffle_do("step")  # Random activation

# Multi-stage activation:
for stage in ["move", "eat", "reproduce"]:
    model.agents.do(stage)

# Activation by agent subclass:
for klass in model.agent_types:
    model.agents_by_type[klass].do("step")
```

Mesa also supports next-event time progression. In this approach, the simulation consists of time-stamped events that are executed chronologically, with the simulation clock advancing to each event's timestamp. This enables both pure discrete event-based models and hybrid approaches combining incremental time progression with event scheduling on the ticks as shown below.. This latter hybrid approach allows combining traditional ABM time steps with the flexibility and potential performance benefits of event scheduling.

```python
# Pure event-based scheduling
simulator = DiscreteEventSimulator()
model = Model(seed=42, simulator=simulator)
simulator.schedule_event_relative(some_function, 3.1415)

# Hybrid time-step and event scheduling
model = Model(seed=42, simulator=ABMSimulator())
model.simulator.schedule_event_next_tick(some_function)
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
- A rich collection of community-contributed extensions, example models, and tutorials

The advancements leading to Mesa 3 were developed by six maintainers (the authors) and an active community with over 130 contributors.

# Conclusions
Mesa 3 introduces significant advancements to the Python ABM framework, enhancing the core toolkit with greater control, interactivity, and speed for researchers. These notable improvements, paired with its foundational integration with the scientific Python ecosystem, modular architecture, and active community, make it an indispensable tool for researchers across disciplines working in Python who need to create and analyze agent-based models.
