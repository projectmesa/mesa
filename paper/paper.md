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
Mesa is an open-source Python framework for agent-based modeling (ABM) that enables researchers to create, analyze and visualize agent-based simulations. Mesa provides a comprehensive set of tools and abstractions for modeling complex systems, with capabilities spanning from basic agent management to sophisticated environmental modeling and interactive visualization. By leveraging Python's scientific computing ecosystem, Mesa offers a powerful yet accessible platform for researchers across disciplines. This paper presents Mesa in its current version (3.1.1) as of late 2024.

# Statement of need
Agent-based modeling is a powerful approach for studying complex systems across many disciplines, from economics and sociology to ecology and epidemiology. As simulations grow more sophisticated, researchers need frameworks that can efficiently handle complex agents and environments while remaining approachable and flexible. While established platforms like NetLogo and MASON exist, there is a clear need for a modern, Python-based framework that integrates with the scientific Python ecosystem and provides robust ABM capabilities.

Mesa addresses this need by offering a modular, extensible framework that leverages Python's strengths in scientific computing and data analysis. It provides a comprehensive set of tools for creating, running, and analyzing agent-based models while maintaining Python's emphasis on readability and simplicity.

# Core capabilities
Mesa is implemented in pure Python (3.11+) with a modular architecture separating:
1. Core ABM components (agents, spaces, model management)
2. Data collection and analysis
3. Visualization systems

This design allows selective use of components while enabling extension and customization. The framework integrates with the scientific Python ecosystem including NumPy, pandas, and Matplotlib.

## Core ABM components
### Agent management
Mesa's agent management system is built around the central concept of AgentSets, which provide intuitive ways to organize and manipulate collections of agents:

```python
# Select wealthy agents and calculate average wealth
wealthy = model.agents.select(lambda a: a.wealth > 1000)
avg_wealth = wealthy.agg("wealth", func=np.mean)

# Group agents by type and apply behaviors
grouped = model.agents.groupby("species")
for species, agents in grouped:
    agents.shuffle_do("reproduce")
```

The framework automatically handles agent lifecycle management, including:
- Unique ID assignment
- Agent registration and removal
- Type-based organization
- Efficient collective operations

### Spatial modeling
Mesa supports multiple approaches to spatial modeling:

1. Grid-based spaces:
```python
grid = MultiGrid(width, height, torus=True)
grid.place_agent(agent, (x, y))
neighbors = grid.get_neighbors(pos, moore=True)
```

2. Network spaces:
```python
network = NetworkGrid(networkx_graph)
network.get_neighbors(agent, include_center=False)
```

3. Continuous spaces:
```python
space = ContinuousSpace(x_max, y_max, torus=True)
space.move_agent(agent, (new_x, new_y))
```

Environmental properties can be modeled using PropertyLayers:
```python
elevation = PropertyLayer("elevation", width, height)
grid.add_property_layer(elevation)
high_ground = grid.properties["elevation"].select_cells(lambda x: x > 50)
```

For more sophisticated environmental modeling, the experimental cell space system enables active cells with their own properties and behaviors:

```python
class ForestCell(Cell):
    def step(self):
        if self.on_fire:
            self.spread_fire()
```

### Time management
Mesa offers flexible approaches to time management:

1. Simple step-based progression:
```python
model.agents.shuffle_do("step")  # Random activation
```

2. Multi-stage activation:
```python
for stage in ["move", "eat", "reproduce"]:
    model.agents.do(stage)
```

3. Event-based scheduling for non-uniform time steps:
```python
scheduler = DiscreteEventScheduler(model)
scheduler.add_event(SimEvent(time=3.5, target=agent))
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
