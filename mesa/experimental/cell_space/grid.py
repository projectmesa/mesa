"""Various Grid Spaces."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import product
from random import Random
from typing import Generic, TypeVar

from mesa.experimental.cell_space import Cell, DiscreteSpace

T = TypeVar("T", bound=Cell)


class Grid(DiscreteSpace[T], Generic[T]):
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

        coordinates = product(*(range(dim) for dim in self.dimensions))

        self._cells = {
            coord: cell_klass(coord, capacity, random=self.random)
            for coord in coordinates
        }
        self._connect_cells()

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
                        (-1, -1), (-1, 0),
                    ( 0, -1),        ( 0, 1),
                        ( 1, -1), ( 1, 0),
                ]
        odd_offsets = [
                        (-1, 0), (-1, 1),
                    ( 0, -1),       ( 0, 1),
                        ( 1, 0), ( 1, 1),
                ]
        # fmt: on

        for cell in self.all_cells:
            i = cell.coordinate[0]
            offsets = even_offsets if i % 2 == 0 else odd_offsets
            self._connect_single_cell_2d(cell, offsets=offsets)

    def _connect_cells_nd(self) -> None:
        raise NotImplementedError("HexGrids are only defined for 2 dimensions")

    def _validate_parameters(self):
        super()._validate_parameters()
        if len(self.dimensions) != 2:
            raise ValueError("HexGrid must have exactly 2 dimensions.")
