"""tests for matplotlib components."""

from mesa import Agent, Model
from mesa.experimental.cell_space import (
    CellAgent,
    HexGrid,
    OrthogonalMooreGrid,
    VoronoiGrid,
    Network
)
from mesa.space import ContinuousSpace, HexSingleGrid, SingleGrid, NetworkGrid
from mesa.visualization.components.matplotlib import (
    draw_continuous_space,
    draw_hex_grid,
    draw_orthogonal_grid,
    draw_voroinoi_grid,
    draw_network
)


def agent_portrayal(agent):
    """Simple portrayal of an agent.

    Args:
        agent (Agent): The agent to portray

    """
    return {"s": 10,
            "c": "tab:blue",
            "marker": "s" if (agent.unique_id % 2) == 0 else "o"}
def test_draw_hex_grid():
    """Test drawing hexgrids."""
    model = Model(seed=42)
    grid = HexSingleGrid(10, 10, torus=True)
    for _ in range(10):
        agent = Agent(model)
        grid.move_to_empty(agent)
    draw_hex_grid(grid, agent_portrayal, None, model)


    model = Model(seed=42)
    grid = HexGrid((10, 10), torus=True, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    draw_hex_grid(grid, agent_portrayal, None, model)

def test_draw_voroinoi_grid():
    """Test drawing voroinoi grids."""
    model = Model(seed=42)

    coordinates = model.rng.random((100, 2)) * 10

    grid = VoronoiGrid(coordinates.tolist(), random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    draw_voroinoi_grid(grid, agent_portrayal)

def test_draw_orthogonal_grid():
    """Test drawing orthogonal grids."""
    model = Model(seed=42)
    grid = SingleGrid(10, 10, torus=True)
    for _ in range(10):
        agent = Agent(model)
        grid.move_to_empty(agent)
    draw_orthogonal_grid(grid, agent_portrayal, None, model)


    model = Model(seed=42)
    grid = OrthogonalMooreGrid((10, 10), torus=True, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    draw_orthogonal_grid(grid, agent_portrayal, None, model)

def test_draw_continuous_space():
    """Test drawing continuous space."""
    model = Model(seed=42)
    space = ContinuousSpace(10, 10, torus=True)
    for _ in range(10):
        x = model.random.random() * 10
        y = model.random.random() * 10
        agent = Agent(model)
        space.place_agent(agent, (x, y))
    draw_continuous_space(space, agent_portrayal)

def test_draw_network():
    """Test drawing network."""

    def agent_portrayal(agent):
        """Simple portrayal of an agent.

        Args:
            agent (Agent): The agent to portray

        """
        return {"node_size": 10,
                "node_color": "tab:blue"}

    import networkx as nx

    n = 10
    m = 20
    seed = 42
    graph = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806


    model = Model(seed=42)
    grid = NetworkGrid(graph)
    for _ in range(10):
        agent = Agent(model)
        pos = agent.random.randint(0, len(graph.nodes)-1)
        grid.place_agent(agent, pos)
    draw_network(grid, agent_portrayal)


    model = Model(seed=42)
    grid = Network(graph, random=model.random, capacity=1)
    for _ in range(10):
        agent = CellAgent(model)
        agent.cell = grid.select_random_empty_cell()

    draw_network(grid, agent_portrayal)


def test_draw_property_layers():
    """Test drawing property layers."""
    pass
