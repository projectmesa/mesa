"""Grid-based cell space implementations with different connection patterns.

Provides several grid types for organizing cells:
- OrthogonalMooreGrid: 8 neighbors in 2D, (3^n)-1 in nD
- OrthogonalVonNeumannGrid: 4 neighbors in 2D, 2n in nD
- HexGrid: 6 neighbors in hexagonal pattern (2D only)

Each grid type supports optional wrapping (torus) and cell capacity limits.
Choose based on how movement and connectivity should work in your model -
Moore for unrestricted movement, Von Neumann for orthogonal-only movement,
or Hex for more uniform distances.
"""

from __future__ import annotations

import copyreg
from collections.abc import Sequence
from itertools import product
from random import Random
from typing import Any, Generic, TypeVar

from mesa.experimental.cell_space import Cell, DiscreteSpace
from mesa.experimental.cell_space.property_layer import (
    HasPropertyLayers,
    PropertyDescriptor,
)

T = TypeVar("T", bound=Cell)


def pickle_gridcell(obj):
    """Helper function for pickling GridCell instances."""
    # we have the base class and the state via __getstate__
    args = obj.__class__.__bases__[0], obj.__getstate__()
    return unpickle_gridcell, args


def unpickle_gridcell(parent, fields):
    """Helper function for unpickling GridCell instances."""
    # since the class is dynamically created, we recreate it here
    cell_klass = type(
        "GridCell",
        (parent,),
        {"_mesa_properties": set()},
    )
    instance = cell_klass(
        (0, 0)
    )  # we use a default coordinate and overwrite it with the correct value next

    # __gestate__ returns a tuple with dict and slots, but slots contains the dict so we can just use the
    # second item only
    for k, v in fields[1].items():
        if k != "__dict__":
            setattr(instance, k, v)

    return instance


