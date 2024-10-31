"""tests for matplotlib components."""

import matplotlib.pyplot as plt

from mesa import Agent, Model
from mesa.experimental.cell_space import (
    CellAgent,
    HexGrid,
    Network,
    OrthogonalMooreGrid,
    VoronoiGrid,
)
from mesa.space import (
    ContinuousSpace,
    HexSingleGrid,
    NetworkGrid,
    PropertyLayer,
    SingleGrid,
)
from mesa.visualization.components.mpl_space_drawing import (
    draw_continuous_space,
    draw_hex_grid,
    draw_network,
    draw_orthogonal_grid,
    draw_property_layers,
    draw_voroinoi_grid,
)


def agent_portrayal(agent):
    """Simple portrayal of an agent.

    Args:
        agent (Agent): The agent to portray

    """
    return {
        "s": 10,
        "c": "tab:blue",
        "marker": "s" if (agent.unique_id % 2) == 0 else "o",
    }


def test_draw_hex_grid():
    """Test drawing hexgrids."""
    model = Model(seed=42)
    grid = HexSingleGrid(10, 10, torus=True)
    for _ in range(10):
        agent = Agent(model)
        grid.move_to_empty(agent)

    fig, ax = plt.subplots()
    draw_hex_grid(grid, agent_portrayal, ax)

    model = Model(seed=42)
    grid = HexGrid((10, 10), torus=True, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    fig, ax = plt.subplots()
    draw_hex_grid(grid, agent_portrayal, ax)


def test_draw_voroinoi_grid():
    """Test drawing voroinoi grids."""
    model = Model(seed=42)

    coordinates = model.rng.random((100, 2)) * 10

    grid = VoronoiGrid(coordinates.tolist(), random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    fig, ax = plt.subplots()
    draw_voroinoi_grid(grid, agent_portrayal, ax)


def test_draw_orthogonal_grid():
    """Test drawing orthogonal grids."""
    model = Model(seed=42)
    grid = SingleGrid(10, 10, torus=True)
    for _ in range(10):
        agent = Agent(model)
        grid.move_to_empty(agent)

    fig, ax = plt.subplots()
    draw_orthogonal_grid(grid, agent_portrayal, ax)

    model = Model(seed=42)
    grid = OrthogonalMooreGrid((10, 10), torus=True, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    fig, ax = plt.subplots()
    draw_orthogonal_grid(grid, agent_portrayal, ax)


def test_draw_continuous_space():
    """Test drawing continuous space."""
    model = Model(seed=42)
    space = ContinuousSpace(10, 10, torus=True)
    for _ in range(10):
        x = model.random.random() * 10
        y = model.random.random() * 10
        agent = Agent(model)
        space.place_agent(agent, (x, y))

    fig, ax = plt.subplots()
    draw_continuous_space(space, agent_portrayal, ax)


def test_draw_network():
    """Test drawing network."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    graph = nx.gnm_random_graph(n, m, seed=seed)

    model = Model(seed=42)
    grid = NetworkGrid(graph)
    for _ in range(10):
        agent = Agent(model)
        pos = agent.random.randint(0, len(graph.nodes) - 1)
        grid.place_agent(agent, pos)

    fig, ax = plt.subplots()
    draw_network(grid, agent_portrayal, ax)

    model = Model(seed=42)
    grid = Network(graph, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    fig, ax = plt.subplots()
    draw_network(grid, agent_portrayal, ax)


def test_draw_property_layers():
    """Test drawing property layers."""
    model = Model(seed=42)
    grid = SingleGrid(10, 10, torus=True)
    grid.add_property_layer(PropertyLayer("test", grid.width, grid.height, 0))

    fig, ax = plt.subplots()
    draw_property_layers(grid, {"test": {"colormap": "viridis", "colorbar": True}}, ax)

    model = Model(seed=42)
    grid = OrthogonalMooreGrid((10, 10), torus=True, random=model.random, capacity=1)
    grid.add_property_layer(PropertyLayer("test", grid.width, grid.height, 0))

    fig, ax = plt.subplots()
    draw_property_layers(grid, {"test": {"colormap": "viridis", "colorbar": True}}, ax)
