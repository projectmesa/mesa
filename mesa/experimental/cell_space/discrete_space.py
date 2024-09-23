"""DiscreteSpace base class."""

from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from random import Random
from typing import Any, Generic, TypeVar

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
        empties (CellCollection) : collecction of all cells that are empty
        property_layers (dict[str, PropertyLayer]): the property layers of the grid
    """

    def __init__(
        self,
        capacity: int | None = None,
        cell_klass: type[T] = Cell,
        random: Random | None = None,
        property_layers: None | PropertyLayer | list[PropertyLayer] = None,
    ):
        """Instantiate a DiscreteSpace.

        Args:
            capacity: capacity of cells
            cell_klass: base class for all cells
            random: random number generator
            property_layers: property layers to add to the grid
        """
        super().__init__()
        self.capacity = capacity
        self._cells: dict[tuple[int, ...], T] = {}
        if random is None:
            random = Random()  # FIXME should default to default rng from model
        self.random = random
        self.cell_klass = cell_klass

        self._empties: dict[tuple[int, ...], None] = {}
        self._empties_initialized = False
        self.property_layers: dict[str, PropertyLayer] = {}
        if property_layers:
            if isinstance(property_layers, PropertyLayer):
                property_layers = [property_layers]
            for layer in property_layers:
                self.add_property_layer(layer)

    @property
    def cutoff_empties(self):  # noqa
        return 7.953 * len(self._cells) ** 0.384

    def _connect_single_cell(self, cell: T): ...

    @cached_property
    def all_cells(self):
        """Return all cells in space."""
        return CellCollection({cell: cell.agents for cell in self._cells.values()})

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
        """Add a property layer to the grid."""
        if property_layer.name in self.property_layers:
            raise ValueError(f"Property layer {property_layer.name} already exists.")
        self.property_layers[property_layer.name] = property_layer
        if add_to_cells:
            for cell in self._cells.values():
                cell.property_layers[property_layer.name] = property_layer

    def remove_property_layer(self, property_name: str, remove_from_cells: bool = True):
        """Remove a property layer from the grid."""
        del self.property_layers[property_name]
        if remove_from_cells:
            for cell in self._cells.values():
                del cell.property_layers[property_name]

    def set_property(
        self, property_name: str, value, condition: Callable[[T], bool] | None = None
    ):
        """Set the value of a property for all cells in the grid."""
        self.property_layers[property_name].set_cells(value, condition)

    def modify_properties(
        self,
        property_name: str,
        operation: Callable,
        value: Any = None,
        condition: Callable[[T], bool] | None = None,
    ):
        """Modify the values of a specific property for all cells in the grid."""
        self.property_layers[property_name].modify_cells(operation, value, condition)
