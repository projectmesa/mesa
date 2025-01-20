"""Test cell spaces."""

import random

import numpy as np
import pytest

from mesa import Model
from mesa.experimental.cell_space import (
    Cell,
    CellAgent,
    CellCollection,
    FixedAgent,
    Grid2DMovingAgent,
    HexGrid,
    Network,
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
    PropertyLayer,
    VoronoiGrid,
)


def test_orthogonal_grid_neumann():
    """Test orthogonal grid with von Neumann neighborhood."""
    width = 10
    height = 10
    grid = OrthogonalVonNeumannGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )

    assert len(grid._cells) == width * height

    # von neumann neighborhood, torus false, top left corner
    assert len(grid._cells[(0, 0)].connections.values()) == 2
    for connection in grid._cells[(0, 0)].connections.values():
        assert connection.coordinate in {(0, 1), (1, 0)}

    # von neumann neighborhood, torus false, top right corner
    for connection in grid._cells[(0, width - 1)].connections.values():
        assert connection.coordinate in {(0, width - 2), (1, width - 1)}

    # von neumann neighborhood, torus false, bottom left corner
    for connection in grid._cells[(height - 1, 0)].connections.values():
        assert connection.coordinate in {(height - 1, 1), (height - 2, 0)}

    # von neumann neighborhood, torus false, bottom right corner
    for connection in grid._cells[(height - 1, width - 1)].connections.values():
        assert connection.coordinate in {
            (height - 1, width - 2),
            (height - 2, width - 1),
        }

    # von neumann neighborhood middle of grid
    assert len(grid._cells[(5, 5)].connections.values()) == 4
    for connection in grid._cells[(5, 5)].connections.values():
        assert connection.coordinate in {(4, 5), (5, 4), (5, 6), (6, 5)}

    # von neumann neighborhood, torus True, top corner
    grid = OrthogonalVonNeumannGrid(
        (width, height), torus=True, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0)].connections.values()) == 4
    for connection in grid._cells[(0, 0)].connections.values():
        assert connection.coordinate in {(0, 1), (1, 0), (0, 9), (9, 0)}

    # von neumann neighborhood, torus True, top right corner
    for connection in grid._cells[(0, width - 1)].connections.values():
        assert connection.coordinate in {(0, 8), (0, 0), (1, 9), (9, 9)}

    # von neumann neighborhood, torus True, bottom left corner
    for connection in grid._cells[(9, 0)].connections.values():
        assert connection.coordinate in {(9, 1), (9, 9), (0, 0), (8, 0)}

    # von neumann neighborhood, torus True, bottom right corner
    for connection in grid._cells[(9, 9)].connections.values():
        assert connection.coordinate in {(9, 0), (9, 8), (8, 9), (0, 9)}


def test_orthogonal_grid_neumann_3d():
    """Test 3D orthogonal grid with von Neumann neighborhood."""
    width = 10
    height = 10
    depth = 10
    grid = OrthogonalVonNeumannGrid(
        (width, height, depth), torus=False, capacity=None, random=random.Random(42)
    )

    assert len(grid._cells) == width * height * depth

    # von neumann neighborhood, torus false, top left corner
    assert len(grid._cells[(0, 0, 0)].connections.values()) == 3
    for connection in grid._cells[(0, 0, 0)].connections.values():
        assert connection.coordinate in {(0, 0, 1), (0, 1, 0), (1, 0, 0)}

    # von neumann neighborhood, torus false, top right corner
    for connection in grid._cells[(0, width - 1, 0)].connections.values():
        assert connection.coordinate in {
            (0, width - 1, 1),
            (0, width - 2, 0),
            (1, width - 1, 0),
        }

    # von neumann neighborhood, torus false, bottom left corner
    for connection in grid._cells[(height - 1, 0, 0)].connections.values():
        assert connection.coordinate in {
            (height - 1, 0, 1),
            (height - 1, 1, 0),
            (height - 2, 0, 0),
        }

    # von neumann neighborhood, torus false, bottom right corner
    for connection in grid._cells[(height - 1, width - 1, 0)].connections.values():
        assert connection.coordinate in {
            (height - 1, width - 1, 1),
            (height - 1, width - 2, 0),
            (height - 2, width - 1, 0),
        }

    # von neumann neighborhood middle of grid
    assert len(grid._cells[(5, 5, 5)].connections.values()) == 6
    for connection in grid._cells[(5, 5, 5)].connections.values():
        assert connection.coordinate in {
            (4, 5, 5),
            (5, 4, 5),
            (5, 5, 4),
            (5, 5, 6),
            (5, 6, 5),
            (6, 5, 5),
        }

    # von neumann neighborhood, torus True, top corner
    grid = OrthogonalVonNeumannGrid(
        (width, height, depth), torus=True, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0, 0)].connections.values()) == 6
    for connection in grid._cells[(0, 0, 0)].connections.values():
        assert connection.coordinate in {
            (0, 0, 1),
            (0, 1, 0),
            (1, 0, 0),
            (0, 0, 9),
            (0, 9, 0),
            (9, 0, 0),
        }


