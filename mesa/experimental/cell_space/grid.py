from __future__ import annotations

from collections.abc import Sequence
from itertools import product
from random import Random
from typing import Generic, TypeVar

from mesa.experimental.cell_space import Cell, DiscreteSpace
from mesa.space import PropertyLayer

T = TypeVar("T", bound=Cell)


class Grid(DiscreteSpace, Generic[T]):
    """Base class for all grid classes

    Attributes:
        dimensions (Sequence[int]): the dimensions of the grid
        torus (bool): whether the grid is a torus
        capacity (int): the capacity of a grid cell
        random (Random): the random number generator
        _try_random (bool): whether to get empty cell be repeatedly trying random cell

    """

    def __init__(
        self,
        dimensions: Sequence[int],
        torus: bool = False,
        capacity: float | None = None,
        random: Random | None = None,
        cell_klass: type[T] = Cell,
    ) -> None:
        super().__init__(capacity=capacity, random=random, cell_klass=cell_klass)
        self.torus = torus
        self.dimensions = dimensions
        self._try_random = True
        self._ndims = len(dimensions)
        self._validate_parameters()

        coordinates = product(*(range(dim) for dim in self.dimensions))

        self._cells = {
            coord: cell_klass(coord, capacity, random=self.random)
            for coord in coordinates
        }
        self._connect_cells()

    def _connect_cells(self) -> None:
        if self._ndims == 2:
            self._connect_cells_2d()
        else:
            self._connect_cells_nd()

    def _connect_cells_2d(self) -> None: ...

    def _connect_cells_nd(self) -> None: ...

    def _validate_parameters(self):
        if not all(isinstance(dim, int) and dim > 0 for dim in self.dimensions):
            raise ValueError("Dimensions must be a list of positive integers.")
        if not isinstance(self.torus, bool):
            raise ValueError("Torus must be a boolean.")
        if self.capacity is not None and not isinstance(self.capacity, float | int):
            raise ValueError("Capacity must be a number or None.")

    def select_random_empty_cell(self) -> T:
        # FIXME:: currently just a simple boolean to control behavior
        # FIXME:: basically if grid is close to 99% full, creating empty list can be faster
        # FIXME:: note however that the old results don't apply because in this implementation
        # FIXME:: because empties list needs to be rebuild each time
        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052 and
        # https://github.com/projectmesa/mesa/pull/1565. The cutoff value provided
        # is the break-even comparison with the time taken in the else branching point.
        if self._try_random:
            while True:
                cell = self.all_cells.select_random_cell()
                if cell.is_empty:
                    return cell
        else:
            return super().select_random_empty_cell()

    def _connect_single_cell_nd(self, cell: T, offsets: list[tuple[int, ...]]) -> None:
        coord = cell.coordinate

        for d_coord in offsets:
            n_coord = tuple(c + dc for c, dc in zip(coord, d_coord))
            if self.torus:
                n_coord = tuple(nc % d for nc, d in zip(n_coord, self.dimensions))
            if all(0 <= nc < d for nc, d in zip(n_coord, self.dimensions)):
                cell.connect(self._cells[n_coord])

    def _connect_single_cell_2d(self, cell: T, offsets: list[tuple[int, int]]) -> None:
        i, j = cell.coordinate
        height, width = self.dimensions

        for di, dj in offsets:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % height, nj % width
            if 0 <= ni < height and 0 <= nj < width:
                cell.connect(self._cells[ni, nj])


