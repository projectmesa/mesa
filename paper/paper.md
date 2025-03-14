---
title: 'Mesa 3: Agent-based modeling with Python in 2025'
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
    orcid: 0000-0002-9242-8500
    affiliation: "2"
  - name: Thomas D. Pike
    orcid: 0000-0003-1576-0283
    affiliation: "3"
  - name: Boyu Wang
    orcid: 0000-0001-9879-2138
    affiliation: "4"
  - name: rht
    orcid: 0009-0002-6902-111X
    affiliation: "5"
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
  - name: Independent Researcher
    index: 5
date: 1 January 2025
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
Mesa is an open-source Python framework for agent-based modeling (ABM) that enables researchers to create, analyze, and visualize agent-based simulations. Mesa provides a comprehensive set of tools and abstractions for modeling complex systems, with capabilities spanning from basic agent management to sophisticated representation of spaces where agents interact. First released in 2014 and published in @masad2015 (with updates published in @kazil2020), this paper highlights advancements and presents Mesa in its current version (3.1.4) as of 2025.

# Statement of need
Agent-based models (ABMs) are composed of autonomous, heterogeneous agents interacting locally with other agents. These interactions give rise to emergent phenomena. The aggregate dynamics of a system under study emerge from these local interactions [@epstein_axtell_1996; @epstein1999]. This type of modeling quickly grew more sophisticated, requiring frameworks to execute them. This led to the establishment of [NetLogo](https://ccl.northwestern.edu/netlogo/) in 1999 and [MASON](https://cs.gmu.edu/~eclab/projects/mason/) in 2003.

NetLogo is the most widely adopted tool and the first to make ABMs accessible, but it only allows for small models. MASON is Java-based, allowing for advancements in scalability and speed above NetLogo, but MASON is difficult for non-programmers. Both of these tools did not serve models over HTTP, which allows for hosting models on the web, nor did they take advantage of the rich scientific Python ecosystem. In response to these needs, Mesa was created with the goal of accessibility -- targeting both beginner and advanced programmers. The major release of Mesa 3 provides advanced usability and stabilized functionality. These features include enhanced management of agents, data collection advancements, an improved visualization framework, and making it easier for researchers to create and analyze complex simulations.

# Applications
Since its creation in 2014, Mesa has been applied to modeling a wide range of phenomena from economics and sociology to ecology and epidemiology and has been cited in more than 500 papers and 800 authors. Mesa has been applied across diverse domains, including:

- Infrastructure resilience and post-disaster recovery planning [@sun2020post]
- Market modeling, including renewable energy auctions and consumer behavior [@anatolitis2017putting]
- Transportation optimization, such as combined truck-drone delivery routing [@leon2022multi]
- Recommender systems analysis examining consumer-business value tradeoffs over time [@ghanem2022balancing]
- Climate adaptation modeling examining household-level behavioral responses to environmental shocks [@taberna2023uncertainty]
- SEIR modeling of Sars-CoV-2 (Covid-19) [@pham2021interventions]
- Management of edge computing resources [@souza2023edgesimpy]

These applications showcase Mesa's versatility in modeling complex systems with autonomous interacting agents, whether representing individual consumers, infrastructure components, buildings, or vehicles.

The framework is particularly suited for:

- Models with heterogeneous agent populations
- Systems requiring sophisticated spatial interactions
- Interactive exploration of parameter spaces
- Teaching and learning agent-based modeling

# Core capabilities
Mesa is a Python-based framework for ABM that provides a comprehensive set of tools for creating, running, and analyzing ABMs. Mesa integrates with the wider scientific Python ecosystem with libraries such as [NumPy](https://numpy.org/), [pandas](https://pandas.pydata.org/), [Matplotlib](https://matplotlib.org/), [NetworkX](https://networkx.org/), and more. The backend of the framework is written in Python, while the front-end end uses a Python implementation of React. The modular architecture is comprised of three main components:

1. Core ABM components (*i.e.,* agents, spaces, agent activation, control over random numbers)to build models
2. Data collection and support for model experimentation
3. Visualization systems

This decoupled design allows selective use of components while enabling extension and customization.

Mesa follows a two-track development model where new features are first released as experimental before being stabilized. Experimental features are clearly marked as such and may have their APIs change between releases. They are graduated to stable status once their APIs and implementations are proven through community testing and feedback. Stable features follow semantic versioning.

## Core ABM components
### Model
The central class in Mesa is the Model. To build a model, the user instantiates a model object, creates a space within it, and populates the space with agent instances. Since ABMs are typically stochastic simulations, Mesa includes a random number generator and, for reproducibility purposes, allows the user to pass a seed.

```python
class SimpleModel(mesa.Model):
    def __init__(self, n_agents=10, seed=42):
        super().__init__(seed=seed)  # Initialize Mesa model with random seed

        SimpleAgent.create_agents(self, n_agents, energy=100)

    def step(self):
        self.agents.shuffle_do("step")  # Activate all agents in random order
```

### Agents
Central to ABMs are the autonomous heterogeneous agents. Mesa provides a variety of base agent classes which the user can subclass. In its most basic implementation, an agent subclass specifies the `__init__` and `step` method. Any subclass of the basic mesa agent subclass registers itself with the specified model instance, and via `agent.remove` it will remove itself from the model. It is strongly encouraged to rely on `remove`, and even extend it if needed to ensure agents are fully removed from the simulation. Sometimes an agent subclass is referred to as a "type" of agent.

```python
class SimpleAgent(mesa.Agent):
    def __init__(self, model, energy):
        super().__init__(model)  # Initialize Mesa agent
        self.energy = energy

    def step(self):
        self.energy -= 1
        if self.energy <= 0:
            self.remove()
```

### Agent management
One significant advancement of Mesa 3 is expanded functionality around agent management. The new [`AgentSet`](https://mesa.readthedocs.io/latest/apis/agent.html#mesa.agent.AgentSet) class provides methods that allow users to filter, group, and analyze agents, making it easier to express complex model logic.

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
- Voronoi-based: `VoronoiMesh` for irregular tessellations (where space is divided into cells based on proximity to seed points)

Example grid creation:

```python
    grid = OrthogonalVonNeumannGrid((width, height), torus=False, random=model.random)
```

In Mesa 3, specialized agent classes for spatial interactions in discrete spaces were added:

- `FixedAgent`: Is assigned to a cell, can access this cell, but cannot move to another cell.
- `CellAgent`: Can move between cells
- `Grid2DMovingAgent`: Extends `CellAgent` with directional movement methods

All discrete spaces support PropertyLayers - efficient numpy-based arrays for storing cell-level properties. This newly added feature allows for agents to interact with spatial properties of the cell more easily:

```python
    grid.create_property_layer("elevation", default_value=10)
    high_ground = grid.elevation.select_cells(lambda x: x > 50)
```

For models where agents need to move continuously through space rather than between discrete locations, `ContinuousSpace` allows agents to occupy any coordinate within defined boundaries:

```python
    space = ContinuousSpace(x_max, y_max, torus=True)
    space.move_agent(agent, (new_x, new_y))
```
The space module is stable but under active development. The new cell-based spaces in Mesa 3 are currently being tested and considered feature-complete. The code snippets reflected in this paper are the future expected state of Mesa. Features not yet merged into core are imported from experimental:

```python
from mesa.experimental.cell_space ...
```

### Time advancement
Mesa supports two primary approaches to advancing time in simulations: incremental-time progression (tick-based) and next-event time progression

Typically, ABMs represent time in discrete steps (often called "ticks"). For each tick, the model's step method is called, and agents are activated to take their designated actions. The most frequently implemented approach is shown below, which runs a model for 100 ticks:

```python
    model = Model(seed=42)

    for _ in range(100):
        model.step()
```

Before Mesa 3, all agents were activated within the step method of the model using predefined schedulers. However, the newly added `AgentSet` class provides a more flexible way to activate agents. These changes include the removal of the Scheduler API and its previously available fixed patterns.

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

Mesa also includes experimental support for next event time progression through the `DiscreteEventSimulator`. This approach allows scheduling events at arbitrary timestamps rather than fixed ticks, enabling both pure event-driven models and hybrid approaches. The hybrid approach combines traditional ABM discrete time steps with the flexibility and potential performance benefits of event scheduling. While currently experimental, this capability is being actively developed and tested:

```python
    # Pure event-based scheduling (experimental)
    simulator = DiscreteEventSimulator()
    model = Model(seed=42, simulator=simulator)
    simulator.schedule_event_relative(some_function, 3.1415)

    # Hybrid incremental time and next-event time progression (experimental)
    model = Model(seed=42, simulator=ABMSimulator())
    model.simulator.schedule_event_next_tick(some_function)
```

## Visualization
Mesa’s visualization module, [SolaraViz](https://mesa.readthedocs.io/latest/tutorials/visualization_tutorial.html),  allows for interactive browser-based model exploration. Advancements with Mesa 3 update the visualization from harder-to-maintain custom code to [Solara](https://solara.dev/), a standardized library. Usage of the visualization module can be seen below:

```python
    visualization = SolaraViz(
        model=model,
        components=[
            make_space_component(wolf_sheep_portrayal),          # Grid visualization
            make_plot_component(["Wolves", "Sheep", "Grass"]),   # Population plot
            lambda m: f"Step {m.steps}: {len(m.agents)} agents"  # Text display
        ],
        model_params=model_params
    )
```

![A screenshot of the WolfSheep Model in Mesa](../docs/images/wolf_sheep.png)

Key features include:

- Interactive model controls
- Real-time data visualization
- Customizable agent and space portrayal
- Support for multiple visualization types, including grids, networks, and charts

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
    results = mesa.batch_run(MyModel, parameters, iterations=5, max_steps=10)
```

# Community and ecosystem
Mesa has grown into a complete ecosystem with [extensions](https://mesa.readthedocs.io/latest/mesa_extension.html) including:

- [Mesa-Geo](https://github.com/projectmesa/mesa-geo) for geospatial modeling [@wang2022mesa]
- [Mesa-Frames](https://github.com/projectmesa/mesa-frames) for high-performance simulations
- A rich collection of community-contributed extensions, [example models](https://github.com/projectmesa/mesa-examples), and tutorials

# Conclusions
Mesa 3 introduces significant advancements to the Python ABM framework, enhancing the core toolkit with greater control, interactivity, and speed for researchers. These notable improvements, paired with its foundational integration with the scientific Python ecosystem, modular architecture, and active community, make it an indispensable tool for researchers across disciplines working in Python who want to create and analyze agent-based models.

# Acknowledgements
The advancements leading to Mesa 3 were developed by seven maintainers (the authors) and an active community with over 140 [contributors](https://github.com/projectmesa/mesa/graphs/contributors). We would especially like to thank [David Masad](https://github.com/dmasad) for his foundational work on Mesa.

# References