def test_orthogonal_grid_moore():
    """Test orthogonal grid with Moore neighborhood."""
    width = 10
    height = 10

    # Moore neighborhood, torus false, top corner
    grid = OrthogonalMooreGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0)].connections.values()) == 3
    for connection in grid._cells[(0, 0)].connections.values():
        assert connection.coordinate in {(0, 1), (1, 0), (1, 1)}

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5, 5)].connections.values()) == 8
    for connection in grid._cells[(5, 5)].connections.values():
        # fmt: off
        assert connection.coordinate in {(4, 4), (4, 5), (4, 6),
                                         (5, 4), (5, 6),
                                         (6, 4), (6, 5), (6, 6)}
        # fmt: on

    # Moore neighborhood, torus True, top corner
    grid = OrthogonalMooreGrid(
        [10, 10], torus=True, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0)].connections.values()) == 8
    for connection in grid._cells[(0, 0)].connections.values():
        # fmt: off
        assert connection.coordinate in {(9, 9), (9, 0), (9, 1),
                                         (0, 9), (0, 1),
                                         (1, 9), (1, 0), (1, 1)}
        # fmt: on


def test_orthogonal_grid_moore_3d():
    """Test 3D orthogonal grid with Moore neighborhood."""
    width = 10
    height = 10
    depth = 10

    # Moore neighborhood, torus false, top corner
    grid = OrthogonalMooreGrid(
        (width, height, depth), torus=False, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0, 0)].connections.values()) == 7
    for connection in grid._cells[(0, 0, 0)].connections.values():
        assert connection.coordinate in {
            (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0),
            (1, 1, 1),
        }

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5, 5, 5)].connections.values()) == 26
    for connection in grid._cells[(5, 5, 5)].connections.values():
        # fmt: off
        assert connection.coordinate in {(4, 4, 4), (4, 4, 5), (4, 4, 6), (4, 5, 4), (4, 5, 5), (4, 5, 6), (4, 6, 4),
                                         (4, 6, 5), (4, 6, 6),
                                         (5, 4, 4), (5, 4, 5), (5, 4, 6), (5, 5, 4), (5, 5, 6), (5, 6, 4), (5, 6, 5),
                                         (5, 6, 6),
                                         (6, 4, 4), (6, 4, 5), (6, 4, 6), (6, 5, 4), (6, 5, 5), (6, 5, 6), (6, 6, 4),
                                         (6, 6, 5), (6, 6, 6)}
        # fmt: on

    # Moore neighborhood, torus True, top corner
    grid = OrthogonalMooreGrid(
        (width, height, depth), torus=True, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0, 0, 0)].connections.values()) == 26
    for connection in grid._cells[(0, 0, 0)].connections.values():
        # fmt: off
        assert connection.coordinate in {(9, 9, 9), (9, 9, 0), (9, 9, 1), (9, 0, 9), (9, 0, 0), (9, 0, 1), (9, 1, 9),
                                         (9, 1, 0), (9, 1, 1),
                                         (0, 9, 9), (0, 9, 0), (0, 9, 1), (0, 0, 9), (0, 0, 1), (0, 1, 9), (0, 1, 0),
                                         (0, 1, 1),
                                         (1, 9, 9), (1, 9, 0), (1, 9, 1), (1, 0, 9), (1, 0, 0), (1, 0, 1), (1, 1, 9),
                                         (1, 1, 0), (1, 1, 1)}
        # fmt: on


