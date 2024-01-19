import itertools
import random
from functools import cache
from typing import Any

from mesa import Agent

Coordinates = tuple[int, int]


def create_neighborhood_getter(moore=True, include_center=False, radius=1):
    @cache
    def of(cell: Cell):
        if radius == 0:
            return {cell: cell.content}

        neighborhood = {}
        for neighbor in cell.connections:
            if (
                moore
                or neighbor.coords[0] == cell.coords[0]
                or neighbor.coords[1] == cell.coords[1]
            ):
                neighborhood[neighbor] = neighbor.content

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
    __slots__ = ["coords", "connections", "content"]

    def __init__(self, i: int, j: int) -> None:
        self.coords = (i, j)
        self.connections: list[Cell] = []
        self.content: list[Agent] = []

    def connect(self, other) -> None:
        """Connects this cell to another cell."""
        self.connections.append(other)

    def disconnect(self, other) -> None:
        """Disconnects this cell from another cell."""
        self.connections.remove(other)

    def add_agent(self, agent: Agent) -> None:
        """Adds an agent to the cell."""
        self.content.append(agent)
        agent.cell = self

    def remove_agent(self, agent: Agent) -> None:
        """Removes an agent from the cell."""
        if agent in self.content:
            self.content.remove(agent)

    def __repr__(self):
        return f"Cell({self.coords})"


class CellCollection:
    def __init__(self, cells: dict[Cell, list[Agent]]) -> None:
        self.cells = cells

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, key):
        return self.cells[key]

    def __len__(self):
        return len(self.cells)

    def __repr__(self):
        return f"CellCollection({self.cells})"

    @property
    def agents(self):
        return itertools.chain.from_iterable(self.cells.values())

    def select_random(self):
        return random.choice(list(self.cells.keys()))


class Space:
    cells: dict[Coordinates, Cell]

    def _connect_single_cell(self, cell):  # <= different for every concrete Space
        ...

    def __iter__(self):
        return iter(self.cells.values())

    def get_neighborhood(self, coords: Coordinates, neighborhood_getter: Any):
        return neighborhood_getter(self.cells[coords])

    def move_agent(self, agent: Agent, pos) -> None:
        """Move an agent from its current position to a new position."""
        if (old_cell := agent.cell) is not None:
            old_cell.remove_agent(agent)
            if self._empties_built:
                self._empties.add(old_cell.coords)

        new_cell = self.cells[pos]
        new_cell.add_agent(agent)
        if self._empties_built:
            self._empties.discard(new_cell.coords)

    @property
    def empties(self) -> CellCollection:
        if not self._empties_built:
            self.build_empties()

        return CellCollection(
            {
                self.cells[coords]: self.cells[coords].content
                for coords in sorted(self._empties)
            }
        )

    def build_empties(self) -> None:
        self._empties = set(filter(self.is_cell_empty, self.cells.keys()))
        self._empties_built = True

    def move_to_empty(self, agent: Agent) -> None:
        """Moves agent to a random empty cell, vacating agent's old cell."""
        num_empty_cells = len(self.empties)
        if num_empty_cells == 0:
            raise Exception("ERROR: No empty cells")

        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052 and
        # https://github.com/projectmesa/mesa/pull/1565. The cutoff value provided
        # is the break-even comparison with the time taken in the else branching point.
        if num_empty_cells > self.cutoff_empties:
            while True:
                new_pos = (
                    agent.random.randrange(self.width),
                    agent.random.randrange(self.height),
                )
                if self.is_cell_empty(new_pos):
                    break
        else:
            new_pos = self.empties.select_random().coords
        self.move_agent(agent, new_pos)

    def is_cell_empty(self, pos) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.cells[pos].content) == 0


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
        i, j = cell.coords
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

    def get_neighborhood(self, coords, neighborhood_getter: Any) -> CellCollection:
        return neighborhood_getter(self.cells[coords])
