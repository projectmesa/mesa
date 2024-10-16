"""A Network grid."""

from random import Random
from typing import Any

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.discrete_space import DiscreteSpace


class Network(DiscreteSpace[Cell]):
    """A networked discrete space."""

    def __init__(
        self,
        G: Any,  # noqa: N803
        capacity: int | None = None,
        random: Random | None = None,
        cell_klass: type[Cell] = Cell,
    ) -> None:
        """A Networked grid.

        Args:
            G: a NetworkX Graph instance.
            capacity (int) : the capacity of the cell
            random (Random): a random number generator
            cell_klass (type[Cell]): The base Cell class to use in the Network

        """
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.G = G

        for node_id in self.G.nodes:
            self._cells[node_id] = self.cell_klass(
                node_id, capacity, random=self.random
            )

        self._connect_cells()

    def _connect_cells(self) -> None:
        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell: Cell):
        for node_id in self.G.neighbors(cell.coordinate):
            cell.connect(self._cells[node_id], node_id)
