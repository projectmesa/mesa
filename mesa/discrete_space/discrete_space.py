"""Abstract Base class for building cell-based spatial environments.

DiscreteSpace provides the core functionality needed by all cell-based spaces:
- Cell creation and tracking
- Agent-cell relationship management
- Property Layer support
- Random selection capabilities
- Capacity management

This serves as the foundation for specific space implementations like grids
and networks, ensuring consistent behavior and shared functionality across
different space types. All concrete cell space implementations (grids, networks, etc.)
inherit from this class.
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from functools import cached_property
from random import Random
from typing import TYPE_CHECKING, TypeVar

import numpy as np

from mesa.agent import AgentSet
from mesa.discrete_space.cell import Cell
from mesa.discrete_space.cell_collection import CellCollection
from mesa.exceptions import CellMissingException
from mesa.experimental.frames.frame import Frame

if TYPE_CHECKING:
    from mesa.agent import Agent

T = TypeVar("T", bound=Cell)


class DiscreteSpace[T: Cell](ABC):
    """Base class for all discrete spaces.

    Attributes:
        capacity (int): The capacity of the cells in the discrete space
        all_cells (CellCollection): The cells composing the discrete space
        random (Random): The random number generator
        cell_klass (Type) : the type of cell class
        empties (CellCollection) : collection of all cells that are empty
        property_layers (dict[str, np.ndarray]): property_layer of the discrete space

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
        frame: Frame | None = None,
    ):
        """Instantiate a DiscreteSpace.

        Args:
            capacity: capacity of cells
            cell_klass: base class for all cells
            random: random number generator
            frame: the frame the space indexes. Spaces that share a frame keep the
                agents they have in common at the same location. By default, the
                space gets a frame of its own.
        """
        super().__init__()
        self.frame = Frame() if frame is None else frame
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

    @abstractmethod
    def _connect_cells(self) -> None: ...

    @abstractmethod
    def find_nearest_cell(self, position: np.ndarray) -> T:
        """Find the cell at or nearest to the given position."""

    def _resolve(self, point: np.ndarray) -> T:
        """Return the cell an agent at the given frame point occupies."""
        return self.find_nearest_cell(point)

    def _owns(self, cell: Cell) -> bool:
        return self._cells.get(cell.coordinate) is cell

    def add(self, agent: Agent, cell: T | None = None) -> None:
        """Add an agent to the space.

        The agent occupies a cell, counts toward its capacity and shows up in
        neighborhood queries. If the agent is in other spaces of the same frame,
        all of them keep agreeing on its location.

        Args:
            agent: the agent to add
            cell: the cell to place the agent in. If omitted, the agent enters at
                its current location in the frame.

        Raises:
            CellFullException: if the cell has no capacity left. The agent then
                stays where it was.
        """
        record = self.frame._record(agent)
        if (
            cell is not None
            and record.is_empty
            and getattr(agent, "_mesa_cell", self) is None
        ):
            # A cell agent entering its first space stays on the single-space path
            agent.cell = cell
            return
        self.frame._enter_discrete(record, self, cell)

    def remove(self, agent: Agent) -> None:
        """Remove an agent from the space, keeping it in the model and in other spaces."""
        record = self.frame._lookup(agent)
        if record is not None and self in record.cells:
            self.frame._leave(record, self)
        elif self.cell_of(agent) is not None:
            agent.cell = None
        else:
            raise ValueError(
                f"Agent {agent.unique_id} is not in this {type(self).__name__}."
            )

    def move(self, agent: Agent, cell: T) -> None:
        """Move an agent to a cell of this space.

        The agent's location in the frame becomes the position of the cell, and
        the other spaces of the frame the agent is in update accordingly. If any
        of them rejects the move, the agent stays where it was.
        """
        record = self.frame._lookup(agent)
        if record is not None and self in record.cells:
            self.frame._write(record, self, cell)
        elif self.cell_of(agent) is not None:
            agent.cell = cell
        else:
            raise ValueError(
                f"Agent {agent.unique_id} is not in this {type(self).__name__}; add it first."
            )

    def cell_of(self, agent: Agent) -> T | None:
        """Return the cell the agent occupies in this space, or None."""
        locations = agent._mesa_locations
        if locations is not None:
            record = locations.get(self.frame.key)
            if record is not None and self in record.cells:
                return record.cells[self]
        cell = getattr(agent, "_mesa_cell", None)
        if cell is not None and self._owns(cell):
            return cell
        return None

    def add_cell(self, cell: T):
        """Add a cell to the space.

        Args:
            cell: cell to add

        Note:
            Discrete spaces rely on caching neighborhood relations for speedups. Adding or removing cells and
            connections at runtime is possible. However, only the caches of cells directly affected will be cleared. So
            if you rely on getting neighborhoods of cells with a radius higher than 1, these might not be cleared
            correctly if you are adding or removing cells and connections at runtime.

        Warning:
            Coordinate Collision: If a cell already exists at the specified
            coordinates (e.g., cell1), it will be overwritten silently by the
            new cell (cell2).

            Ensure the target coordinates are vacant before calling this method.
        """
        self.__dict__.pop("all_cells", None)
        self._cells[cell.coordinate] = cell

    def remove_cell(self, cell: T):
        """Remove a cell from the space.

        Note:
            Discrete spaces rely on caching neighborhood relations for speedups. Adding or removing cells and
            connections at runtime is possible. However, only the caches of cells directly affected will be cleared. So
            if you rely on getting neighborhoods of cells with a radius higher than 1, these might not be cleared
            correctly if you are adding or removing cells and connections at runtime.


        """
        neighbors = cell.neighborhood

        try:
            self._cells.pop(cell.coordinate)
        except KeyError as e:
            raise CellMissingException(cell.coordinate) from e

        self.__dict__.pop("all_cells", None)

        # iterate over all neighbors
        for neighbor in neighbors.cells:
            neighbor.disconnect(cell)
            cell.disconnect(neighbor)

    def add_connection(self, cell1: T, cell2: T):
        """Add a connection between the two cells.

        Note:
            Discrete spaces rely on caching neighborhood relations for speedups. Adding or removing cells and
            connections at runtime is possible. However, only the caches of cells directly affected will be cleared. So
            if you rely on getting neighborhoods of cells with a radius higher than 1, these might not be cleared
            correctly if you are adding or removing cells and connections at runtime.

        """
        cell1.connect(cell2)
        cell2.connect(cell1)

    def remove_connection(self, cell1: T, cell2: T):
        """Remove a connection between the two cells.

        Note:
            Discrete spaces rely on caching neighborhood relations for speedups. Adding or removing cells and
            connections at runtime is possible. However, only the caches of cells directly affected will be cleared. So
            if you rely on getting neighborhoods of cells with a radius higher than 1, these might not be cleared
            correctly if you are adding or removing cells and connections at runtime.

        """
        cell1.disconnect(cell2)
        cell2.disconnect(cell1)

    @cached_property
    def all_cells(self):
        """Return all cells in space."""
        return CellCollection(
            {cell: cell._agents for cell in self._cells.values()}, random=self.random
        )

    def __iter__(self):  # noqa
        return iter(self._cells.values())

    def __getitem__(self, key: tuple[int, ...]) -> T:  # noqa: D105
        try:
            return self._cells[key]
        except KeyError as e:
            raise CellMissingException(key) from e

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

        if self._cells:
            self.cell_klass = type(next(iter(self._cells.values())))

        for cell in self._cells.values():
            cell.connections = {
                key: self._cells[coord] for key, coord in cell.connections.items()
            }
