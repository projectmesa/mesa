from itertools import product
from random import Random
from typing import Callable

from mesa.experimental.cell_space import Cell, DiscreteSpace


class Grid(DiscreteSpace):
    """Base class for all grid classes

    Attributes:
        width (int): width of the grid
        height (int): height of the grid
        torus (bool): whether the grid is a torus
        _try_random (bool): whether to get empty cell be repeatedly trying random cell

    """

    def __init__(
        self,
        dimensions: list[int],
        torus: bool = False,
        capacity: int | None = None,
        random: Random | None = None,
        cell_klass: type[Cell] = Cell,
    ) -> None:
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.torus = torus
        self.dimensions = dimensions
        self._try_random = True

        self._validate_parameters()

        coordinates = product(*(range(dim) for dim in self.dimensions))

        self._cells = {
            coord: cell_klass(coord, capacity, random=self.random)
            for coord in coordinates
        }

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _validate_parameters(self):
        if not all(isinstance(dim, int) and dim > 0 for dim in self.dimensions):
            raise ValueError("Dimensions must be a list of positive integers.")
        if not isinstance(self.torus, bool):
            raise ValueError("Torus must be a boolean.")
        if self.capacity is not None and not isinstance(self.capacity, int):
            raise ValueError("Capacity must be an integer or None.")

    def _calculate_neighborhood_offsets(self, cell: Cell) -> list[tuple[int, int]]:
        # Default implementation
        return []

    def select_random_empty_cell(self) -> Cell:
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

    def _connect_single_cell(self, cell):
        coord = cell.coordinate

        for d_coord in self._calculate_neighborhood_offsets(cell):
            n_coord = tuple(c + dc for c, dc in zip(coord, d_coord))
            if self.torus:
                n_coord = tuple(nc % d for nc, d in zip(n_coord, self.dimensions))
            if all(0 <= nc < d for nc, d in zip(n_coord, self.dimensions)):
                cell.connect(self._cells[n_coord])


class OrthogonalMooreGrid(Grid):
    """Grid where cells are connected to their 8 neighbors.

    Example for two dimensions:
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]
    """

    def _calculate_neighborhood_offsets(self, cell):

        offsets = list(product([-1, 0, 1], repeat=len(self.dimensions)))
        offsets.remove((0,) * len(self.dimensions))  # Remove the central cell
        return offsets


class OrthogonalVonNeumannGrid(Grid):
    """Grid where cells are connected to their 4 neighbors.

    Example for two dimensions:
    directions = [
                (0, -1),
        (-1, 0),         ( 1, 0),
                (0,  1),
    ]
    """

    def _calculate_neighborhood_offsets(self, cell: Cell):
        """
        Calculates the offsets for a Von Neumann neighborhood in an n-dimensional grid.
        This neighborhood includes all cells that are one step away in any single dimension.

        Returns:
            A list of tuples representing the relative positions of neighboring cells.
        """
        offsets = []
        dimensions = len(self.dimensions)
        for dim in range(dimensions):
            for delta in [
                -1,
                1,
            ]:  # Move one step in each direction for the current dimension
                offset = [0] * dimensions
                offset[dim] = delta
                offsets.append(tuple(offset))
        return offsets


class HexGrid(Grid):

    def _validate_parameters(self):
        super()._validate_parameters()
        if len(self.dimensions) != 2:
            raise ValueError("HexGrid must have exactly 2 dimensions.")

    @staticmethod
    def _calculate_neighborhood_offsets(cell):
        i, j = cell.coordinate

        # fmt: off
        if i % 2 == 0:
            offsets = [
                    (-1, -1), (-1, 0),
                ( 0, -1),        ( 0, 1),
                    ( 1, -1), ( 1, 0),
            ]
        else:
            offsets = [
                    (-1, 0), (-1, 1),
                ( 0, -1),       ( 0, 1),
                    ( 1, 0), ( 1, 1),
            ]
        # fmt: on

        return offsets
