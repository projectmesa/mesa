import random
from functools import cached_property

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.cell_collection import CellCollection
from mesa.space import Coordinate


class DiscreteSpace:
    # FIXME:: random should become a keyword argument
    # FIXME:: defaulting to the same rng as model.random.
    # FIXME:: all children should be also like that.

    def __init__(
        self,
        capacity: int | None = None,
    ):
        super().__init__()
        self.capacity = capacity
        self.cells: dict[Coordinate, Cell] = {}
        self.random = random  # FIXME

        self._empties: dict[Coordinate, None] = {}
        self.cutoff_empties = -1
        self.empties_initialized = False

    def _connect_single_cell(self, cell):
        ...

    def _initialize_empties(self):
        self._empties = {
            cell.coordinate: None for cell in self.cells.values() if cell.is_empty
        }
        self.cutoff_empties = 7.953 * len(self.cells) ** 0.384
        self.empties_initialized = True

    @cached_property
    def all_cells(self):
        return CellCollection({cell: cell.agents for cell in self.cells.values()})

    def __iter__(self):
        return iter(self.cells.values())

    def __getitem__(self, key):
        return self.cells[key]

    @property
    def empties(self) -> CellCollection:
        return self.all_cells.select(lambda cell: cell.is_empty)

    def select_random_empty_cell(self) -> Cell:
        if not self.empties_initialized:
            self._initialize_empties()

        return self.cells[self.random.choice(list(self._empties))]
