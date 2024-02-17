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
        neighborhood_func: Callable[[Cell], list[tuple[int, int]]] | None = None,
    ) -> None:
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.torus = torus
        self.dimensions = dimensions
        self._try_random = True
        if neighborhood_func is not None:
            self.neighborhood_func = neighborhood_func
        else:
            self.neighborhood_func = self._default_neighborhood_func

        coordinates = product(*(range(dim) for dim in self.dimensions))

        self._cells = {
            coord: cell_klass(coord, capacity, random=self.random)
            for coord in coordinates
        }

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    @staticmethod
    def _default_neighborhood_func(cell: Cell) -> list[tuple[int, int]]:
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

        for d_coord in self.neighborhood_func(cell):
            n_coord = tuple(c + dc for c, dc in zip(coord, d_coord))
            if self.torus:
                n_coord = tuple(nc % d for nc, d in zip(n_coord, self.dimensions))
            if all(0 <= nc < d for nc, d in zip(n_coord, self.dimensions)):
                cell.connect(self._cells[n_coord])

        # i, j = cell.coordinate

        # for di, dj in self.neighborhood_func(cell):
        #     ni, nj = (i + di, j + dj)
        #     if self.torus:
        #         ni, nj = ni % self.height, nj % self.width
        #     if 0 <= ni < self.height and 0 <= nj < self.width:
        #         cell.connect(self._cells[ni, nj])


class OrthogonalMooreGrid(Grid):

    @staticmethod
    def _default_neighborhood_func(cell):
        # fmt: off
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        # fmt: on
        return directions


class OrthogonalVonNeumannGrid(Grid):

    @staticmethod
    def _default_neighborhood_func(cell):
        # fmt: off
        directions = [
                    (0, -1),
            (-1, 0),         ( 1, 0),
                    (0,  1),
        ]
        # fmt: on
        return directions


class HexGrid(Grid):

    @staticmethod
    def _default_neighborhood_func(cell):
        i, j = cell.coordinate

        # fmt: off
        if i % 2 == 0:
            directions = [
                    (-1, -1), (-1, 0),
                ( 0, -1),        ( 0, 1),
                    ( 1, -1), ( 1, 0),
            ]
        else:
            directions = [
                    (-1, 0), (-1, 1),
                ( 0, -1),       ( 0, 1),
                    ( 1, 0), ( 1, 1),
            ]
        # fmt: on

        return directions