def test_orthogonal_grid_moore_4d():
    """Test 4D orthogonal grid with Moore neighborhood."""
    width = 10
    height = 10
    depth = 10
    time = 10

    # Moore neighborhood, torus false, top corner
    grid = OrthogonalMooreGrid(
        (width, height, depth, time),
        torus=False,
        capacity=None,
        random=random.Random(42),
    )
    assert len(grid._cells[(0, 0, 0, 0)].connections.values()) == 15
    for connection in grid._cells[(0, 0, 0, 0)].connections.values():
        assert connection.coordinate in {
            (0, 0, 0, 1),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 1, 0, 0),
            (0, 1, 0, 1),
            (0, 1, 1, 0),
            (0, 1, 1, 1),
            (1, 0, 0, 0),
            (1, 0, 0, 1),
            (1, 0, 1, 0),
            (1, 0, 1, 1),
            (1, 1, 0, 0),
            (1, 1, 0, 1),
            (1, 1, 1, 0),
            (1, 1, 1, 1),
        }

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5, 5, 5, 5)].connections.values()) == 80
    for connection in grid._cells[(5, 5, 5, 5)].connections.values():
        # fmt: off
        assert connection.coordinate in {(4, 4, 4, 4), (4, 4, 4, 5), (4, 4, 4, 6), (4, 4, 5, 4), (4, 4, 5, 5),
                                         (4, 4, 5, 6), (4, 4, 6, 4), (4, 4, 6, 5), (4, 4, 6, 6),
                                         (4, 5, 4, 4), (4, 5, 4, 5), (4, 5, 4, 6), (4, 5, 5, 4), (4, 5, 5, 5),
                                         (4, 5, 5, 6), (4, 5, 6, 4), (4, 5, 6, 5), (4, 5, 6, 6),
                                         (4, 6, 4, 4), (4, 6, 4, 5), (4, 6, 4, 6), (4, 6, 5, 4), (4, 6, 5, 5),
                                         (4, 6, 5, 6), (4, 6, 6, 4), (4, 6, 6, 5), (4, 6, 6, 6),
                                         (5, 4, 4, 4), (5, 4, 4, 5), (5, 4, 4, 6), (5, 4, 5, 4), (5, 4, 5, 5),
                                         (5, 4, 5, 6), (5, 4, 6, 4), (5, 4, 6, 5), (5, 4, 6, 6),
                                         (5, 5, 4, 4), (5, 5, 4, 5), (5, 5, 4, 6), (5, 5, 5, 4), (5, 5, 5, 6),
                                         (5, 5, 6, 4), (5, 5, 6, 5), (5, 5, 6, 6),
                                         (5, 6, 4, 4), (5, 6, 4, 5), (5, 6, 4, 6), (5, 6, 5, 4), (5, 6, 5, 5),
                                         (5, 6, 5, 6), (5, 6, 6, 4), (5, 6, 6, 5), (5, 6, 6, 6),
                                         (6, 4, 4, 4), (6, 4, 4, 5), (6, 4, 4, 6), (6, 4, 5, 4), (6, 4, 5, 5),
                                         (6, 4, 5, 6), (6, 4, 6, 4), (6, 4, 6, 5), (6, 4, 6, 6),
                                         (6, 5, 4, 4), (6, 5, 4, 5), (6, 5, 4, 6), (6, 5, 5, 4), (6, 5, 5, 5),
                                         (6, 5, 5, 6), (6, 5, 6, 4), (6, 5, 6, 5), (6, 5, 6, 6),
                                         (6, 6, 4, 4), (6, 6, 4, 5), (6, 6, 4, 6), (6, 6, 5, 4), (6, 6, 5, 5),
                                         (6, 6, 5, 6), (6, 6, 6, 4), (6, 6, 6, 5), (6, 6, 6, 6)}
        # fmt: on


