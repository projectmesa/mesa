import itertools
import random
from collections.abc import Iterable
from functools import cache, cached_property
from typing import Any, Callable, Optional

from .. import Agent, Model

Coordinate = tuple[int, int]


class CellAgent(Agent):
    """
    Base class for a model agent in Mesa.

    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): A reference to the model instance.
        self.pos: Position | None = None
    """

    def __init__(self, unique_id: int, model: Model) -> None:
        """
        Create a new agent.

        Args:
            unique_id (int): A unique identifier for this agent.
            model (Model): The model instance in which the agent exists.
        """
        super().__init__(unique_id, model)
        self.cell: Cell | None = None

    def move_to(self, cell) -> None:
        if self.cell is not None:
            self.cell.remove_agent(self)
        self.cell = cell
        cell.add_agent(self)


class Cell:
    __slots__ = [
        "coordinate",
        "_connections",
        "owner",
        "agents",
        "capacity",
        "properties",
    ]

    def __init__(self, coordinate, owner, capacity: int | None = None) -> None:
        self.coordinate = coordinate
        self._connections: list[Cell] = []  # TODO: change to CellCollection?
        self.agents: dict[
            Agent, None
        ] = {}  # TODO:: change to AgentSet or weakrefs? (neither is very performant, )
        self.capacity = capacity
        self.properties: dict[str, object] = {}
        self.owner = owner

    def connect(self, other) -> None:
        """Connects this cell to another cell."""
        self._connections.append(other)

    def disconnect(self, other) -> None:
        """Disconnects this cell from another cell."""
        self._connections.remove(other)

    def add_agent(self, agent: CellAgent) -> None:
        """Adds an agent to the cell."""
        n = len(self.agents)

        if n == 0:
            self.owner._empties.pop(self.coordinate, None)

        if self.capacity and n >= self.capacity:
            raise Exception(
                "ERROR: Cell is full"
            )  # FIXME we need MESA errors or a proper error

        self.agents[agent] = None

    def remove_agent(self, agent: CellAgent) -> None:
        """Removes an agent from the cell."""
        self.agents.pop(agent, None)
        agent.cell = None
        if len(self.agents) == 0:
            self.owner._empties[self.coordinate] = None

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
        return CellCollection(
            self._neighborhood(radius=radius, include_center=include_center)
        )

    @cache
    def _neighborhood(self, radius=1, include_center=False):
        # if radius == 0:
        #     return {self: self.agents}
        if radius < 1:
            raise ValueError("radius must be larger than one")
        if radius == 1:
            return {neighbor: neighbor.agents for neighbor in self._connections}
        else:
            neighborhood = {}
            for neighbor in self._connections:
                neighborhood.update(neighbor._neighborhood(radius - 1, include_center))
            if not include_center:
                neighborhood.pop(self, None)
            return neighborhood

    def __repr__(self):
        return f"Cell({self.coords})"


class CellCollection:
    def __init__(self, cells: dict[Cell, list[Agent]] | Iterable[Cell]) -> None:
        if isinstance(cells, dict):
            self._cells = cells
        else:
            self._cells = {cell: cell.agents for cell in cells}
        self.random = random  # FIXME

    def __iter__(self):
        return iter(self._cells)

    def __getitem__(self, key: Cell) -> Iterable[Agent]:
        return self._cells[key]

    @cached_property
    def __len__(self) -> int:
        return len(self._cells)

    def __repr__(self):
        return f"CellCollection({self._cells})"

    @cached_property
    def cells(self):
        return list(self._cells.keys())

    @property
    def agents(self) -> Iterable[Agent]:
        return itertools.chain.from_iterable(self._cells.values())

    def select_random_cell(self):
        return self.random.choice(self.cells)

    def select_random_agent(self):
        return self.random.choice(list(self.agents))

    def select(self, filter_func: Optional[Callable[[Cell], bool]] = None, n=0):
        # FIXME: n is not considered
        if filter_func is None and n == 0:
            return self

        return CellCollection(
            {
                cell: agents
                for cell, agents in self._cells.items()
                if filter_func is None or filter_func(cell)
            }
        )


