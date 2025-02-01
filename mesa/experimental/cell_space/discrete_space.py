"""Base class for building cell-based spatial environments.

DiscreteSpace provides the core functionality needed by all cell-based spaces:
- Cell creation and tracking
- Agent-cell relationship management
- Property layer support
- Random selection capabilities
- Capacity management

This serves as the foundation for specific space implementations like grids
and networks, ensuring consistent behavior and shared functionality across
different space types. All concrete cell space implementations (grids, networks, etc.)
inherit from this class.
"""

from __future__ import annotations

import warnings
from functools import cached_property
from random import Random
from typing import Generic, TypeVar

from mesa.agent import AgentSet
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
        empties (CellCollection) : collection of all cells that are empty
        property_layers (dict[str, PropertyLayer]): the property layers of the discrete space

    Notes:
        A `UserWarning` is issued if `random=None`. You can resolve this warning by explicitly
        passing a random number generator. In most cases, this will be the seeded random number
        generator in the model. So, you would do `random=self.random` in a `Model` or `Agent` instance.

    """

    def __init__(
        self,
        capacity: int | None = None,
        cell_klass: type[T] = Cell,
        random: Random | None = None,
    ):
        """Instantiate a DiscreteSpace.

        Args:
            capacity: capacity of cells
            cell_klass: base class for all cells
            random: random number generator
        """
        super().__init__()
        self.capacity = capacity
        self._cells: dict[tuple[int, ...], T] = {}
        if random is None:
            warnings.warn(
                "Random number generator not specified, this can make models non-reproducible. Please pass a random number generator explicitly",
                UserWarning,
                stacklevel=2,
            )
            random = Random()
        self.random = random
        self.cell_klass = cell_klass

        self._empties: dict[tuple[int, ...], None] = {}

    @property
    def cutoff_empties(self):  # noqa
        return 7.953 * len(self._cells) ** 0.384

    @property
    def agents(self) -> AgentSet:
        """Return an AgentSet with the agents in the space."""
        return AgentSet(self.all_cells.agents, random=self.random)

    def _connect_cells(self): ...
    def _connect_single_cell(self, cell: T): ...

    @cached_property
    def all_cells(self):
        """Return all cells in space."""
        return CellCollection(
            {cell: cell.agents for cell in self._cells.values()}, random=self.random
        )

    def __iter__(self):  # noqa
        return iter(self._cells.values())

    def __getitem__(self, key: tuple[int, ...]) -> T:  # noqa: D105
        return self._cells[key]

    @property
    def empties(self) -> CellCollection[T]:
        """Return all empty in spaces."""
        return self.all_cells.select(lambda cell: cell.is_empty)

    def select_random_empty_cell(self) -> T:
        """Select random empty cell."""
        return self.random.choice(list(self.empties))

    def __setstate__(self, state):
        """Set the state of the discrete space and rebuild the connections."""
        self.__dict__ = state
        self._connect_cells()
