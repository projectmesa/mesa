from collections.abc import Sequence
from itertools import combinations
from random import Random
from typing import Optional

from numpy import array as np_array
from numpy.random import uniform as np_uniform
from pyhull.delaunay import DelaunayTri

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.discrete_space import DiscreteSpace


class VoronoiGrid(DiscreteSpace):
    def __init__(
        self,
        dimensions: Optional[Sequence[int]] = None,
        density: Optional[float] = None,
        capacity: float | None = None,
        random: Optional[Random] = None,
        cell_klass: type[Cell] = Cell,
    ) -> None:
        """A Voronoi Tessellation Grid

        Args:
            dimensions (Sequence[int]): a sequence of space dimensions
            density (float): density of cells in the space
            capacity (int) : the capacity of the cell
            random (Random):
            CellKlass (type[Cell]): The base Cell class to use in the Network

        """
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.dimensions = dimensions
        self.density = density
        self._ndims = len(dimensions)
        self._validate_parameters()

        _grid_total_space = 1
        for dim in self.dimensions:
            _grid_total_space *= dim

        self.number_cells = _grid_total_space * density

        self.np_coordinates = np_array(
            [np_uniform(0, dim, self.number_cells) for dim in self.dimensions]
        ).T

        self._cells = {
            i: cell_klass(self.np_coordinates[i], capacity, random=self.random)
            for i in range(self.number_cells)
        }

        self._connect_cells()

    def _connect_cells(self):
        self._connect_cells_nd()

    def _connect_cells_nd(self):
        triangulation = DelaunayTri(self.np_coordinates)

        for p in triangulation.vertices:
            for i, j in combinations(p, 2):
                self._cells[i].connect(self._cells[j])
                self._cells[j].connect(self._cells[i])

    def _validate_parameters(self):
        if not isinstance(self.density, float) and not (self.density > 0):
            raise ValueError("Density should be a positive float.")
        if not all(isinstance(dim, int) and dim > 0 for dim in self.dimensions):
            raise ValueError("Dimensions must be a list of positive integers.")
        if self.capacity is not None and not isinstance(self.capacity, (float, int)):
            raise ValueError("Capacity must be a number or None.")
