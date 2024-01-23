import itertools
import random
from collections.abc import Iterable
from functools import cache, cached_property
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from mesa import Agent

Coordinate = tuple[int, int]


class Cell:
    __slots__ = ["coordinate", "_connections", "agents", "capacity", "properties"]

    def __init__(self, i: int, j: int, capacity: int | None = 1) -> None:
        self.coordinate = (i, j)
        self._connections: list[Cell] = []
        self.agents: list[Agent] = []
        self.capacity = capacity
        self.properties: dict[str, object] = {}

    def connect(self, other) -> None:
        """Connects this cell to another cell."""
        self._connections.append(other)

    def disconnect(self, other) -> None:
        """Disconnects this cell from another cell."""
        self._connections.remove(other)

    def add_agent(self, agent: Agent) -> None:
        """Adds an agent to the cell."""
        if self.capacity and len(self.agents) >= self.capacity:
            raise Exception("ERROR: Cell is full")
        if isinstance(agent.cell, Cell):
            agent.cell.remove_agent(agent)
        self.agents.append(agent)
        agent.cell = self

    def remove_agent(self, agent: Agent) -> None:
        """Removes an agent from the cell."""
        self.agents.remove(agent)
        agent.cell = None

    @property
    def is_empty(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == 0

    @property
    def is_full(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == self.capacity

    def __repr__(self):
        return f"Cell({self.coordinate}, {self.agents})"

    @cache
    def neighborhood(self, radius=1, include_center=False):
        if radius == 0:
            return {self: self.agents}
        if radius == 1:
            return CellCollection(
                {neighbor: neighbor.agents for neighbor in self._connections}
            )
        else:
            neighborhood = {}
            for neighbor in self._connections:
                neighborhood.update(neighbor.neighorhood(radius - 1, include_center))
            if not include_center:
                neighborhood.pop(self, None)
            return CellCollection(neighborhood)


class CellCollection:
    def __init__(self, cells: dict[Cell, list[Agent]] | Iterable[Cell]) -> None:
        if isinstance(cells, dict):
            self._cells = cells
        else:
            self._cells = {cell: cell.agents for cell in cells}

    def __iter__(self):
        return iter(self._cells)

    def __getitem__(self, key):
        return self._cells[key]

    @cached_property
    def __len__(self):
        return len(self._cells)

    def __repr__(self):
        return f"CellCollection({self._cells})"

    @cached_property
    def cells(self):
        return list(self._cells.keys())

    @property
    def agents(self):
        return itertools.chain.from_iterable(self._cells.values())

    def select_random_cell(self):
        return random.choice(self.cells)

    def select_random_agent(self):
        return random.choice(list(self.agents))

    def select(self, filter_func: Optional[Callable[[Cell], bool]] = None, n=0):
        if filter_func is None and n == 0:
            return self

        return CellCollection(
            {
                cell: agents
                for cell, agents in self._cells.items()
                if filter_func is None or filter_func(cell)
            }
        )


class Space:
    cells: dict[Coordinate, Cell] = {}

    def _connect_single_cell(self, cell):
        ...

    @cached_property
    def all_cells(self):
        return CellCollection({cell: cell.agents for cell in self.cells.values()})

    def __iter__(self):
        return iter(self.cells.values())

    def __getitem__(self, key):
        return self.cells[key]

    def move_agent(self, agent: Agent, pos: Coordinate) -> None:
        """Move an agent from its current position to a new position."""
        self.cells[pos].add_agent(agent)

    @property
    def empties(self) -> CellCollection:
        return self.all_cells.select(lambda cell: cell.is_empty)

    def move_to_empty(self, agent: Agent) -> None:
        while True:
            new_cell = self.all_cells.select_random_cell()
            if new_cell.is_empty:
                new_cell.add_agent(agent)
                return

        # TODO: Adjust cutoff value for performance
        for _ in range(len(self.all_cells) // 10):
            new_cell = self.all_cells.select_random_cell()
            if new_cell.is_empty:
                new_cell.add_agent(agent)
                return

        try:
            self.empties.select_random_cell().add_agent(agent)
        except IndexError as err:
            raise Exception("ERROR: No empty cell found") from err


class Grid(Space):
    def __init__(
        self, width: int, height: int, torus: bool = False, moore=True, capacity=1
    ) -> None:
        self.width = width
        self.height = height
        self.torus = torus
        self.moore = moore
        self.capacity = capacity
        self.cells = {
            (i, j): Cell(i, j, capacity) for j in range(width) for i in range(height)
        }

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        i, j = cell.coordinate

        # fmt: off
        if self.moore:
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                ( 0, -1),          ( 0, 1),
                ( 1, -1), ( 1, 0), ( 1, 1),
            ]
        else: # Von Neumann neighborhood
            directions = [
                          (-1, 0),
                ( 0, -1),          (0, 1),
                          ( 1, 0),
            ]
        # fmt: on

        for di, dj in directions:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % self.height, nj % self.width
            if 0 <= ni < self.height and 0 <= nj < self.width:
                cell.connect(self.cells[ni, nj])
