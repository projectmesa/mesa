"""DiscreteSpace base class."""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import cached_property
from random import Random
from typing import Any, Generic, TypeVar

from mesa.agent import AgentSet
from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.cell_collection import CellCollection
from mesa.space import PropertyLayer

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
        self._empties_initialized = False
        self.property_layers: dict[str, PropertyLayer] = {}

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

    # PropertyLayer methods
    def add_property_layer(
        self, property_layer: PropertyLayer, add_to_cells: bool = True
    ):
        """Add a property layer to the grid.

        Args:
            property_layer: the property layer to add
            add_to_cells: whether to add the property layer to all cells (default: True)
        """
        if property_layer.name in self.property_layers:
            raise ValueError(f"Property layer {property_layer.name} already exists.")
        self.property_layers[property_layer.name] = property_layer
        if add_to_cells:
            for cell in self._cells.values():
                cell._mesa_property_layers[property_layer.name] = property_layer

    def remove_property_layer(self, property_name: str, remove_from_cells: bool = True):
        """Remove a property layer from the grid.

        Args:
            property_name: the name of the property layer to remove
            remove_from_cells: whether to remove the property layer from all cells (default: True)
        """
        del self.property_layers[property_name]
        if remove_from_cells:
            for cell in self._cells.values():
                del cell._mesa_property_layers[property_name]

    def set_property(
        self, property_name: str, value, condition: Callable[[T], bool] | None = None
    ):
        """Set the value of a property for all cells in the grid.

        Args:
            property_name: the name of the property to set
            value: the value to set
            condition: a function that takes a cell and returns a boolean
        """
        self.property_layers[property_name].set_cells(value, condition)

    def modify_properties(
        self,
        property_name: str,
        operation: Callable,
        value: Any = None,
        condition: Callable[[T], bool] | None = None,
    ):
        """Modify the values of a specific property for all cells in the grid.

        Args:
            property_name: the name of the property to modify
            operation: the operation to perform
            value: the value to use in the operation
            condition: a function that takes a cell and returns a boolean (used to filter cells)
        """
        self.property_layers[property_name].modify_cells(operation, value, condition)

    def __setstate__(self, state):
        """Set the state of the discrete space and rebuild the connections."""
        self.__dict__ = state
        self._connect_cells()