class DiscreteSpace:
    # FIXME:: random should become a keyword argument
    # FIXME:: defaulting to the same rng as model.random.
    # FIXME:: all children should be also like that.

    def __init__(
        self,
        capacity: int | None = None,
    ):
        super().__init__()
        self.capacity = capacity
        self.cells: dict[Coordinate, Cell] = {}
        self.random = random  # FIXME

        self._empties = {}
        self.cutoff_empties = -1
        self.empties_initialized = False

    def _connect_single_cell(self, cell):
        ...

    def select_random_empty_cell(self) -> Cell:
        ...

    def _initialize_empties(self):
        self._empties = {
            cell.coordinate: None for cell in self.cells.values() if cell.is_empty
        }
        self.cutoff_empties = 7.953 * len(self.cells) ** 0.384
        self.empties_initialized = True

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


class Grid(DiscreteSpace):
    def __init__(
        self, width: int, height: int, torus: bool = False, capacity: int = 1
    ) -> None:
        super().__init__(capacity)
        self.torus = torus
        self.width = width
        self.height = height

    def select_random_empty_cell(self) -> Cell:
        if not self.empties_initialized:
            self._initialize_empties()

        num_empty_cells = len(self._empties)
        if num_empty_cells == 0:
            raise Exception("ERROR: No empty cells")

        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052 and
        # https://github.com/projectmesa/mesa/pull/1565. The cutoff value provided
        # is the break-even comparison with the time taken in the else branching point.
        if num_empty_cells > self.cutoff_empties:
            while True:
                cell = self.all_cells.select_random_cell()
                if cell.is_empty:
                    break
        else:
            coordinate = self.random.choice(list(self._empties))
            cell = self.cells[coordinate]

        return cell


class OrthogonalGrid(Grid):
    def __init__(
        self,
        width: int,
        height: int,
        torus: bool = False,
        moore: bool = True,
        capacity: int | None = None,
    ) -> None:
        """Orthogonal grid

        Args:
            width (int): width of the grid
            height (int): height of the grid
            torus (bool): whether the space is a torus
            moore (bool): whether the space used Moore or von Neumann neighborhood
            capacity (int): the number of agents that can simultaneously occupy a cell

        """
        super().__init__(width, height, torus, capacity)
        self.moore = moore
        self.cells = {
            (i, j): Cell((i, j), self, capacity)
            for j in range(width)
            for i in range(height)
        }

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        i, j = cell.coordinate

        # fmt: off
        if self.moore:
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                ( 0, -1),           ( 0, 1),
                ( 1, -1),  ( 1, 0), ( 1, 1),
            ]
        else:  # Von Neumann neighborhood
            directions = [
                         (-1, 0),
                (0, -1),          (0, 1),
                         ( 1, 0),
            ]
        # fmt: on

        for di, dj in directions:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % self.height, nj % self.width
            if 0 <= ni < self.height and 0 <= nj < self.width:
                cell.connect(self.cells[ni, nj])


class HexGrid(Grid):
    def __init__(
        self, width: int, height: int, torus: bool = False, capacity=1
    ) -> None:
        """Hexagonal Grid

        Args:
            width (int): width of the grid
            height (int): height of the grid
            torus (bool): whether the space is a torus
            capacity (int): the number of agents that can simultaneously occupy a cell

        """
        super().__init__(width, height, torus, capacity)
        self.cells = {
            (i, j): Cell((i, j), self, capacity)
            for j in range(width)
            for i in range(height)
        }

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        i, j = cell.coordinate

        # fmt: off
        if i % 2 == 0:
            directions = [
                   (-1, -1), (-1, 0),
                (0, -1),         (0, 1),
                   ( 1, -1),  (1, 0),
            ]
        else:
            directions = [
                   (-1, 0), (-1, 1),
                (0, -1),        (0, 1),
                   ( 1, 0),  (1, 1),
            ]
        # fmt: on

        for di, dj in directions:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % self.height, nj % self.width
            if 0 <= ni < self.height and 0 <= nj < self.width:
                cell.connect(self.cells[ni, nj])


class NetworkGrid(DiscreteSpace):
    def __init__(self, G: Any, capacity: int | None = None) -> None:
        """A Networked grid

        Args:
            G: a NetworkX Graph instance.
            capacity (int) : the capacity of the cell

        """
        super().__init__(capacity)
        self.G = G

        for node_id in self.G.nodes:
            self.cells[node_id] = Cell(node_id, self, capacity)

        for cell in self.all_cells:
            self._connect_single_cell(cell)

    def _connect_single_cell(self, cell):
        neighbors = [
            self.cells[node_id] for node_id in self.G.neighbors(cell.coordinate)
        ]
        cell.connect(neighbors)

    def select_random_empty_cell(self) -> Cell:
        if not self.empties_initialized:
            self._initialize_empties()

        return self.random.choice(self._empties)
