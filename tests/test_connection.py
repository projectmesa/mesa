import pytest

from mesa.experimental.cell_space import (
    Cell,
)


def test_get_connection():
    cell = Cell(coordinate=(0, 0))
    right_cell = Cell(coordinate=(1, 0))
    left_cell = Cell(coordinate=(-1, 0))

    cell.connect(right_cell, "right")

    assert cell._connections["right"].coordinate == right_cell.coordinate
    assert cell._connections[0].coordinate == right_cell.coordinate

    with pytest.raises(KeyError):
        left = cell._connections["left"]

    with pytest.raises(TypeError):
        obj = {
            "name": "right",
        }
        random_cell = cell._connections[obj]


def test_in_connection():
    cell = Cell(coordinate=(0, 0))
    right_cell = Cell(coordinate=(1, 0))
    left_cell = Cell(coordinate=(-1, 0))

    cell.connect(right_cell, "right")

    assert right_cell in cell._connections
    assert left_cell not in cell._connections

    assert 0 in cell._connections
    assert 2 not in cell._connections

    with pytest.raises(TypeError):
        obj = {
            "name": "right",
        }
        is_in = obj in cell._connections


def test_add_connection():
    cell = Cell(coordinate=(0, 0))
    right_cell = Cell(coordinate=(1, 0))
    left_cell = Cell(coordinate=(-1, 0))

    cell.connect(right_cell, "right")

    # Raises exception when adding duplicated name
    with pytest.raises(ValueError):
        cell.connect(left_cell, "right")


def test_remove_connection():
    cell = Cell(coordinate=(0, 0))
    right_cell = Cell(coordinate=(1, 0))
    left_cell = Cell(coordinate=(-1, 0))
    bot_cell = Cell(coordinate=(0, -1))

    cell.connect(right_cell, "right")
    cell.connect(left_cell, "left")
    cell.connect(bot_cell, "bottom")

    assert 2 in cell._connections
    cell._connections.remove(2)
    assert 2 not in cell._connections

    assert "left" in cell._connections
    cell._connections.remove(left_cell)
    assert "left" not in cell._connections

    assert "right" in cell._connections
    cell._connections.remove("right")
    assert "right" not in cell._connections

    # Raises exception when removing non-exsistent name
    with pytest.raises(ValueError):
        cell._connections.remove("top")

    with pytest.raises(ValueError):
        cell._connections.remove(123)

    with pytest.raises(TypeError):
        obj = {
            "name": "right",
        }
        cell._connections.remove(obj)
