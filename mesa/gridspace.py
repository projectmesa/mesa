import itertools
import random
from functools import cache, cached_property
from typing import Any, Callable, Optional

from .agent import Agent

Coordinate = tuple[int, int]


def create_neighborhood_getter(moore=True, include_center=False, radius=1):
    @cache
    def of(cell: Cell):
        if radius == 0:
            return {cell: cell.agents}

        neighborhood = {}
        for neighbor in cell._connections:
            if (
                moore
                or neighbor.coordinate[0] == cell.coordinate[0]
                or neighbor.coordinate[1] == cell.coordinate[1]
            ):
                neighborhood[neighbor] = neighbor.agents

        if radius > 1:
            for neighbor in list(neighborhood.keys()):
                neighborhood.update(
                    create_neighborhood_getter(moore, include_center, radius - 1)(
                        neighbor
                    )
                )

        if not include_center:
            neighborhood.pop(cell, None)

        return CellCollection(neighborhood)

    return of


class Cell:
    __slots__ = ["coordinate", "_connections", "agents", "capacity", "properties"]

    def __init__(self, i: int, j: int, capacity: int = 1) -> None:
        self.coordinate = (i, j)
        self._connections: list[Cell] = []
        self.agents: list[Agent] = []
        self.capacity = capacity
        self.properties: dict[str, Any] = {}

    def connect(self, other) -> None:
        """Connects this cell to another cell."""
        self._connections.append(other)

    def disconnect(self, other) -> None:
        """Disconnects this cell from another cell."""
        self._connections.remove(other)

    def add_agent(self, agent: Agent) -> None:
        """Adds an agent to the cell."""
        if len(self.agents) >= self.capacity:
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


class CellCollection:
    def __init__(self, cells: dict[Cell, list[Agent]]) -> None:
        self._cells = cells

    def __iter__(self):
        return iter(self._cells)

    def __getitem__(self, key):
        return self._cells[key]

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

    def move_agent(self, agent: Agent, pos) -> None:
        """Move an agent from its current position to a new position."""
        if (old_cell := agent.cell) is not None:
            old_cell.remove_agent(agent)

        new_cell = self.cells[pos]
        new_cell.add_agent(agent)

    @property
    def empties(self) -> CellCollection:
        return self.all_cells.select(lambda cell: cell.is_empty)

    def move_to_empty(self, agent: Agent) -> None:
        # TODO: Add Heuristic for almost full grids
        while True:
            new_cell = self.all_cells.select_random_cell()
            if new_cell.is_empty:
                new_cell.add_agent(agent)
                return


class Grid(Space):
    def __init__(self, width: int, height: int, torus: bool = False) -> None:
        self.width = width
        self.height = height
        self.torus = torus
        self.cells = {(i, j): Cell(i, j) for j in range(width) for i in range(height)}

        self._empties_built = False
        self.cutoff_empties = 7.953 * len(self.cells) ** 0.384

        for cell in self.cells.values():
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        i, j = cell.coordinate
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        for di, dj in directions:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % self.height, nj % self.width
            if 0 <= ni < self.height and 0 <= nj < self.width:
                cell.connect(self.cells[ni, nj])