class _PropertyGrid(Grid, Generic[T]):
    """
    A private subclass of Grid that supports the addition of property layers, enabling
    the representation and manipulation of additional data layers on the grid. This class is
    intended for internal use within the Mesa framework.

    The `_PropertyGrid` extends the capabilities of a basic grid by allowing each cell
    to have multiple properties, each represented by a separate PropertyLayer.
    These properties can be used to model complex environments where each cell
    has multiple attributes or states.

    Attributes:
        properties (dict): A dictionary mapping property layer names to PropertyLayer instances.

    Methods:
        add_property_layer(property_layer): Adds a new property layer to the grid.
        remove_property_layer(property_name): Removes a property layer from the grid by its name.
        select_random_empty_cell(self): Returns an empty random cell instance from the grid.


    Note:
        This class is not intended for direct use in user models but is currently used by the OrthogonalMooreGrid and OrthogonalVonNeumannGrid.
    """

    def __init__(
        self,
        dimensions: Sequence[int],
        torus: bool = False,
        capacity: float | None = None,
        random: Random | None = None,
        cell_klass: type[T] = Cell,
        property_layers: None | PropertyLayer | list[PropertyLayer] = None,
    ) -> None:
        super().__init__(
            dimensions=dimensions,
            torus=torus,
            capacity=capacity,
            random=random,
            cell_klass=cell_klass,
        )

        self.properties = {}

        # Handle both single PropertyLayer instance and list of PropertyLayer instances
        if property_layers:
            # If a single PropertyLayer is passed, convert it to a list
            if isinstance(property_layers, PropertyLayer):
                property_layers = [property_layers]

            for layer in property_layers:
                self.add_property_layer(layer)

    def add_property_layer(self, property_layer: PropertyLayer):
        """
        Adds a new property layer to the grid.

        Args:
            property_layer (PropertyLayer): The PropertyLayer instance to be added to the grid.

        Raises:
            ValueError: If a property layer with the same name already exists in the grid.
            ValueError: If the dimensions of the property layer do not match the grid's dimensions.
        """
        if property_layer.name in self.properties:
            raise ValueError(f"Property layer {property_layer.name} already exists.")
        if (
            property_layer.width != self.dimensions[0]
            or property_layer.height != self.dimensions[1]
        ):
            raise ValueError(
                f"Property layer dimensions {property_layer.width}x{property_layer.height} do not match grid dimensions {self.dimensions[0]}x{self.dimensions[1]}."
            )
        self.properties[property_layer.name] = property_layer

    def remove_property_layer(self, property_name: str):
        """
        Removes a property layer from the grid by its name.

        Args:
            property_name (str): The name of the property layer to be removed.

        Raises:
            ValueError: If a property layer with the given name does not exist in the grid.
        """
        if property_name not in self.properties:
            raise ValueError(f"Property layer {property_name} does not exist.")
        del self.properties[property_name]


class OrthogonalMooreGrid(_PropertyGrid[T]):
    """Grid where cells are connected to their 8 neighbors.

    Example for two dimensions:
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]
    """

    def _connect_cells_2d(self) -> None:
        # fmt: off
        offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        # fmt: on
        height, width = self.dimensions

        for cell in self.all_cells:
            self._connect_single_cell_2d(cell, offsets)

    def _connect_cells_nd(self) -> None:
        offsets = list(product([-1, 0, 1], repeat=len(self.dimensions)))
        offsets.remove((0,) * len(self.dimensions))  # Remove the central cell

        for cell in self.all_cells:
            self._connect_single_cell_nd(cell, offsets)


class OrthogonalVonNeumannGrid(_PropertyGrid[T]):
    """Grid where cells are connected to their 4 neighbors.

    Example for two dimensions:
    directions = [
                (0, -1),
        (-1, 0),         ( 1, 0),
                (0,  1),
    ]
    """

    def _connect_cells_2d(self) -> None:
        # fmt: off
        offsets = [
                    (-1, 0),
            (0, -1),         (0, 1),
                    ( 1, 0),
        ]
        # fmt: on
        height, width = self.dimensions

        for cell in self.all_cells:
            self._connect_single_cell_2d(cell, offsets)

    def _connect_cells_nd(self) -> None:
        offsets = []
        dimensions = len(self.dimensions)
        for dim in range(dimensions):
            for delta in [
                -1,
                1,
            ]:  # Move one step in each direction for the current dimension
                offset = [0] * dimensions
                offset[dim] = delta
                offsets.append(tuple(offset))

        for cell in self.all_cells:
            self._connect_single_cell_nd(cell, offsets)


class HexGrid(Grid[T]):
    def _connect_cells_2d(self) -> None:
        # fmt: off
        even_offsets = [
                        (-1, -1), (-1, 0),
                    ( 0, -1),        ( 0, 1),
                        ( 1, -1), ( 1, 0),
                ]
        odd_offsets = [
                        (-1, 0), (-1, 1),
                    ( 0, -1),       ( 0, 1),
                        ( 1, 0), ( 1, 1),
                ]
        # fmt: on

        for cell in self.all_cells:
            i = cell.coordinate[0]
            offsets = even_offsets if i % 2 == 0 else odd_offsets
            self._connect_single_cell_2d(cell, offsets=offsets)

    def _connect_cells_nd(self) -> None:
        raise NotImplementedError("HexGrids are only defined for 2 dimensions")

    def _validate_parameters(self):
        super()._validate_parameters()
        if len(self.dimensions) != 2:
            raise ValueError("HexGrid must have exactly 2 dimensions.")