class Grid(DiscreteSpace[T], Generic[T], HasPropertyLayers):
    """Base class for all grid classes.

    Attributes:
        dimensions (Sequence[int]): the dimensions of the grid
        torus (bool): whether the grid is a torus
        capacity (int): the capacity of a grid cell
        random (Random): the random number generator
        _try_random (bool): whether to get empty cell be repeatedly trying random cell

    Notes:
        width and height are accessible via properties, higher dimensions can be retrieved via dimensions

    """

    @property
    def width(self) -> int:
        """Convenience access to the width of the grid."""
        return self.dimensions[0]

    @property
    def height(self) -> int:
        """Convenience access to the height of the grid."""
        return self.dimensions[1]

    def __init__(
        self,
        dimensions: Sequence[int],
        torus: bool = False,
        capacity: float | None = None,
        random: Random | None = None,
        cell_klass: type[T] = Cell,
    ) -> None:
        """Initialise the grid class.

        Args:
            dimensions: the dimensions of the space
            torus: whether the space wraps
            capacity: capacity of the grid cell
            random: a random number generator
            cell_klass: the base class to use for the cells
        """
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.torus = torus
        self.dimensions = dimensions
        self._try_random = True
        self._ndims = len(dimensions)
        self._validate_parameters()
        self.cell_klass = type(
            "GridCell",
            (self.cell_klass,),
            {"_mesa_properties": set()},
        )

        # we register the pickle_gridcell helper function
        copyreg.pickle(self.cell_klass, pickle_gridcell)

        coordinates = product(*(range(dim) for dim in self.dimensions))

        self._cells = {
            coord: self.cell_klass(coord, capacity, random=self.random)
            for coord in coordinates
        }
        self._connect_cells()
        self.create_property_layer("empty", default_value=True, dtype=bool)

    def _connect_cells(self) -> None:
        if self._ndims == 2:
            self._connect_cells_2d()
        else:
            self._connect_cells_nd()

    def _connect_cells_2d(self) -> None: ...

    def _connect_cells_nd(self) -> None: ...

    def _validate_parameters(self):
        if not all(isinstance(dim, int) and dim > 0 for dim in self.dimensions):
            raise ValueError("Dimensions must be a list of positive integers.")
        if not isinstance(self.torus, bool):
            raise ValueError("Torus must be a boolean.")
        if self.capacity is not None and not isinstance(self.capacity, float | int):
            raise ValueError("Capacity must be a number or None.")

    def select_random_empty_cell(self) -> T:  # noqa
        # FIXME:: currently just a simple boolean to control behavior
        # FIXME:: basically if grid is close to 99% full, creating empty list can be faster
        # FIXME:: note however that the old results don't apply because in this implementation
        # FIXME:: because empties list needs to be rebuild each time
        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052 and
        # https://github.com/projectmesa/mesa/pull/1565. The cutoff value provided
        # is the break-even comparison with the time taken in the else branching point.
        if self._try_random:
            while True:
                cell = self.all_cells.select_random_cell()
                if cell.is_empty:
                    return cell
        else:
            return super().select_random_empty_cell()

    def _connect_single_cell_nd(self, cell: T, offsets: list[tuple[int, ...]]) -> None:
        coord = cell.coordinate

        for d_coord in offsets:
            n_coord = tuple(c + dc for c, dc in zip(coord, d_coord))
            if self.torus:
                n_coord = tuple(nc % d for nc, d in zip(n_coord, self.dimensions))
            if all(0 <= nc < d for nc, d in zip(n_coord, self.dimensions)):
                cell.connect(self._cells[n_coord], d_coord)

    def _connect_single_cell_2d(self, cell: T, offsets: list[tuple[int, int]]) -> None:
        i, j = cell.coordinate
        height, width = self.dimensions

        for di, dj in offsets:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % height, nj % width
            if 0 <= ni < height and 0 <= nj < width:
                cell.connect(self._cells[ni, nj], (di, dj))

    def __getstate__(self) -> dict[str, Any]:
        """Custom __getstate__ for handling dynamic GridCell class and PropertyDescriptors."""
        state = super().__getstate__()
        state = {k: v for k, v in state.items() if k != "cell_klass"}
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Custom __setstate__ for handling dynamic GridCell class and PropertyDescriptors."""
        self.__dict__ = state
        self._connect_cells()  # using super fails for this for some reason, so we repeat ourselves

        self.cell_klass = type(
            self._cells[(0, 0)]
        )  # the __reduce__ function handles this for us nicely
        for layer in self._mesa_property_layers.values():
            setattr(self.cell_klass, layer.name, PropertyDescriptor(layer))


class OrthogonalMooreGrid(Grid[T]):
    """Grid where cells are connected to their 8 neighbors.

    Example for two dimensions:
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]
    """

    def _connect_cells_2d(self) -> None:
        # fmt: off
        offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        # fmt: on

        for cell in self.all_cells:
            self._connect_single_cell_2d(cell, offsets)

    def _connect_cells_nd(self) -> None:
        offsets = list(product([-1, 0, 1], repeat=len(self.dimensions)))
        offsets.remove((0,) * len(self.dimensions))  # Remove the central cell

        for cell in self.all_cells:
            self._connect_single_cell_nd(cell, offsets)


class OrthogonalVonNeumannGrid(Grid[T]):
    """Grid where cells are connected to their 4 neighbors.

    Example for two dimensions:
    directions = [
                (0, -1),
        (-1, 0),         ( 1, 0),
                (0,  1),
    ]
    """

    def _connect_cells_2d(self) -> None:
        # fmt: off
        offsets = [
                    (-1, 0),
            (0, -1),         (0, 1),
                    ( 1, 0),
        ]
        # fmt: on

        for cell in self.all_cells:
            self._connect_single_cell_2d(cell, offsets)

    def _connect_cells_nd(self) -> None:
        offsets: list[tuple[int, ...]] = []
        dimensions = len(self.dimensions)
        for dim in range(dimensions):
            for delta in [
                -1,
                1,
            ]:  # Move one step in each direction for the current dimension
                offset = [0] * dimensions
                offset[dim] = delta
                offsets.append(tuple(offset))

        for cell in self.all_cells:
            self._connect_single_cell_nd(cell, offsets)


class HexGrid(Grid[T]):
    """A Grid with hexagonal tilling of the space."""

    def _connect_cells_2d(self) -> None:
        # fmt: off
        even_offsets = [
                        (-1, -1), (0, -1),
                    ( -1, 0),        ( 1, 0),
                        ( -1, 1), (0, 1),
                ]
        odd_offsets = [
                        (0, -1), (1, -1),
                    ( -1, 0),       ( 1, 0),
                        ( 0, 1), ( 1, 1),
                ]
        # fmt: on

        for cell in self.all_cells:
            i = cell.coordinate[1]
            offsets = even_offsets if i % 2 else odd_offsets
            self._connect_single_cell_2d(cell, offsets=offsets)

    def _connect_cells_nd(self) -> None:
        raise NotImplementedError("HexGrids are only defined for 2 dimensions")

    def _validate_parameters(self):
        super()._validate_parameters()
        if len(self.dimensions) != 2:
            raise ValueError("HexGrid must have exactly 2 dimensions.")
