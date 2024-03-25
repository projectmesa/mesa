from __future__ import annotations

from functools import cached_property
from random import Random
from typing import Generic, TypeVar

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.cell_collection import CellCollection

T = TypeVar("T", bound=Cell)


class DiscreteSpace(Generic[T]):
    """Base class for all discrete spaces.

    Attributes:
        capacity (int): The capacity of the cells in the discrete space
        all_cells (CellCollection): The cells composing the discrete space
        random (Random): The random number generator
        cell_klass (Type) : the type of cell class
        empties (CellCollection) : collecction of all cells that are empty

    """

    def __init__(
        self,
        capacity: int | None = None,
        cell_klass: type[T] = Cell,
        random: Random | None = None,
    ):
        super().__init__()
        self.capacity = capacity
        self._cells: dict[tuple[int, ...], T] = {}
        if random is None:
            random = Random()  # FIXME should default to default rng from model
        self.random = random
        self.cell_klass = cell_klass

        self._empties: dict[tuple[int, ...], None] = {}
        self._empties_initialized = False

    @property
    def cutoff_empties(self):
        return 7.953 * len(self._cells) ** 0.384

    def _connect_single_cell(self, cell: T): ...

    @cached_property
    def all_cells(self):
        return CellCollection({cell: cell.agents for cell in self._cells.values()})

    def __iter__(self):
        return iter(self._cells.values())

    def __getitem__(self, key):
        return self._cells[key]

    @property
    def empties(self) -> CellCollection:
        return self.all_cells.select(lambda cell: cell.is_empty)

    def select_random_empty_cell(self) -> T:
        """select random empty cell"""
        return self.random.choice(list(self.empties))
