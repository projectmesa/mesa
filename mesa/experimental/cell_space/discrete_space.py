from functools import cached_property
from random import Random

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.cell_collection import CellCollection
from mesa.space import Coordinate


class DiscreteSpace:
    # FIXME:: random should become a keyword argument

    def __init__(
        self,
        capacity: int | None = None,
        cell_klass: type[Cell] = Cell,
        random: Random | None = None
    ):
        super().__init__()
        self.capacity = capacity
        self.cells: dict[Coordinate, Cell] = {}
        if random is None:
            random = Random()  # FIXME should default to default rng from model
        self.random = random
        self.cell_klass = cell_klass

        self._empties: dict[Coordinate, None] = {}
        self.empties_initialized = False

    @property
    def cutoff_empties(self):
        return 7.953 * len(self.cells) ** 0.384

    def _connect_single_cell(self, cell):
        ...

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
        """select random empty cell"""
        return self.random.choice(list(self.empties))
