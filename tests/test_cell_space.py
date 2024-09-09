"""Test cell spaces."""

import random

import pytest

from mesa import Model
from mesa.spaces import (
    Cell,
    CellAgent,
    CellCollection,
    HexGrid,
    Network,
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
    VoronoiGrid,
)


def test_orthogonal_grid_neumann():
    """Test orthogonal grid with von Neumann neighborhood."""
    width = 10
    height = 10
    grid = OrthogonalVonNeumannGrid((width, height), torus=False, capacity=None)

    assert len(grid._cells) == width * height

    # von neumann neighborhood, torus false, top left corner
    assert len(grid._cells[(0, 0)]._connections) == 2
    for connection in grid._cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0)}

    # von neumann neighborhood, torus false, top right corner
    for connection in grid._cells[(0, width - 1)]._connections:
        assert connection.coordinate in {(0, width - 2), (1, width - 1)}

    # von neumann neighborhood, torus false, bottom left corner
    for connection in grid._cells[(height - 1, 0)]._connections:
        assert connection.coordinate in {(height - 1, 1), (height - 2, 0)}

    # von neumann neighborhood, torus false, bottom right corner
    for connection in grid._cells[(height - 1, width - 1)]._connections:
        assert connection.coordinate in {
            (height - 1, width - 2),
            (height - 2, width - 1),
        }

    # von neumann neighborhood middle of grid
    assert len(grid._cells[(5, 5)]._connections) == 4
    for connection in grid._cells[(5, 5)]._connections:
        assert connection.coordinate in {(4, 5), (5, 4), (5, 6), (6, 5)}

    # von neumann neighborhood, torus True, top corner
    grid = OrthogonalVonNeumannGrid((width, height), torus=True, capacity=None)
    assert len(grid._cells[(0, 0)]._connections) == 4
    for connection in grid._cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0), (0, 9), (9, 0)}

    # von neumann neighborhood, torus True, top right corner
    for connection in grid._cells[(0, width - 1)]._connections:
        assert connection.coordinate in {(0, 8), (0, 0), (1, 9), (9, 9)}

    # von neumann neighborhood, torus True, bottom left corner
    for connection in grid._cells[(9, 0)]._connections:
        assert connection.coordinate in {(9, 1), (9, 9), (0, 0), (8, 0)}

    # von neumann neighborhood, torus True, bottom right corner
    for connection in grid._cells[(9, 9)]._connections:
        assert connection.coordinate in {(9, 0), (9, 8), (8, 9), (0, 9)}


