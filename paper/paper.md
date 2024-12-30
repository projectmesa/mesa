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
  - name: Jackie Kazil
    orcid: 0000-0002-8300-7384
    affiliation: "3"
affiliations:
  - name: Delft University of Technology (Faculty of Technology, Policy and Management), the Netherlands
    index: 1
  - name: Independent Researcher, Germany
    index: 2
  - name: George Mason University (Department of Computational Social Science), United States
    index: 3
  - name: University at Buffalo (Department of Geography), United States
    index: 4
date: 30 December 2024
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
Mesa is an open-source Python framework for agent-based modeling (ABM) that enables researchers to create, analyze, and visualize agent-based simulations. Mesa provides a comprehensive set of tools and abstractions for modeling complex systems, with capabilities spanning from basic agent management to sophisticated representation of spaces within which agents interact. First released in 2014 and published in @masad2015 (with updates published in @kazil2020), this paper presents Mesa in its current version (3.1.1) as of late 2024.

# Statement of need
Agent-based models (ABMs), or artificial societies, are composed of autonomous heterogeneous agents interacting locally with other agents. These interactions give rise to emergent phenomena. The aggregate dynamics of a system under study emerge from these local interactions [@epstein_axtell_1996] [@epstein1999]. This type of modeling quickly grew more sophisticated, requiring frameworks to execute them. This led to the establishment of [NetLogo](https://ccl.northwestern.edu/netlogo/) and [MASON](https://cs.gmu.edu/~eclab/projects/mason/).

However, before Mesa, there was no modern Python-based framework for ABMs that integrated with the scientific Python ecosystem. Since it’s creation in 2014, Mesa has been applied to modeling everything from economics and sociology to ecology and epidemiology and has been cited in more than 500 papers and 800 authors. Today, Mesa advanced usability and stabilized functionality with its most recent major release (3+). These features include enhanced management of agents, data collection advancements, improved visualization framework, and making it easier for researchers to create and analyze complex simulations.

# Core capabilities
Mesa is a Python-based framework for ABM that provides a comprehensive set of tools for creating, running, and analyzing ABMs. Mesa integrates with the wider scientific Python ecosystem with libraries such as [NumPy](https://numpy.org/), [pandas](https://pandas.pydata.org/), [Matplotlib](https://matplotlib.org/), [NetworkX](https://networkx.org/), and more. Mesa is implemented in pure Python (3.11+) with a modular architecture separating:
1. Core ABM components (*i.e.,* agents, spaces, agent activation, control over random numbers)
2. Data collection and support for model experimentation
3. Visualization systems

This design allows selective use of components while enabling extension and customization.

## Core ABM components
### Model
The central class in Mesa is the Model. The user extends the model. Within it, the user instantiates the space and populates it with agent instances. Since ABMs are typically stochastic simulations, the model also controls the random number generation.

### Agents
Central to ABMs are the autonomous heterogeneous agents. Mesa provides a variety of base agent classes which the user can subclass. In its most basic implementation, such an agent subclass specifies the `__init__` and `step` method. Any subclass of the basic mesa agent subclass registers itself with the specified model instance, and via `agent.remove` it will remove itself from the model. It is strongly encouraged to rely on `remove`, and even extend it if needed to ensure agents are fully removed from the simulation.

### Agent management
One significant advancement of Mesa 3+ is expanded functionality around agent management. The new [`AgentSet`](https://mesa.readthedocs.io/latest/apis/agent.html#mesa.agent.AgentSet) class provides methods that allow users to filter, group, and analyze agents, making it easier to express complex model logic.

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
Mesa 3 provides both discrete (cell-based) and continuous space implementations. In discrete spaces, an agent occupies a cell. Mesa implements discrete spaces using a doubly-linked structure where each cell maintains connections to its neighbors. The framework includes several discrete space variants with a consistent API:

- Grid-based: `OrthogonalMooreGrid`, `OrthogonalVonNeumanGrid`, and `HexGrid`
- Network-based: `Network` for graph-based topologies
- Voronoi-based: `VoronoiMesh` for irregular tessellations

Example grid creation:
```python
grid = OrthogonalVonNeumannGrid(
    (width, height), torus=False, random=model.random
)
```

Mesa provides specialized agent classes for spatial interactions in the discrete spaces:

- `FixedAgent`: Is assigned to a cell, can access this cell, but cannot move to another cell.
- `CellAgent`: Can move between cells
- `Grid2DMovingAgent`: Extends `CellAgent` with directional movement methods

All discrete spaces support PropertyLayers - efficient numpy-based arrays for storing cell-level properties:
```python
grid.create_property_layer("elevation", default_value=10)
high_ground = grid.elevation.select_cells(lambda x: x > 50)
```

For models where agents need to move continuously through space rather than between discrete locations, `ContinuousSpace` allows agents to occupy any coordinate within defined boundaries:
```python
space = ContinuousSpace(x_max, y_max, torus=True)
space.move_agent(agent, (new_x, new_y))
```

### Time advancement
Typically, ABMs rely on incremental time progression or ticks. For each tick, the step method of the model is called. This activates the agents in some way. The most frequently implemented approach is shown below, which runs a model for 100 ticks.

```python
model = Model(seed=42)

for _ in range(100):
    model.step()
```

Generally, within the step method of the model, one activates all the agents. The newly added `AgentSet` class provides a more flexible way to activate agents replacing the fixed patterns previously available.

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
Mesa's visualization system, [SolaraViz](https://mesa.readthedocs.io/latest/tutorials/visualization_tutorial.html), provides interactive browser-based model exploration:

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
Mesa has been applied across diverse domains, including:

- Sustainability and food security modeling, including supply chain optimization and resource allocation [@namany2020sustainable]
- Infrastructure resilience and post-disaster recovery planning [@sun2020post]
- Building stock modeling for energy demand and emissions analysis [@nageli2020towards]
- Market modeling, including renewable energy auctions and consumer behavior [@anatolitis2017putting]
- Transportation optimization, such as combined truck-drone delivery routing [@leon2022multi]
- Recommender systems analysis examining consumer-business value tradeoffs over time [@ghanem2022balancing]
- Climate adaptation modeling examining household-level behavioral responses to environmental shocks [@taberna2023uncertainty]

These applications showcase Mesa's versatility in modeling complex systems with autonomous interacting agents, whether representing individual consumers, infrastructure components, buildings, or vehicles.

The framework is particularly suited for:
- Models with heterogeneous agent populations
- Systems requiring sophisticated spatial interactions
- Interactive exploration of parameter spaces
- Teaching and learning agent-based modeling

# Community and ecosystem
Mesa has grown into a complete ecosystem with extensions including:
- [Mesa-Geo](https://github.com/projectmesa/mesa-geo) for geospatial modeling [wang2022mesa]
- [Mesa-Frames](https://github.com/projectmesa/mesa-frames) for high-performance simulations
- A rich collection of community-contributed extensions, [example models](https://github.com/projectmesa/mesa-examples), and tutorials

# Acknowledgements
The advancements leading to Mesa 3 were developed by six maintainers (the authors) and an active community with over 140 [contributors](https://github.com/projectmesa/mesa/graphs/contributors). We would especially like to thank [David Masad](https://github.com/dmasad) for his foundational work on Mesa and [rht](https://github.com/rht) for his work as maintainer in 2022 to 2024.

# Conclusions
Mesa 3 introduces significant advancements to the Python ABM framework, enhancing the core toolkit with greater control, interactivity, and speed for researchers. These notable improvements, paired with its foundational integration with the scientific Python ecosystem, modular architecture, and active community, make it an indispensable tool for researchers across disciplines working in Python who need to create and analyze agent-based models.

# References
