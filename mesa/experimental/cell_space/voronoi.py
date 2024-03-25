from collections.abc import Sequence
from itertools import combinations
from random import Random
from typing import Optional

from pyhull.delaunay import DelaunayTri

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.discrete_space import DiscreteSpace


class VoronoiGrid(DiscreteSpace):
    def __init__(
        self,
        centroids_coordinates: Sequence[Sequence[float]],
        capacity: Optional[float] = None,
        random: Optional[Random] = None,
        cell_klass: type[Cell] = Cell,
    ) -> None:
        """A Voronoi Tessellation Grid

        Args:
            centroids_coordinates: coordinates of centroids to build the tessellation space
            capacity (int) : capacity of the cells in the discrete space
            random (Random): random number generator
            CellKlass (type[Cell]): type of cell class
        """
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.centroids_coordinates = centroids_coordinates
        self._validate_parameters()

        self._cells = {
            i: cell_klass(self.centroids_coordinates[i], capacity, random=self.random)
            for i in range(len(self.centroids_coordinates))
        }

        self._connect_cells()

    def _connect_cells(self) -> None:
        """Connect cells to neighbors based on given centroids and using Delaunay Triangulation"""
        triangulation = DelaunayTri(self.centroids_coordinates)

        for p in triangulation.vertices:
            for i, j in combinations(p, 2):
                self._cells[i].connect(self._cells[j])
                self._cells[j].connect(self._cells[i])

    def _validate_parameters(self) -> None:
        if self.capacity is not None and not isinstance(self.capacity, (float, int)):
            raise ValueError("Capacity must be a number or None.")
        if not isinstance(self.centroids_coordinates, Sequence) and not isinstance(
            self.centroids_coordinates[0], Sequence
        ):
            raise ValueError("Centroids should be a list of lists")
        dimension_1 = len(self.centroids_coordinates[0])
        for coordinate in self.centroids_coordinates:
            if dimension_1 != len(coordinate):
                raise ValueError("Centroid coordinates should be a homogeneous array")