def test_orthogonal_grid_neumann_3d():
    """Test 3D orthogonal grid with von Neumann neighborhood."""
    width = 10
    height = 10
    depth = 10
    grid = OrthogonalVonNeumannGrid((width, height, depth), torus=False, capacity=None)

    assert len(grid._cells) == width * height * depth

    # von neumann neighborhood, torus false, top left corner
    assert len(grid._cells[(0, 0, 0)]._connections) == 3
    for connection in grid._cells[(0, 0, 0)]._connections:
        assert connection.coordinate in {(0, 0, 1), (0, 1, 0), (1, 0, 0)}

    # von neumann neighborhood, torus false, top right corner
    for connection in grid._cells[(0, width - 1, 0)]._connections:
        assert connection.coordinate in {
            (0, width - 1, 1),
            (0, width - 2, 0),
            (1, width - 1, 0),
        }

    # von neumann neighborhood, torus false, bottom left corner
    for connection in grid._cells[(height - 1, 0, 0)]._connections:
        assert connection.coordinate in {
            (height - 1, 0, 1),
            (height - 1, 1, 0),
            (height - 2, 0, 0),
        }

    # von neumann neighborhood, torus false, bottom right corner
    for connection in grid._cells[(height - 1, width - 1, 0)]._connections:
        assert connection.coordinate in {
            (height - 1, width - 1, 1),
            (height - 1, width - 2, 0),
            (height - 2, width - 1, 0),
        }

    # von neumann neighborhood middle of grid
    assert len(grid._cells[(5, 5, 5)]._connections) == 6
    for connection in grid._cells[(5, 5, 5)]._connections:
        assert connection.coordinate in {
            (4, 5, 5),
            (5, 4, 5),
            (5, 5, 4),
            (5, 5, 6),
            (5, 6, 5),
            (6, 5, 5),
        }

    # von neumann neighborhood, torus True, top corner
    grid = OrthogonalVonNeumannGrid((width, height, depth), torus=True, capacity=None)
    assert len(grid._cells[(0, 0, 0)]._connections) == 6
    for connection in grid._cells[(0, 0, 0)]._connections:
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
    grid = OrthogonalMooreGrid((width, height), torus=False, capacity=None)
    assert len(grid._cells[(0, 0)]._connections) == 3
    for connection in grid._cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0), (1, 1)}

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5, 5)]._connections) == 8
    for connection in grid._cells[(5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 4), (4, 5), (4, 6),
                                         (5, 4),         (5, 6),
                                         (6, 4), (6, 5), (6, 6)}
        # fmt: on

    # Moore neighborhood, torus True, top corner
    grid = OrthogonalMooreGrid([10, 10], torus=True, capacity=None)
    assert len(grid._cells[(0, 0)]._connections) == 8
    for connection in grid._cells[(0, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(9, 9), (9, 0), (9, 1),
                                         (0, 9),         (0, 1),
                                         (1, 9), (1, 0), (1, 1)}
        # fmt: on


def test_orthogonal_grid_moore_3d():
    """Test 3D orthogonal grid with Moore neighborhood."""
    width = 10
    height = 10
    depth = 10

    # Moore neighborhood, torus false, top corner
    grid = OrthogonalMooreGrid((width, height, depth), torus=False, capacity=None)
    assert len(grid._cells[(0, 0, 0)]._connections) == 7
    for connection in grid._cells[(0, 0, 0)]._connections:
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
    assert len(grid._cells[(5, 5, 5)]._connections) == 26
    for connection in grid._cells[(5, 5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 4, 4), (4, 4, 5), (4, 4, 6), (4, 5, 4), (4, 5, 5), (4, 5, 6), (4, 6, 4), (4, 6, 5), (4, 6, 6),
                                         (5, 4, 4), (5, 4, 5), (5, 4, 6), (5, 5, 4),             (5, 5, 6), (5, 6, 4), (5, 6, 5), (5, 6, 6),
                                         (6, 4, 4), (6, 4, 5), (6, 4, 6), (6, 5, 4), (6, 5, 5), (6, 5, 6), (6, 6, 4), (6, 6, 5), (6, 6, 6)}
        # fmt: on

    # Moore neighborhood, torus True, top corner
    grid = OrthogonalMooreGrid((width, height, depth), torus=True, capacity=None)
    assert len(grid._cells[(0, 0, 0)]._connections) == 26
    for connection in grid._cells[(0, 0, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(9, 9, 9), (9, 9, 0), (9, 9, 1), (9, 0, 9), (9, 0, 0), (9, 0, 1), (9, 1, 9), (9, 1, 0), (9, 1, 1),
                                         (0, 9, 9), (0, 9, 0), (0, 9, 1), (0, 0, 9),             (0, 0, 1), (0, 1, 9), (0, 1, 0), (0, 1, 1),
                                         (1, 9, 9), (1, 9, 0), (1, 9, 1), (1, 0, 9), (1, 0, 0), (1, 0, 1), (1, 1, 9), (1, 1, 0), (1, 1, 1)}
        # fmt: on


def test_orthogonal_grid_moore_4d():
    """Test 4D orthogonal grid with Moore neighborhood."""
    width = 10
    height = 10
    depth = 10
    time = 10

    # Moore neighborhood, torus false, top corner
    grid = OrthogonalMooreGrid((width, height, depth, time), torus=False, capacity=None)
    assert len(grid._cells[(0, 0, 0, 0)]._connections) == 15
    for connection in grid._cells[(0, 0, 0, 0)]._connections:
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
    assert len(grid._cells[(5, 5, 5, 5)]._connections) == 80
    for connection in grid._cells[(5, 5, 5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 4, 4, 4), (4, 4, 4, 5), (4, 4, 4, 6), (4, 4, 5, 4), (4, 4, 5, 5), (4, 4, 5, 6), (4, 4, 6, 4), (4, 4, 6, 5), (4, 4, 6, 6),
                                         (4, 5, 4, 4), (4, 5, 4, 5), (4, 5, 4, 6), (4, 5, 5, 4), (4, 5, 5, 5), (4, 5, 5, 6), (4, 5, 6, 4), (4, 5, 6, 5), (4, 5, 6, 6),
                                            (4, 6, 4, 4), (4, 6, 4, 5), (4, 6, 4, 6), (4, 6, 5, 4), (4, 6, 5, 5), (4, 6, 5, 6), (4, 6, 6, 4), (4, 6, 6, 5), (4, 6, 6, 6),
                                            (5, 4, 4, 4), (5, 4, 4, 5), (5, 4, 4, 6), (5, 4, 5, 4), (5, 4, 5, 5), (5, 4, 5, 6), (5, 4, 6, 4), (5, 4, 6, 5), (5, 4, 6, 6),
                                            (5, 5, 4, 4), (5, 5, 4, 5), (5, 5, 4, 6), (5, 5, 5, 4),             (5, 5, 5, 6), (5, 5, 6, 4), (5, 5, 6, 5), (5, 5, 6, 6),
                                            (5, 6, 4, 4), (5, 6, 4, 5), (5, 6, 4, 6), (5, 6, 5, 4), (5, 6, 5, 5), (5, 6, 5, 6), (5, 6, 6, 4), (5, 6, 6, 5), (5, 6, 6, 6),
                                            (6, 4, 4, 4), (6, 4, 4, 5), (6, 4, 4, 6), (6, 4, 5, 4), (6, 4, 5, 5), (6, 4, 5, 6), (6, 4, 6, 4), (6, 4, 6, 5), (6, 4, 6, 6),
                                            (6, 5, 4, 4), (6, 5, 4, 5), (6, 5, 4, 6), (6, 5, 5, 4), (6, 5, 5, 5), (6, 5, 5, 6), (6, 5, 6, 4), (6, 5, 6, 5), (6, 5, 6, 6),
                                            (6, 6, 4, 4), (6, 6, 4, 5), (6, 6, 4, 6), (6, 6, 5, 4), (6, 6, 5, 5), (6, 6, 5, 6), (6, 6, 6, 4), (6, 6, 6, 5), (6, 6, 6, 6)}
        # fmt: on


def test_orthogonal_grid_moore_1d():
    """Test 1D orthogonal grid with Moore neighborhood."""
    width = 10

    # Moore neighborhood, torus false, left edge
    grid = OrthogonalMooreGrid((width,), torus=False, capacity=None)
    assert len(grid._cells[(0,)]._connections) == 1
    for connection in grid._cells[(0,)]._connections:
        assert connection.coordinate in {(1,)}

    # Moore neighborhood middle of grid
    assert len(grid._cells[(5,)]._connections) == 2
    for connection in grid._cells[(5,)]._connections:
        assert connection.coordinate in {(4,), (6,)}

    # Moore neighborhood, torus True, left edge
    grid = OrthogonalMooreGrid((width,), torus=True, capacity=None)
    assert len(grid._cells[(0,)]._connections) == 2
    for connection in grid._cells[(0,)]._connections:
        assert connection.coordinate in {(1,), (9,)}


def test_cell_neighborhood():
    """Test neighborhood method of cell in different GridSpaces."""
    # orthogonal grid

    ## von Neumann
    width = 10
    height = 10
    grid = OrthogonalVonNeumannGrid((width, height), torus=False, capacity=None)
    for radius, n in zip(range(1, 4), [2, 5, 9]):
        neighborhood = grid._cells[(0, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    ## Moore
    width = 10
    height = 10
    grid = OrthogonalMooreGrid((width, height), torus=False, capacity=None)
    for radius, n in zip(range(1, 4), [3, 8, 15]):
        neighborhood = grid._cells[(0, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    with pytest.raises(ValueError):
        grid._cells[(0, 0)].neighborhood(radius=0)

    # hexgrid
    width = 10
    height = 10
    grid = HexGrid((width, height), torus=False, capacity=None)
    for radius, n in zip(range(1, 4), [2, 6, 11]):
        neighborhood = grid._cells[(0, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    width = 10
    height = 10
    grid = HexGrid((width, height), torus=False, capacity=None)
    for radius, n in zip(range(1, 4), [5, 10, 17]):
        neighborhood = grid._cells[(1, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    # networkgrid


def test_hexgrid():
    """Test HexGrid."""
    width = 10
    height = 10

    grid = HexGrid((width, height), torus=False)
    assert len(grid._cells) == width * height

    # first row
    assert len(grid._cells[(0, 0)]._connections) == 2
    for connection in grid._cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0)}

    # second row
    assert len(grid._cells[(1, 0)]._connections) == 5
    for connection in grid._cells[(1, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(0, 0), (0, 1),
                                                    (1, 1),
                                         (2, 0), (2, 1)}

    # middle odd row
    assert len(grid._cells[(5, 5)]._connections) == 6
    for connection in grid._cells[(5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 5), (4, 6),
                                      (5, 4),       (5, 6),
                                         (6, 5), (6, 6)}

        # fmt: on

    # middle even row
    assert len(grid._cells[(4, 4)]._connections) == 6
    for connection in grid._cells[(4, 4)]._connections:
        # fmt: off
        assert connection.coordinate in {(3, 3), (3, 4),
                                      (4, 3),       (4, 5),
                                         (5, 3), (5, 4)}

        # fmt: on

    grid = HexGrid((width, height), torus=True)
    assert len(grid._cells) == width * height

    # first row
    assert len(grid._cells[(0, 0)]._connections) == 6
    for connection in grid._cells[(0, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(9, 9), (9, 0),
                                      (0, 9),       (0, 1),
                                         (1, 9), (1, 0)}

        # fmt: on


def test_networkgrid():
    """Test NetworkGrid."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G)

    assert len(grid._cells) == n

    for i, cell in grid._cells.items():
        for connection in cell._connections:
            assert connection.coordinate in G.neighbors(i)


def test_voronoigrid():
    """Test VoronoiGrid."""
    points = [[0, 1], [1, 3], [1.1, 1], [1, 1]]

    grid = VoronoiGrid(points)

    assert len(grid._cells) == len(points)

    # Check cell neighborhood
    assert len(grid._cells[0]._connections) == 2
    for connection in grid._cells[0]._connections:
        assert connection.coordinate in [[1, 1], [1, 3]]

    with pytest.raises(ValueError):
        VoronoiGrid(points, capacity="str")

    with pytest.raises(ValueError):
        VoronoiGrid((1, 1))

    with pytest.raises(ValueError):
        VoronoiGrid([[0, 1], [0, 1, 1]])


def test_empties_space():
    """Test empties method for Discrete Spaces."""
    import networkx as nx

    n = 10
    m = 20
    seed = 42
    G = nx.gnm_random_graph(n, m, seed=seed)  # noqa: N806
    grid = Network(G)

    assert len(grid.empties) == n

    model = Model()
    for i in range(8):
        grid._cells[i].add_agent(CellAgent(model))

    cell = grid.select_random_empty_cell()
    assert cell.coordinate in {8, 9}


def test_cell():
    """Test Cell class."""
    cell1 = Cell((1,), capacity=None, random=random.Random())
    cell2 = Cell((2,), capacity=None, random=random.Random())

    # connect
    cell1.connect(cell2)
    assert cell2 in cell1._connections

    # disconnect
    cell1.disconnect(cell2)
    assert cell2 not in cell1._connections

    # remove cell not in connections
    with pytest.raises(ValueError):
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
