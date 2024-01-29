
from mesa.experimental.cell_space import CellAgent, CellCollection, OrthogonalGrid, HexGrid, NetworkGrid



def test_orthogonal_grid():
    width = 10
    height = 10
    grid = OrthogonalGrid(width, height, torus=False, moore=False, capacity=None)

    assert len(grid.cells) == width * height

    # von neumann neighborhood, torus false, top corner
    assert len(grid.cells[(0, 0)]._connections) == 2
    for connection in grid.cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0)}

    # von neumann neighborhood middle of grid
    assert len(grid.cells[(5, 5)]._connections) == 4
    for connection in grid.cells[(5, 5)]._connections:
        assert connection.coordinate in {(4, 5), (5, 4), (5,6), (6,5)}

    # von neumann neighborhood, torus True, top corner
    grid = OrthogonalGrid(width, height, torus=True, moore=False, capacity=None)
    assert len(grid.cells[(0, 0)]._connections) == 4
    for connection in grid.cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0), (0, 9), (9,0)}


    # Moore neighborhood, torus false, top corner
    grid = OrthogonalGrid(width, height, torus=False, moore=True, capacity=None)
    assert len(grid.cells[(0, 0)]._connections) == 3
    for connection in grid.cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0), (1,1)}

    # Moore neighborhood middle of grid
    assert len(grid.cells[(5, 5)]._connections) == 8
    for connection in grid.cells[(5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 4), (4, 5), (4, 6),
                                         (5, 4),         (5, 6),
                                         (6, 4), (6, 5), (6, 6)}
        # fmt: on

    # Moore neighborhood, torus True, top corner
    grid = OrthogonalGrid(10, 10, torus=True, moore=True, capacity=None)
    assert len(grid.cells[(0, 0)]._connections) == 8
    for connection in grid.cells[(0, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(9, 9), (9, 0), (9, 1),
                                         (0, 9),         (0, 1),
                                         (1, 9), (1, 0), (1, 1)}
        # fmt: on

def test_cell_neighborhood():
    # orthogonal grid
    width = 10
    height = 10

    ## von Neumann
    grid = OrthogonalGrid(width, height, torus=False, moore=False, capacity=None)
    for radius, n in zip(range(1, 4), [2,  5, 9]):
        neighborhood = grid.cells[(0, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    width = 10
    height = 10

    grid = OrthogonalGrid(width, height, torus=False, moore=True, capacity=None)
    for radius, n in zip(range(1, 4), [3,  8, 15]):
        neighborhood = grid.cells[(0, 0)].neighborhood(radius=radius)
        assert len(neighborhood) == n

    ## Moore


    # hexgrid

    # networkgrid


def test_hexgrid():
    width = 10
    height = 10

    grid = HexGrid(width, height, torus=False)
    assert len(grid.cells) == width * height

    # first row
    assert len(grid.cells[(0, 0)]._connections) == 2
    for connection in grid.cells[(0, 0)]._connections:
        assert connection.coordinate in {(0, 1), (1, 0)}

    # second row
    assert len(grid.cells[(1, 0)]._connections) == 5
    for connection in grid.cells[(1, 0)]._connections:
        # fmt: off
        assert connection.coordinate in {(0, 0), (0, 1),
                                                    (1, 1),
                                         (2, 0), (2, 1)}

    # middle odd row
    assert len(grid.cells[(5, 5)]._connections) == 6
    for connection in grid.cells[(5, 5)]._connections:
        # fmt: off
        assert connection.coordinate in {(4, 5), (4, 6),
                                      (5, 4),       (5, 6),
                                         (6, 5), (6, 6)}

        # fmt: on

    # middle even row
    assert len(grid.cells[(4, 4)]._connections) == 6
    for connection in grid.cells[(4, 4)]._connections:
        # fmt: off
        assert connection.coordinate in {(3, 3), (3, 4),
                                      (4, 3),       (4, 5),
                                         (5, 3), (5, 4)}

        # fmt: on

# def test_networkgrid():
#     grid = NetworkGrid()