def test_orthogonal_grid_moore_1d():
    """Test 1D orthogonal grid with Moore neighborhood."""
    width = 10

    # Moore neighborhood, torus false, left edge
    grid = OrthogonalMooreGrid(
        (width,), torus=False, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0,)].connections.values()) == 1
    for connection in grid._cells[(0,)].connections.values():
        assert connection.coordinate in {(1,)}

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5,)].connections.values()) == 2
    for connection in grid._cells[(5,)].connections.values():
        assert connection.coordinate in {(4,), (6,)}

    # Moore neighborhood, torus True, left edge
    grid = OrthogonalMooreGrid(
        (width,), torus=True, capacity=None, random=random.Random(42)
    )
    assert len(grid._cells[(0,)].connections.values()) == 2
    for connection in grid._cells[(0,)].connections.values():
        assert connection.coordinate in {(1,), (9,)}


def test_cell_neighborhood():
    """Test neighborhood method of cell in different GridSpaces."""
    # orthogonal grid

    ## von Neumann
    width = 10
    height = 10
    grid = OrthogonalVonNeumannGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )
    for radius, n in zip(range(1, 4), [2, 5, 9]):
        if radius == 1:
            neighborhood = grid._cells[(0, 0)].neighborhood
        else:
            neighborhood = grid._cells[(0, 0)].get_neighborhood(radius=radius)
        assert len(neighborhood) == n

    ## Moore
    width = 10
    height = 10
    grid = OrthogonalMooreGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )
    for radius, n in zip(range(1, 4), [3, 8, 15]):
        if radius == 1:
            neighborhood = grid._cells[(0, 0)].neighborhood
        else:
            neighborhood = grid._cells[(0, 0)].get_neighborhood(radius=radius)
        assert len(neighborhood) == n

    with pytest.raises(ValueError):
        grid._cells[(0, 0)].get_neighborhood(radius=0)

    # hexgrid
    width = 10
    height = 10
    grid = HexGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )
    for radius, n in zip(range(1, 4), [3, 7, 13]):
        if radius == 1:
            neighborhood = grid._cells[(0, 0)].neighborhood
        else:
            neighborhood = grid._cells[(0, 0)].get_neighborhood(radius=radius)
        assert len(neighborhood) == n

    width = 10
    height = 10
    grid = HexGrid(
        (width, height), torus=False, capacity=None, random=random.Random(42)
    )
    for radius, n in zip(range(1, 4), [4, 10, 17]):
        if radius == 1:
            neighborhood = grid._cells[(1, 0)].neighborhood
        else:
            neighborhood = grid._cells[(1, 0)].get_neighborhood(radius=radius)
        assert len(neighborhood) == n

    # networkgrid


def test_hexgrid():
    """Test HexGrid."""
    width = 10
    height = 10

    grid = HexGrid((width, height), torus=False, random=random.Random(42))
    assert len(grid._cells) == width * height

    # first row
    assert len(grid._cells[(0, 0)].connections.values()) == 3
    for connection in grid._cells[(0, 0)].connections.values():
        assert connection.coordinate in {(0, 1), (1, 0), (1, 1)}

    # second row
    assert len(grid._cells[(1, 0)].connections.values()) == 4
    for connection in grid._cells[(1, 0)].connections.values():
        # fmt: off
        assert connection.coordinate in {   (1, 1), (2, 1),
                                         (0, 0),    (2, 0),}
        # fmt: on

    # middle odd row
    assert len(grid._cells[(5, 5)].connections.values()) == 6
    for connection in grid._cells[(5, 5)].connections.values():
        # fmt: off
        assert connection.coordinate in {  (4, 4), (5, 4),
                                         (4, 5), (6, 5),
                                         (4, 6), (5, 6)}

        # fmt: on

    # middle even row
    assert len(grid._cells[(4, 4)].connections.values()) == 6
    for connection in grid._cells[(4, 4)].connections.values():
        # fmt: off
        assert connection.coordinate in {(4, 3), (5, 3),
                                         (3, 4), (5, 4),
                                         (4, 5), (5, 5)}

        # fmt: on

    grid = HexGrid((width, height), torus=True, random=random.Random(42))
    assert len(grid._cells) == width * height

    # first row
    assert len(grid._cells[(0, 0)].connections.values()) == 6
    for connection in grid._cells[(0, 0)].connections.values():
        # fmt: off
        assert connection.coordinate in {(0, 9), (1, 9),
                                         (9, 0), (1, 0),
                                         (0, 1), (1, 1)}

        # fmt: on


