from typing import Any

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.discrete_space import DiscreteSpace


class Network(DiscreteSpace):
    def __init__(self, G: Any, capacity: int | None = None) -> None:
        """A Networked grid

        Args:
            G: a NetworkX Graph instance.
            capacity (int) : the capacity of the cell

        """
        super().__init__(capacity)
        self.G = G

        for node_id in self.G.nodes:
            self.cells[node_id] = Cell(node_id, self, capacity)

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        for node_id in self.G.neighbors(cell.coordinate):
            cell.connect(self.cells[node_id])
