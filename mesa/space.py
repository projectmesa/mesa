"""
Mesa Space Module
=================

Objects used to add a spatial component to a model.

Grid: base grid, which creates a rectangular grid.
SingleGrid: extension to Grid which strictly enforces one agent per cell.
MultiGrid: extension to Grid where each cell can contain a set of agents.
HexGrid: extension to Grid to handle hexagonal neighbors.
ContinuousSpace: a two-dimensional space where each agent has an arbitrary
                 position of `float`'s.
NetworkGrid: a network where each node contains zero or more agents.
"""
# Instruction for PyLint to suppress variable name errors, since we have a
# good reason to use one-character variable names for x and y.
# pylint: disable=invalid-name

# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import itertools
import collections
import math
from warnings import warn

import numpy as np

from typing import (
    Any,
    Callable,
    List,
    Iterable,
    Iterator,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

# For Mypy
from .agent import Agent
from numbers import Real
import numpy.typing as npt

Coordinate = Tuple[int, int]
# used in ContinuousSpace
FloatCoordinate = Union[Tuple[float, float], npt.NDArray[float]]
NetworkCoordinate = int

Position = Union[Coordinate, FloatCoordinate, NetworkCoordinate]

GridContent = Union[Agent, None]
MultiGridContent = List[Agent]

F = TypeVar("F", bound=Callable[..., Any])


def accept_tuple_argument(wrapped_function: F) -> F:
    """Decorator to allow grid methods that take a list of (x, y) coord tuples
    to also handle a single position, by automatically wrapping tuple in
    single-item list rather than forcing user to do it."""

    def wrapper(grid_instance, positions) -> Any:
        if isinstance(positions, tuple) and len(positions) == 2:
            return wrapped_function(grid_instance, [positions])
        else:
            return wrapped_function(grid_instance, positions)

    return cast(F, wrapper)


def is_integer(x: Real) -> bool:
    # Check if x is either a CPython integer or Numpy integer.
    return isinstance(x, (int, np.integer))


class Grid:
    """Base class for a rectangular grid.

    Grid cells are indexed by [x][y], where [0][0] is assumed to be the
    bottom-left and [width-1][height-1] is the top-right. If a grid is
    toroidal, the top and bottom, and left and right, edges wrap to each other

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.
        grid: Internal list-of-lists which holds the grid cells themselves.
    """

    def __init__(self, width: int, height: int, torus: bool) -> None:
        """Create a new grid.

        Args:
            width, height: The width and height of the grid
            torus: Boolean whether the grid wraps or not.
        """
        self.height = height
        self.width = width
        self.torus = torus
        self.num_cells = height * width

        self.grid: list[list[GridContent]]
        self.grid = [
            [self.default_val() for _ in range(self.height)] for _ in range(self.width)
        ]

        # Add all cells to the empties list.
        self.empties = set(itertools.product(range(self.width), range(self.height)))

        # Neighborhood Cache
        self._neighborhood_cache: dict[Any, list[Coordinate]] = dict()

    @staticmethod
    def default_val() -> None:
        """Default value for new cell elements."""
        return None

    @overload
    def __getitem__(self, index: int) -> list[GridContent]:
        ...

    @overload
    def __getitem__(
        self, index: tuple[int | slice, int | slice]
    ) -> GridContent | list[GridContent]:
        ...

    @overload
    def __getitem__(self, index: Sequence[Coordinate]) -> list[GridContent]:
        ...

    def __getitem__(
        self,
        index: int | Sequence[Coordinate] | tuple[int | slice, int | slice],
    ) -> GridContent | list[GridContent]:
        """Access contents from the grid."""

        if isinstance(index, int):
            # grid[x]
            return self.grid[index]
        elif isinstance(index[0], tuple):
            # grid[(x1, y1), (x2, y2), ...]
            index = cast(Sequence[Coordinate], index)
            return [self.grid[x][y] for x, y in map(self.torus_adj, index)]

        x, y = index
        x_int, y_int = is_integer(x), is_integer(y)

        if x_int and y_int:
            # grid[x, y]
            index = cast(Coordinate, index)
            x, y = self.torus_adj(index)
            return self.grid[x][y]
        elif x_int:
            # grid[x, :]
            x, _ = self.torus_adj((x, 0))
            y = cast(slice, y)
            return self.grid[x][y]
        elif y_int:
            # grid[:, y]
            _, y = self.torus_adj((0, y))
            x = cast(slice, x)
            return [rows[y] for rows in self.grid[x]]
        else:
            # grid[:, :]
            x, y = (cast(slice, x), cast(slice, y))
            return [cell for rows in self.grid[x] for cell in rows[y]]

    def __iter__(self) -> Iterator[GridContent]:
        """Create an iterator that chains the rows of the grid together
        as if it is one list:"""
        return itertools.chain(*self.grid)

    def coord_iter(self) -> Iterator[tuple[GridContent, int, int]]:
        """An iterator that returns coordinates as well as cell contents."""
        for row in range(self.width):
            for col in range(self.height):
                yield self.grid[row][col], row, col  # agent, x, y

    def neighbor_iter(self, pos: Coordinate, moore: bool = True) -> Iterator[Agent]:
        """Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
            moore: Boolean for whether to use Moore neighborhood (including
                   diagonals) or Von Neumann (only up/down/left/right).
        """

        warn(
            "`neighbor_iter` is deprecated in favor of `iter_neighbors` "
            "and will be removed in the subsequent version."
        )
        return self.iter_neighbors(pos, moore)

    def iter_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[Coordinate]:
        """Return an iterator over cell coordinates that are in the
        neighborhood of a certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                        (including diagonals)
                   If False, return Von Neumann neighborhood
                        (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            An iterator of coordinate tuples representing the neighborhood. For
            example with radius 1, it will return list with number of elements
            equals at most 9 (8) if Moore, 5 (4) if Von Neumann (if not
            including the center).
        """
        yield from self.get_neighborhood(pos, moore, include_center, radius)

    def get_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> list[Coordinate]:
        """Return a list of cells that are in the neighborhood of a
        certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                   (including diagonals)
                   If False, return Von Neumann neighborhood
                   (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the neighborhood;
            With radius 1, at most 9 if Moore, 5 if Von Neumann (8 and 4
            if not including the center).
        """
        cache_key = (pos, moore, include_center, radius)
        neighborhood = self._neighborhood_cache.get(cache_key, None)

        if neighborhood is not None:
            return neighborhood

        # We use a list instead of a dict for the neighborhood because it would
        # be easier to port the code to Cython or Numba (for performance
        # purpose), with minimal changes. To better understand how the
        # algorithm was conceived, look at
        # https://github.com/projectmesa/mesa/pull/1476#issuecomment-1306220403
        # and the discussion in that PR in general.
        neighborhood = []

        x, y = pos
        if self.torus:
            x_max_radius, y_max_radius = self.width // 2, self.height // 2
            x_radius, y_radius = min(radius, x_max_radius), min(radius, y_max_radius)

            # For each dimension, in the edge case where the radius is as big as
            # possible and the dimension is even, we need to shrink by one the range
            # of values, to avoid duplicates in neighborhood. For example, if
            # the width is 4, while x, x_radius, and x_max_radius are 2, then
            # (x + dx) has a value from 0 to 4 (inclusive), but this means that
            # the 0 position is repeated since 0 % 4 and 4 % 4 are both 0.
            xdim_even, ydim_even = (self.width + 1) % 2, (self.height + 1) % 2
            kx = int(x_radius == x_max_radius and xdim_even)
            ky = int(y_radius == y_max_radius and ydim_even)

            for dx in range(-x_radius, x_radius + 1 - kx):
                for dy in range(-y_radius, y_radius + 1 - ky):

                    if not moore and abs(dx) + abs(dy) > radius:
                        continue

                    nx, ny = (x + dx) % self.width, (y + dy) % self.height
                    neighborhood.append((nx, ny))
        else:
            x_range = range(max(0, x - radius), min(self.width, x + radius + 1))
            y_range = range(max(0, y - radius), min(self.height, y + radius + 1))

            for nx in x_range:
                for ny in y_range:

                    if not moore and abs(nx - x) + abs(ny - y) > radius:
                        continue

                    neighborhood.append((nx, ny))

        if not include_center and neighborhood:
            neighborhood.remove(pos)

        self._neighborhood_cache[cache_key] = neighborhood

        return neighborhood

    def iter_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[Agent]:
        """Return an iterator over neighbors to a certain point.

        Args:
            pos: Coordinates for the neighborhood to get.
            moore: If True, return Moore neighborhood
                    (including diagonals)
                   If False, return Von Neumann neighborhood
                     (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            An iterator of non-None objects in the given neighborhood;
            at most 9 if Moore, 5 if Von-Neumann
            (8 and 4 if not including the center).
        """
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> list[Agent]:
        """Return a list of neighbors to a certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                    (including diagonals)
                   If False, return Von Neumann neighborhood
                     (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of non-None objects in the given neighborhood;
            at most 9 if Moore, 5 if Von-Neumann
            (8 and 4 if not including the center).
        """
        return list(self.iter_neighbors(pos, moore, include_center, radius))

    def torus_adj(self, pos: Coordinate) -> Coordinate:
        """Convert coordinate, handling torus looping."""
        if not self.out_of_bounds(pos):
            return pos
        elif not self.torus:
            raise Exception("Point out of bounds, and space non-toroidal.")
        else:
            return pos[0] % self.width, pos[1] % self.height

    def out_of_bounds(self, pos: Coordinate) -> bool:
        """Determines whether position is off the grid, returns the out of
        bounds coordinate."""
        x, y = pos
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    @accept_tuple_argument
    def iter_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> Iterator[Agent]:
        """Returns an iterator of the contents of the cells
        identified in cell_list.

        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            An iterator of the contents of the cells identified in cell_list
        """
        # iter_cell_list_contents returns only non-empty contents.
        return (self.grid[x][y] for x, y in cell_list if self.grid[x][y])

    @accept_tuple_argument
    def get_cell_list_contents(self, cell_list: Iterable[Coordinate]) -> list[Agent]:
        """Returns a list of the contents of the cells
        identified in cell_list.
        Note: this method returns a list of `Agent`'s; `None` contents are excluded.

        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A list of the contents of the cells identified in cell_list
        """
        return list(self.iter_cell_list_contents(cell_list))

    def move_agent(self, agent: Agent, pos: Coordinate) -> None:
        """Move an agent from its current position to a new position.

        Args:
            agent: Agent object to move. Assumed to have its current location
                   stored in a 'pos' tuple.
            pos: Tuple of new position to move the agent to.
        """
        pos = self.torus_adj(pos)
        self.remove_agent(agent)
        self.place_agent(agent, pos)

    def place_agent(self, agent: Agent, pos: Coordinate) -> None:
        """Place the agent at the specified location, and set its pos variable."""
        x, y = pos
        self.grid[x][y] = agent
        self.empties.discard(pos)
        agent.pos = pos

    def remove_agent(self, agent: Agent) -> None:
        """Remove the agent from the grid and set its pos attribute to None."""
        if (pos := agent.pos) is None:
            return
        x, y = pos
        self.grid[x][y] = self.default_val()
        self.empties.add(pos)
        agent.pos = None

    def swap_pos(self, agent_a: Agent, agent_b: Agent) -> None:
        """Swap agents positions"""
        agents_no_pos = []
        if (pos_a := agent_a.pos) is None:
            agents_no_pos.append(agent_a)
        if (pos_b := agent_b.pos) is None:
            agents_no_pos.append(agent_b)
        if agents_no_pos:
            agents_no_pos = [f"<Agent id: {a.unique_id}>" for a in agents_no_pos]
            raise Exception(f"{', '.join(agents_no_pos)} - not on the grid")

        if pos_a == pos_b:
            return

        self.remove_agent(agent_a)
        self.remove_agent(agent_b)

        self.place_agent(agent_a, pos_b)
        self.place_agent(agent_b, pos_a)

    def is_cell_empty(self, pos: Coordinate) -> bool:
        """Returns a bool of the contents of a cell."""
        x, y = pos
        return self.grid[x][y] == self.default_val()

    def move_to_empty(
        self, agent: Agent, cutoff: float = 0.998, num_agents: int | None = None
    ) -> None:
        """Moves agent to a random empty cell, vacating agent's old cell."""
        if num_agents is not None:
            warn(
                (
                    "`num_agents` is being deprecated since it's no longer used "
                    "inside `move_to_empty`. It shouldn't be passed as a parameter."
                ),
                DeprecationWarning,
            )
        num_empty_cells = len(self.empties)
        if num_empty_cells == 0:
            raise Exception("ERROR: No empty cells")

        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052. The default cutoff value
        # provided is the break-even comparison with the time taken in the else
        # branching point.
        if 1 - num_empty_cells / self.num_cells < cutoff:
            while True:
                new_pos = (
                    agent.random.randrange(self.width),
                    agent.random.randrange(self.height),
                )
                if self.is_cell_empty(new_pos):
                    break
        else:
            new_pos = agent.random.choice(sorted(self.empties))
        self.remove_agent(agent)
        self.place_agent(agent, new_pos)

    def find_empty(self) -> Coordinate | None:
        """Pick a random empty cell."""
        import random

        warn(
            (
                "`find_empty` is being phased out since it uses the global "
                "`random` instead of the model-level random-number generator. "
                "Consider replacing it with having a model or agent object "
                "explicitly pick one of the grid's list of empty cells."
            ),
            DeprecationWarning,
        )

        if self.exists_empty_cells():
            pos = random.choice(sorted(self.empties))
            return pos
        else:
            return None

    def exists_empty_cells(self) -> bool:
        """Return True if any cells empty else False."""
        return len(self.empties) > 0


class SingleGrid(Grid):
    """Grid where each cell contains exactly at most one object."""

    def position_agent(
        self, agent: Agent, x: int | str = "random", y: int | str = "random"
    ) -> None:
        """Position an agent on the grid.
        This is used when first placing agents! Setting either x or y to "random"
        gives the same behavior as 'move_to_empty()' to get a random position.
        If x or y are positive, they are used.
        Use 'swap_pos()' to swap agents positions.
        """
        warn(
            (
                "`position_agent` is being deprecated; use instead "
                "`place_agent` to place an agent at a specified "
                "location or `move_to_empty` to place an agent "
                "at a random empty cell."
            ),
            DeprecationWarning,
        )

        if not (isinstance(x, int) or x == "random"):
            raise Exception(
                "x must be an integer or a string 'random'."
                f" Actual type: {type(x)}. Actual value: {x}."
            )
        if not (isinstance(y, int) or y == "random"):
            raise Exception(
                "y must be an integer or a string 'random'."
                f" Actual type: {type(y)}. Actual value: {y}."
            )

        if x == "random" or y == "random":
            if len(self.empties) == 0:
                raise Exception("ERROR: Grid full")
            self.move_to_empty(agent)
        else:
            coords = (x, y)
            self.place_agent(agent, coords)

    def place_agent(self, agent: Agent, pos: Coordinate) -> None:
        if self.is_cell_empty(pos):
            super().place_agent(agent, pos)
        else:
            raise Exception("Cell not empty")


class MultiGrid(Grid):
    """Grid where each cell can contain more than one object.

    Grid cells are indexed by [x][y], where [0][0] is assumed to be at
    bottom-left and [width-1][height-1] is the top-right. If a grid is
    toroidal, the top and bottom, and left and right, edges wrap to each other.

    Each grid cell holds a set object.

    Properties:
        width, height: The grid's width and height.

        torus: Boolean which determines whether to treat the grid as a torus.

        grid: Internal list-of-lists which holds the grid cells themselves.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
    """

    grid: list[list[MultiGridContent]]

    @staticmethod
    def default_val() -> MultiGridContent:
        """Default value for new cell elements."""
        return []

    def place_agent(self, agent: Agent, pos: Coordinate) -> None:
        """Place the agent at the specified location, and set its pos variable."""
        x, y = pos
        if agent.pos is None or agent not in self.grid[x][y]:
            self.grid[x][y].append(agent)
            agent.pos = pos
            self.empties.discard(pos)

    def remove_agent(self, agent: Agent) -> None:
        """Remove the agent from the given location and set its pos attribute to None."""
        pos = agent.pos
        x, y = pos
        self.grid[x][y].remove(agent)
        if self.is_cell_empty(pos):
            self.empties.add(pos)
        agent.pos = None

    @accept_tuple_argument
    def iter_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> Iterator[MultiGridContent]:
        """Returns an iterator of the contents of the
        cells identified in cell_list.

        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A iterator of the contents of the cells identified in cell_list
        """
        return itertools.chain.from_iterable(
            self[x][y] for x, y in cell_list if not self.is_cell_empty((x, y))
        )


class HexGrid(Grid):
    """Hexagonal Grid: Extends Grid to handle hexagonal neighbors.

    Functions according to odd-q rules.
    See http://www.redblobgames.com/grids/hexagons/#coordinates for more.

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
        get_neighborhood: Returns the cells surrounding a given cell.
        iter_neighbors: Iterates over position neighbors.
        iter_neighborhood: Returns an iterator over cell coordinates that are
            in the neighborhood of a certain point.
    """

    def torus_adj_2d(self, pos: Coordinate) -> Coordinate:
        return pos[0] % self.width, pos[1] % self.height

    def get_neighborhood(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> list[Coordinate]:
        """Return a list of coordinates that are in the
        neighborhood of a certain point. To calculate the neighborhood
        for a HexGrid the parity of the x coordinate of the point is
        important, the neighborhood can be sketched as:

            Always: (0,-), (0,+)
            When x is even: (-,+), (-,0), (+,+), (+,0)
            When x is odd:  (-,0), (-,-), (+,0), (+,-)

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the neighborhood. For
            example with radius 1, it will return list with number of elements
            equals at most 9 (8) if Moore, 5 (4) if Von Neumann (if not
            including the center).
        """
        cache_key = (pos, include_center, radius)
        neighborhood = self._neighborhood_cache.get(cache_key, None)

        if neighborhood is not None:
            return neighborhood

        queue = collections.deque()
        queue.append(pos)
        coordinates = set()

        while radius > 0:

            level_size = len(queue)
            radius -= 1

            for i in range(level_size):

                x, y = queue.pop()

                if x % 2 == 0:
                    adjacent = [
                        (x, y - 1),
                        (x, y + 1),
                        (x - 1, y + 1),
                        (x - 1, y),
                        (x + 1, y + 1),
                        (x + 1, y),
                    ]
                else:
                    adjacent = [
                        (x, y - 1),
                        (x, y + 1),
                        (x - 1, y),
                        (x - 1, y - 1),
                        (x + 1, y),
                        (x + 1, y - 1),
                    ]

                if self.torus:
                    adjacent = [
                        coord
                        for coord in map(self.torus_adj_2d, adjacent)
                        if coord not in coordinates
                    ]
                else:
                    adjacent = [
                        coord
                        for coord in adjacent
                        if not self.out_of_bounds(coord) and coord not in coordinates
                    ]

                coordinates.update(adjacent)

                if radius > 0:
                    queue.extendleft(adjacent)

        if include_center:
            coordinates.add(pos)
        else:
            coordinates.discard(pos)

        neighborhood = sorted(coordinates)
        self._neighborhood_cache[cache_key] = neighborhood

        return neighborhood

    def neighbor_iter(self, pos: Coordinate) -> Iterator[Agent]:
        """Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
        """

        warn(
            "`neighbor_iter` is deprecated in favor of `iter_neighbors` "
            "and will be removed in the subsequent version."
        )
        return self.iter_neighbors(pos)

    def iter_neighborhood(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> Iterator[Coordinate]:
        """Return an iterator over cell coordinates that are in the
        neighborhood of a certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            An iterator of coordinate tuples representing the neighborhood.
        """
        yield from self.get_neighborhood(pos, include_center, radius)

    def iter_neighbors(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> Iterator[Agent]:
        """Return an iterator over neighbors to a certain point.

        Args:
            pos: Coordinates for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            An iterator of non-None objects in the given neighborhood
        """
        neighborhood = self.get_neighborhood(pos, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> list[Agent]:
        """Return a list of neighbors to a certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of non-None objects in the given neighborhood
        """
        return list(self.iter_neighbors(pos, include_center, radius))


class ContinuousSpace:
    """Continuous space where each agent can have an arbitrary position.

    Assumes that all agents have a pos property storing their position as
    an (x, y) tuple.

    This class uses a numpy array internally to store agents in order to speed
    up neighborhood lookups. This array is calculated on the first neighborhood
    lookup, and is updated if agents are added or removed.
    """

    def __init__(
        self,
        x_max: float,
        y_max: float,
        torus: bool,
        x_min: float = 0,
        y_min: float = 0,
    ) -> None:
        """Create a new continuous space.

        Args:
            x_max, y_max: Maximum x and y coordinates for the space.
            torus: Boolean for whether the edges loop around.
            x_min, y_min: (default 0) If provided, set the minimum x and y
                          coordinates for the space. Below them, values loop to
                          the other edge (if torus=True) or raise an exception.
        """
        self.x_min = x_min
        self.x_max = x_max
        self.width = x_max - x_min
        self.y_min = y_min
        self.y_max = y_max
        self.height = y_max - y_min
        self.center = np.array(((x_max + x_min) / 2, (y_max + y_min) / 2))
        self.size = np.array((self.width, self.height))
        self.torus = torus

        self._agent_points: npt.NDArray[FloatCoordinate] | None = None
        self._index_to_agent: dict[int, Agent] = {}
        self._agent_to_index: dict[Agent, int | None] = {}

    def _build_agent_cache(self):
        """Cache agents positions to speed up neighbors calculations."""
        self._index_to_agent = {}
        for idx, agent in enumerate(self._agent_to_index):
            self._agent_to_index[agent] = idx
            self._index_to_agent[idx] = agent
        # Since dicts are ordered by insertion, we can iterate through agents keys
        self._agent_points = np.array([agent.pos for agent in self._agent_to_index])

    def _invalidate_agent_cache(self):
        """Clear cached data of agents and positions in the space."""
        self._agent_points = None
        self._index_to_agent = {}

    def place_agent(self, agent: Agent, pos: FloatCoordinate) -> None:
        """Place a new agent in the space.

        Args:
            agent: Agent object to place.
            pos: Coordinate tuple for where to place the agent.
        """
        self._invalidate_agent_cache()
        self._agent_to_index[agent] = None
        pos = self.torus_adj(pos)
        agent.pos = pos

    def move_agent(self, agent: Agent, pos: FloatCoordinate) -> None:
        """Move an agent from its current position to a new position.

        Args:
            agent: The agent object to move.
            pos: Coordinate tuple to move the agent to.
        """
        pos = self.torus_adj(pos)
        agent.pos = pos

        if self._agent_points is not None:
            # instead of invalidating the full cache,
            # apply the move to the cached values
            idx = self._agent_to_index[agent]
            self._agent_points[idx] = pos

    def remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the space.

        Args:
            agent: The agent object to remove
        """
        if agent not in self._agent_to_index:
            raise Exception("Agent does not exist in the space")
        del self._agent_to_index[agent]

        self._invalidate_agent_cache()
        agent.pos = None

    def get_neighbors(
        self, pos: FloatCoordinate, radius: float, include_center: bool = True
    ) -> list[Agent]:
        """Get all agents within a certain radius.

        Args:
            pos: (x,y) coordinate tuple to center the search at.
            radius: Get all the objects within this distance of the center.
            include_center: If True, include an object at the *exact* provided
                            coordinates. i.e. if you are searching for the
                            neighbors of a given agent, True will include that
                            agent in the results.
        """
        if self._agent_points is None:
            self._build_agent_cache()

        deltas = np.abs(self._agent_points - np.array(pos))
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2

        (idxs,) = np.where(dists <= radius**2)
        neighbors = [
            self._index_to_agent[x] for x in idxs if include_center or dists[x] > 0
        ]
        return neighbors

    def get_heading(
        self, pos_1: FloatCoordinate, pos_2: FloatCoordinate
    ) -> FloatCoordinate:
        """Get the heading vector between two points, accounting for toroidal space.
        It is possible to calculate the heading angle by applying the atan2 function to the
        result.

        Args:
            pos_1, pos_2: Coordinate tuples for both points.
        """
        one = np.array(pos_1)
        two = np.array(pos_2)
        if self.torus:
            one = (one - self.center) % self.size
            two = (two - self.center) % self.size
        heading = two - one
        if isinstance(pos_1, tuple):
            heading = tuple(heading)
        return heading

    def get_distance(self, pos_1: FloatCoordinate, pos_2: FloatCoordinate) -> float:
        """Get the distance between two point, accounting for toroidal space.

        Args:
            pos_1, pos_2: Coordinate tuples for both points.
        """
        x1, y1 = pos_1
        x2, y2 = pos_2

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        if self.torus:
            dx = min(dx, self.width - dx)
            dy = min(dy, self.height - dy)
        return math.sqrt(dx * dx + dy * dy)

    def torus_adj(self, pos: FloatCoordinate) -> FloatCoordinate:
        """Adjust coordinates to handle torus looping.

        If the coordinate is out-of-bounds and the space is toroidal, return
        the corresponding point within the space. If the space is not toroidal,
        raise an exception.

        Args:
            pos: Coordinate tuple to convert.
        """
        if not self.out_of_bounds(pos):
            return pos
        elif not self.torus:
            raise Exception("Point out of bounds, and space non-toroidal.")
        else:
            x = self.x_min + ((pos[0] - self.x_min) % self.width)
            y = self.y_min + ((pos[1] - self.y_min) % self.height)
            if isinstance(pos, tuple):
                return (x, y)
            else:
                return np.array((x, y))

    def out_of_bounds(self, pos: FloatCoordinate) -> bool:
        """Check if a point is out of bounds."""
        x, y = pos
        return x < self.x_min or x >= self.x_max or y < self.y_min or y >= self.y_max


class NetworkGrid:
    """Network Grid where each node contains zero or more agents."""

    def __init__(self, G: Any) -> None:
        """Create a new network.

        Args:
            G: a NetworkX graph instance.
        """
        self.G = G
        for node_id in self.G.nodes:
            G.nodes[node_id]["agent"] = self.default_val()

    @staticmethod
    def default_val() -> list:
        """Default value for a new node."""
        return []

    def place_agent(self, agent: Agent, node_id: int) -> None:
        """Place an agent in a node."""
        self.G.nodes[node_id]["agent"].append(agent)
        agent.pos = node_id

    def get_neighbors(self, node_id: int, include_center: bool = False) -> list[int]:
        """Get all adjacent nodes"""
        neighbors = list(self.G.neighbors(node_id))
        if include_center:
            neighbors.append(node_id)
        return neighbors

    def move_agent(self, agent: Agent, node_id: int) -> None:
        """Move an agent from its current node to a new node."""
        self.remove_agent(agent)
        self.place_agent(agent, node_id)

    def remove_agent(self, agent: Agent) -> None:
        """Remove the agent from the network and set its pos attribute to None."""
        node_id = agent.pos
        self.G.nodes[node_id]["agent"].remove(agent)
        agent.pos = None

    def is_cell_empty(self, node_id: int) -> bool:
        """Returns a bool of the contents of a cell."""
        return self.G.nodes[node_id]["agent"] == self.default_val()

    def get_cell_list_contents(self, cell_list: list[int]) -> list[Agent]:
        """Returns a list of the agents contained in the nodes identified
        in `cell_list`; nodes with empty content are excluded.
        """
        list_of_lists = [
            self.G.nodes[node_id]["agent"]
            for node_id in cell_list
            if not self.is_cell_empty(node_id)
        ]
        return [item for sublist in list_of_lists for item in sublist]

    def get_all_cell_contents(self) -> list[Agent]:
        """Returns a list of all the agents in the network."""
        return self.get_cell_list_contents(self.G)

    def iter_cell_list_contents(self, cell_list: list[int]) -> Iterator[Agent]:
        """Returns an iterator of the agents contained in the nodes identified
        in `cell_list`; nodes with empty content are excluded.
        """
        yield from self.get_cell_list_contents(cell_list)