def test_networkgrid():
    """Test NetworkGrid."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G, random=random.Random(42))

    assert len(grid._cells) == n

    for i, cell in grid._cells.items():
        for connection in cell.connections.values():
            assert connection.coordinate in G.neighbors(i)

    import pickle

    pickle.loads(pickle.dumps(grid))  # noqa: S301


def test_voronoigrid():
    """Test VoronoiGrid."""
    points = [[0, 1], [1, 3], [1.1, 1], [1, 1]]

    grid = VoronoiGrid(points, random=random.Random(42))

    assert len(grid._cells) == len(points)

    # Check cell neighborhood
    assert len(grid._cells[0].connections.values()) == 2
    for connection in grid._cells[0].connections.values():
        assert connection.coordinate in [[1, 1], [1, 3]]

    with pytest.raises(ValueError):
        VoronoiGrid(points, capacity="str", random=random.Random(42))

    with pytest.raises(ValueError):
        VoronoiGrid((1, 1), random=random.Random(42))

    with pytest.raises(ValueError):
        VoronoiGrid([[0, 1], [0, 1, 1]], random=random.Random(42))


def test_empties_space():
    """Test empties method for Discrete Spaces."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G, random=random.Random(42))

    assert len(grid.empties) == n

    model = Model()
    for i in range(8):
        grid._cells[i].add_agent(CellAgent(model))


def test_agents_property():
    """Test empties method for Discrete Spaces."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G, random=random.Random(42))

    model = Model()
    for i in range(8):
        grid._cells[i].add_agent(CellAgent(model))

    cell = grid.select_random_empty_cell()
    assert cell.coordinate in {8, 9}

    assert len(grid.agents) == 8

    for i, j in enumerate(sorted(grid.agents.get("unique_id"))):
        assert (i + 1) == j  # unique_id starts from 1


def test_cell():
    """Test Cell class."""
    cell1 = Cell((1,), capacity=None, random=random.Random())
    cell2 = Cell((2,), capacity=None, random=random.Random())

    # connect
    cell1.connect(cell2)
    assert cell2 in cell1.connections.values()

    # disconnect
    cell1.disconnect(cell2)
    assert cell2 not in cell1.connections.values()

    # remove cell not in connections
    cell1.disconnect(cell2)

    # add_agent
    model = Model()
    agent = CellAgent(model)

    cell1.add_agent(agent)
    assert agent in cell1.agents

    # remove_agent
    cell1.remove_agent(agent)
    assert agent not in cell1.agents

    with pytest.raises(ValueError):
        cell1.remove_agent(agent)

    cell1 = Cell((1,), capacity=1, random=random.Random())
    cell1.add_agent(CellAgent(model))
    assert cell1.is_full

    with pytest.raises(Exception):
        cell1.add_agent(CellAgent(model))


def test_cell_collection():
    """Test CellCollection."""
    cell1 = Cell((1,), capacity=None, random=random.Random())

    collection = CellCollection({cell1: cell1.agents}, random=random.Random())
    assert len(collection) == 1
    assert cell1 in collection

    rng = random.Random()
    n = 10
    collection = CellCollection([Cell((i,), random=rng) for i in range(n)], random=rng)
    assert len(collection) == n

    cell = collection.select_random_cell()
    assert cell in collection

    cells = collection.cells
    assert len(cells) == n

    agents = collection.agents
    assert len(list(agents)) == 0

    cells = collection.cells
    model = Model()
    cells[0].add_agent(CellAgent(model))
    cells[3].add_agent(CellAgent(model))
    cells[7].add_agent(CellAgent(model))
    agents = collection.agents
    assert len(list(agents)) == 3

    agent = collection.select_random_agent()
    assert agent in set(collection.agents)

    agents = collection[cells[0]]
    assert agents == cells[0].agents

    cell = collection.select(at_most=1)
    assert len(cell) == 1

    cells = collection.select(at_most=2)
    assert len(cells) == 2

    cells = collection.select(at_most=0.5)
    assert len(cells) == 5

    cells = collection.select()
    assert len(cells) == len(collection)


def test_empty_cell_collection():
    """Test that CellCollection properly handles empty collections."""
    rng = random.Random(42)

    # Test initializing with empty collection
    collection = CellCollection([], random=rng)
    assert len(collection) == 0
    assert collection._capacity is None
    assert list(collection.cells) == []
    assert list(collection.agents) == []

    # Test selecting from empty collection
    selected = collection.select(lambda cell: True)
    assert len(selected) == 0
    assert selected._capacity is None

    # Test filtering to empty collection
    n = 10
    full_collection = CellCollection(
        [Cell((i,), random=rng) for i in range(n)], random=rng
    )
    assert len(full_collection) == n

    # Filter to empty collection
    empty_result = full_collection.select(lambda cell: False)
    assert len(empty_result) == 0
    assert empty_result._capacity is None

    # Test at_most with empty collection
    at_most_result = full_collection.select(lambda cell: False, at_most=5)
    assert len(at_most_result) == 0
    assert at_most_result._capacity is None


### PropertyLayer tests
def test_property_layer_integration():
    """Test integration of PropertyLayer with DiscrateSpace and Cell."""
    dimensions = (10, 10)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))

    # Test adding a PropertyLayer to the grid
    elevation = PropertyLayer("elevation", dimensions, default_value=0.0)
    grid.add_property_layer(elevation)
    assert "elevation" in grid._mesa_property_layers
    assert len(grid._mesa_property_layers) == 2  ## empty is always there
    assert grid.elevation is elevation

    with pytest.raises(AttributeError):
        grid.elevation = 0

    # Test accessing PropertyLayer from a cell
    cell = grid._cells[(0, 0)]
    assert hasattr(cell, "elevation")
    assert cell.elevation == 0.0

    # Test setting property value for a cell
    cell.elevation = 100
    assert cell.elevation == 100
    assert elevation.data[0, 0] == 100

    # Test modifying property value for a cell
    cell.elevation += 50
    assert cell.elevation == 150
    assert elevation.data[0, 0] == 150

    cell.elevation = np.add(cell.elevation, 50)
    assert cell.elevation == 200
    assert elevation.data[0, 0] == 200

    # Test modifying PropertyLayer values
    grid.set_property("elevation", 100, condition=lambda value: value == 200)
    assert cell.elevation == 100

    # Test modifying PropertyLayer using numpy operations
    grid.modify_properties("elevation", np.add, 50)
    assert cell.elevation == 150

    # Test removing a PropertyLayer
    grid.remove_property_layer("elevation")
    assert "elevation" not in grid._mesa_property_layers
    assert not hasattr(cell, "elevation")

    # what happens if we add a layer whose name clashes with an existing cell attribute?
    dimensions = (10, 10)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))

    with pytest.raises(ValueError):
        grid.create_property_layer("capacity", 1, dtype=int)


def test_copy_pickle_with_propertylayers():
    """Test deepcopy and pickle with dynamically created GridClass and ProperyLayer descriptors."""
    import copy
    import pickle

    dimensions = (10, 10)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))

    grid2 = copy.deepcopy(grid)
    assert grid2._cells[(0, 0)].empty

    data = grid2._mesa_property_layers["empty"].data
    grid2._cells[(0, 0)].empty = False
    assert grid2._cells[(0, 0)].empty == data[0, 0]

    dimensions = (10, 10)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    dump = pickle.dumps(grid)
    grid2 = pickle.loads(dump)  # noqa: S301
    assert grid2._cells[(0, 0)].empty
    data = grid2._mesa_property_layers["empty"].data
    grid2._cells[(0, 0)].empty = False
    assert grid2._cells[(0, 0)].empty == data[0, 0]


def test_multiple_property_layers():
    """Test initialization of DiscrateSpace with PropertyLayers."""
    dimensions = (5, 5)
    elevation = PropertyLayer("elevation", dimensions, default_value=0.0)
    temperature = PropertyLayer("temperature", dimensions, default_value=20.0)

    # Test initialization with a single PropertyLayer
    grid1 = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    grid1.add_property_layer(elevation)
    assert "elevation" in grid1._mesa_property_layers
    assert len(grid1._mesa_property_layers) == 2  ## empty is already there

    # Test initialization with multiple PropertyLayers
    grid2 = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    grid2.add_property_layer(temperature)
    grid2.add_property_layer(elevation)
    #
    assert "temperature" in grid2._mesa_property_layers
    assert "elevation" in grid2._mesa_property_layers
    assert len(grid2._mesa_property_layers) == 3

    # Modify properties
    grid2.modify_properties("elevation", lambda x: x + 10)
    grid2.modify_properties("temperature", lambda x: x + 5)

    for cell in grid2.all_cells:
        assert cell.elevation == 10
        assert cell.temperature == 25


def test_get_neighborhood_mask():
    """Test get_neighborhood_mask."""
    dimensions = (5, 5)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    grid.create_property_layer("elevation", default_value=0.0)

    grid.get_neighborhood_mask((2, 2))

    mask = grid.get_neighborhood_mask((2, 2))
    for cell in grid._cells[(2, 2)].connections.values():
        assert mask[cell.coordinate]
    assert mask[grid._cells[(2, 2)].coordinate]

    mask = grid.get_neighborhood_mask((2, 2), include_center=False)
    for cell in grid._cells[(2, 2)].connections.values():
        assert mask[cell.coordinate]
    assert not mask[grid._cells[(2, 2)].coordinate]


def test_select_cells():
    """Test select_cells."""
    dimensions = (5, 5)
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))

    data = np.random.default_rng(12456).random((5, 5))
    grid.add_property_layer(PropertyLayer.from_data("elevation", data))

    # fixme, add an agent and update the np.all test accordingly
    mask = grid.select_cells(
        conditions={"elevation": lambda x: x > 0.5}, return_list=False, only_empty=True
    )
    assert mask.shape == (5, 5)
    assert np.all(mask == (data > 0.5))

    mask = grid.select_cells(
        conditions={"elevation": lambda x: x > 0.5}, return_list=False, only_empty=False
    )
    assert mask.shape == (5, 5)
    assert np.all(mask == (data > 0.5))

    # fixme add extreme_values highest and lowest
    mask = grid.select_cells(
        extreme_values={"elevation": "highest"}, return_list=False, only_empty=False
    )
    assert mask.shape == (5, 5)
    assert np.all(mask == (data == data.max()))

    mask = grid.select_cells(
        extreme_values={"elevation": "lowest"}, return_list=False, only_empty=False
    )
    assert mask.shape == (5, 5)
    assert np.all(mask == (data == data.min()))

    with pytest.raises(ValueError):
        grid.select_cells(
            extreme_values={"elevation": "weird"}, return_list=False, only_empty=False
        )

    # fixme add pre-specified mask to any other option


def test_property_layer():
    """Test various property layer methods."""
    elevation = PropertyLayer("elevation", (5, 5), default_value=0.0)

    # test set_cells
    elevation.set_cells(10)
    assert np.all(elevation.data == 10)

    elevation.set_cells(np.ones((5, 5)))
    assert np.all(elevation.data == 1)

    with pytest.raises(ValueError):
        elevation.set_cells(np.ones((6, 6)))

    data = np.random.default_rng(42).random((5, 5))
    layer = PropertyLayer.from_data("some_name", data)

    def condition(x):
        return x > 0.5

    layer.set_cells(1, condition=condition)
    assert np.all((layer.data == 1) == (data > 0.5))

    # modify_cells
    data = np.zeros((10, 10))
    layer = PropertyLayer.from_data("some_name", data)

    layer.data = np.zeros((10, 10))
    layer.modify_cells(lambda x: x + 2)
    assert np.all(layer.data == 2)

    layer.data = np.ones((10, 10))
    layer.modify_cells(np.multiply, 3)
    assert np.all(layer.data[3, 3] == 3)

    data = np.random.default_rng(42).random((10, 10))
    layer.data = np.random.default_rng(42).random((10, 10))
    layer.modify_cells(np.add, value=3, condition=condition)
    assert np.all((layer.data > 3.5) == (data > 0.5))

    with pytest.raises(ValueError):
        layer.modify_cells(np.add)  # Missing value for ufunc

    # aggregate
    layer.data = np.ones((10, 10))
    assert layer.aggregate(np.sum) == 100


def test_property_layer_errors():
    """Test error handling for PropertyLayers."""
    dimensions = 5, 5
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    elevation = PropertyLayer("elevation", dimensions, default_value=0.0)

    # Test adding a PropertyLayer with an existing name
    grid.add_property_layer(elevation)
    with pytest.raises(ValueError, match="Property layer elevation already exists."):
        grid.add_property_layer(elevation)

    # test adding a layer with different dimensions than space
    dimensions = 5, 5
    grid = OrthogonalMooreGrid(dimensions, torus=False, random=random.Random(42))
    elevation = PropertyLayer("elevation", (10, 10), default_value=0.0)
    with pytest.raises(
        ValueError,
        match="Dimensions of property layer do not match the dimensions of the grid",
    ):
        grid.add_property_layer(elevation)

    with pytest.warns(UserWarning):
        PropertyLayer("elevation", (10, 10), default_value=0, dtype=float)


def test_cell_agent():  # noqa: D103
    cell1 = Cell((1,), capacity=None, random=random.Random())
    cell2 = Cell((2,), capacity=None, random=random.Random())

    # connect
    # add_agent
    model = Model()
    agent = CellAgent(model)

    agent.cell = cell1
    assert agent in cell1.agents

    agent.cell = None
    assert agent not in cell1.agents

    agent.cell = cell2
    assert agent not in cell1.agents
    assert agent in cell2.agents

    agent.cell = cell1
    assert agent in cell1.agents
    assert agent not in cell2.agents

    agent.remove()
    assert agent not in model._all_agents
    assert agent not in cell1.agents
    assert agent not in cell2.agents

    model = Model()
    agent = CellAgent(model)
    agent.cell = cell1
    agent.move_to(cell2)
    assert agent not in cell1.agents
    assert agent in cell2.agents


def test_grid2DMovingAgent():  # noqa: D103
    # we first test on a moore grid because all directions are defined
    grid = OrthogonalMooreGrid((10, 10), torus=False, random=random.Random(42))

    model = Model()
    agent = Grid2DMovingAgent(model)

    agent.cell = grid[4, 4]
    agent.move("up")
    assert agent.cell == grid[3, 4]

    grid = OrthogonalVonNeumannGrid((10, 10), torus=False, random=random.Random(42))

    model = Model()
    agent = Grid2DMovingAgent(model)
    agent.cell = grid[4, 4]

    with pytest.raises(ValueError):  # test for invalid direction
        agent.move("upright")

    with pytest.raises(ValueError):  # test for unknown direction
        agent.move("back")


def test_patch():  # noqa: D103
    cell1 = Cell((1,), capacity=None, random=random.Random())
    cell2 = Cell((2,), capacity=None, random=random.Random())

    # connect
    # add_agent
    model = Model()
    agent = FixedAgent(model)
    agent.cell = cell1

    with pytest.raises(ValueError):
        agent.cell = cell2

    agent.remove()
    assert agent not in model._agents


def test_copying_discrete_spaces():  # noqa: D103
    # inspired by #2373
    # we use deepcopy but this also applies to pickle
    import copy

    import networkx as nx

    grid = OrthogonalMooreGrid((100, 100), random=random.Random(42))
    grid_copy = copy.deepcopy(grid)

    c1 = grid[(5, 5)].connections
    c2 = grid_copy[(5, 5)].connections

    for c1, c2 in zip(grid.all_cells, grid_copy.all_cells):
        for k, v in c1.connections.items():
            assert v.coordinate == c2.connections[k].coordinate

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G, random=random.Random(42))
    grid_copy = copy.deepcopy(grid)

    for c1, c2 in zip(grid.all_cells, grid_copy.all_cells):
        for k, v in c1.connections.items():
            assert v.coordinate == c2.connections[k].coordinate

    grid = HexGrid((100, 100), random=random.Random(42))
    grid_copy = copy.deepcopy(grid)

    c1 = grid[(5, 5)].connections
    c2 = grid_copy[(5, 5)].connections

    for c1, c2 in zip(grid.all_cells, grid_copy.all_cells):
        for k, v in c1.connections.items():
            assert v.coordinate == c2.connections[k].coordinate
