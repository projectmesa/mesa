"""
Mesa Space Module
=================

Objects used to add a spatial component to a model.

Grid: base grid, a simple list-of-lists.
SingleGrid: grid which strictly enforces one object per cell.
MultiGrid: extension to Grid where each cell is a set of objects.

"""
# Instruction for PyLint to suppress variable name errors, since we have a
# good reason to use one-character variable names for x and y.
# pylint: disable=invalid-name

import itertools

import numpy as np

from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Sequence,
    Tuple,
    Union,
    cast,
    overload,
)
from .agent import Agent

Coordinate = Tuple[int, int]
GridContent = Union[Optional[Agent], Set[Agent]]
# used in ContinuousSpace
FloatCoordinate = Union[Tuple[float, float], np.ndarray]


def clamp(x: float, lowest: float, highest: float) -> float:
    # This should be faster than np.clip for a scalar x.
    # TODO: measure how much faster this function is.
    return max(lowest, min(x, highest))


def accept_tuple_argument(wrapped_function):
    """Decorator to allow grid methods that take a list of (x, y) coord tuples
    to also handle a single position, by automatically wrapping tuple in
    single-item list rather than forcing user to do it."""

    def wrapper(*args: Any):
        if isinstance(args[1], tuple) and len(args[1]) == 2:
            return wrapped_function(args[0], [args[1]])
        else:
            return wrapped_function(*args)

    return wrapper


class Grid:
    """Base class for a square grid.

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

        self.grid: List[List[GridContent]] = []

        for x in range(self.width):
            col: List[GridContent] = []
            for y in range(self.height):
                col.append(self.default_val())
            self.grid.append(col)

        # Add all cells to the empties list.
        self.empties = set(itertools.product(*(range(self.width), range(self.height))))

        # Neighborhood Cache
        self._neighborhood_cache: Dict[Any, List[Coordinate]] = dict()

    @staticmethod
    def default_val() -> None:
        """Default value for new cell elements."""
        return None

    @overload
    def __getitem__(self, index: int) -> List[GridContent]:
        ...

    @overload
    def __getitem__(
        self, index: Tuple[Union[int, slice], Union[int, slice]]
    ) -> Union[GridContent, List[GridContent]]:
        ...

    @overload
    def __getitem__(self, index: Sequence[Coordinate]) -> List[GridContent]:
        ...

    def __getitem__(
        self,
        index: Union[
            int,
            Sequence[Coordinate],
            Tuple[Union[int, slice], Union[int, slice]],
        ],
    ) -> Union[GridContent, List[GridContent]]:
        """Access contents from the grid."""

        if isinstance(index, int):
            # grid[x]
            return self.grid[index]

        if isinstance(index[0], tuple):
            # grid[(x1, y1), (x2, y2)]
            index = cast(Sequence[Coordinate], index)

            cells = []
            for pos in index:
                x1, y1 = self.torus_adj(pos)
                cells.append(self.grid[x1][y1])
            return cells

        x, y = index

        if isinstance(x, int) and isinstance(y, int):
            # grid[x, y]
            index = cast(Coordinate, index)
            x, y = self.torus_adj(index)
            return self.grid[x][y]

        if isinstance(x, int):
            # grid[x, :]
            x, _ = self.torus_adj((x, 0))
            x = slice(x, x + 1)

        if isinstance(y, int):
            # grid[:, y]
            _, y = self.torus_adj((0, y))
            y = slice(y, y + 1)

        # grid[:, :]
        x, y = (cast(slice, x), cast(slice, y))
        cells = []
        for rows in self.grid[x]:
            for cell in rows[y]:
                cells.append(cell)
        return cells

        raise IndexError

    def __iter__(self) -> Iterator[GridContent]:
        """Create an iterator that chains the rows of the grid together
        as if it is one list:"""
        return itertools.chain(*self.grid)

    def coord_iter(self) -> Iterator[Tuple[GridContent, int, int]]:
        """An iterator that returns coordinates as well as cell contents."""
        for row in range(self.width):
            for col in range(self.height):
                yield self.grid[row][col], row, col  # agent, x, y

    def neighbor_iter(
        self, pos: Coordinate, moore: bool = True
    ) -> Iterator[GridContent]:
        """Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
            moore: Boolean for whether to use Moore neighborhood (including
                   diagonals) or Von Neumann (only up/down/left/right).
        """
        neighborhood = self.get_neighborhood(pos, moore=moore)
        return self.iter_cell_list_contents(neighborhood)

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
            A list of coordinate tuples representing the neighborhood. For
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
    ) -> List[Coordinate]:
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

        if neighborhood is None:
            coordinates: Set[Coordinate] = set()

            x, y = pos
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and not include_center:
                        continue
                    # Skip coordinates that are outside manhattan distance
                    if not moore and abs(dx) + abs(dy) > radius:
                        continue

                    coord = (x + dx, y + dy)

                    if self.out_of_bounds(coord):
                        # Skip if not a torus and new coords out of bounds.
                        if not self.torus:
                            continue
                        coord = self.torus_adj(coord)

                    coordinates.add(coord)

            neighborhood = sorted(coordinates)
            self._neighborhood_cache[cache_key] = neighborhood

        return neighborhood

    def iter_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[GridContent]:
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
    ) -> List[GridContent]:
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
    ) -> Iterator[GridContent]:
        """Returns an iterator of the contents of the cells
        identified in cell_list.

        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            An iterator of the contents of the cells identified in cell_list
        """
        return filter(None, (self.grid[x][y] for x, y in cell_list))

    @accept_tuple_argument
    def get_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> List[GridContent]:
        """Returns a list of the contents of the cells
        identified in cell_list.

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
        self._remove_agent(agent.pos, agent)
        self._place_agent(pos, agent)
        agent.pos = pos

    def place_agent(self, agent: Agent, pos: Coordinate) -> None:
        """Position an agent on the grid, and set its pos variable."""
        self._place_agent(pos, agent)
        agent.pos = pos

    def _place_agent(self, pos: Coordinate, agent: Agent) -> None:
        """Place the agent at the correct location."""
        x, y = pos
        self.grid[x][y] = agent
        self.empties.discard(pos)

    def remove_agent(self, agent: Agent) -> None:
        """Remove the agent from the grid and set its pos variable to None."""
        pos = agent.pos
        self._remove_agent(pos, agent)
        agent.pos = None

    def _remove_agent(self, pos: Coordinate, agent: Agent) -> None:
        """Remove the agent from the given location."""
        x, y = pos
        self.grid[x][y] = None
        self.empties.add(pos)

    def is_cell_empty(self, pos: Coordinate) -> bool:
        """Returns a bool of the contents of a cell."""
        x, y = pos
        return self.grid[x][y] == self.default_val()

    def move_to_empty(
        self, agent: Agent, cutoff: float = 0.998, num_agents: Optional[int] = None
    ) -> None:
        """Moves agent to a random empty cell, vacating agent's old cell."""
        pos = agent.pos
        if len(self.empties) == 0:
            raise Exception("ERROR: No empty cells")
        if num_agents is None:
            try:
                num_agents = agent.model.schedule.get_agent_count()
            except AttributeError:
                raise Exception(
                    "Your agent is not attached to a model, and so Mesa is unable\n"
                    "to figure out the total number of agents you have created.\n"
                    "This number is required in order to calculate the threshold\n"
                    "for using a much faster algorithm to find an empty cell.\n"
                    "In this case, you must specify `num_agents`."
                )
        new_pos = (0, 0)  # Initialize it with a starting value.
        # This method is based on Agents.jl's random_empty() implementation.
        # See https://github.com/JuliaDynamics/Agents.jl/pull/541.
        # For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052.
        # This switch assumes the worst case (for this algorithm) of one
        # agent per position, which is not true in general but is appropriate
        # here.
        if clamp(num_agents / (self.width * self.height), 0.0, 1.0) < cutoff:
            # The default cutoff value provided is the break-even comparison
            # with the time taken in the else branching point.
            # The number is measured to be 0.998 in Agents.jl, but since Mesa
            # run under different environment, the number is different here.
            while True:
                new_pos = (
                    agent.random.randrange(self.width),
                    agent.random.randrange(self.height),
                )
                if self.is_cell_empty(new_pos):
                    break
        else:
            new_pos = agent.random.choice(sorted(self.empties))
        self._place_agent(new_pos, agent)
        agent.pos = new_pos
        self._remove_agent(pos, agent)

    def find_empty(self) -> Optional[Coordinate]:
        """Pick a random empty cell."""
        from warnings import warn
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

    empties: Set[Coordinate] = set()

    def __init__(self, width: int, height: int, torus: bool) -> None:
        """Create a new single-item grid.

        Args:
            width, height: The width and width of the grid
            torus: Boolean whether the grid wraps or not.
        """
        super().__init__(width, height, torus)

    def position_agent(
        self, agent: Agent, x: Union[int, str] = "random", y: Union[int, str] = "random"
    ) -> None:
        """Position an agent on the grid.
        This is used when first placing agents! Use 'move_to_empty()'
        when you want agents to jump to an empty cell.
        Use 'swap_pos()' to swap agents positions.
        If x or y are positive, they are used, but if "random",
        we get a random position.
        Ensure this random position is not occupied (in Grid).
        """
        if x == "random" or y == "random":
            if len(self.empties) == 0:
                raise Exception("ERROR: Grid full")
            coords = agent.random.choice(sorted(self.empties))
        else:
            coords = (x, y)
        agent.pos = coords
        self._place_agent(coords, agent)

    def _place_agent(self, pos: Coordinate, agent: Agent) -> None:
        if self.is_cell_empty(pos):
            super()._place_agent(pos, agent)
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

    @staticmethod
    def default_val() -> Set[Agent]:
        """Default value for new cell elements."""
        return []

    def _place_agent(self, pos: Coordinate, agent: Agent) -> None:
        """Place the agent at the correct location."""
        x, y = pos
        if agent not in self.grid[x][y]:
            self.grid[x][y].append(agent)
        self.empties.discard(pos)

    def _remove_agent(self, pos: Coordinate, agent: Agent) -> None:
        """Remove the agent from the given location."""
        x, y = pos
        self.grid[x][y].remove(agent)
        if self.is_cell_empty(pos):
            self.empties.add(pos)

    @accept_tuple_argument
    def iter_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> Iterator[GridContent]:
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
        neighbor_iter: Iterates over position neighbors.
        iter_neighborhood: Returns an iterator over cell coordinates that are
            in the neighborhood of a certain point.
    """

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
            A list of coordinate tuples representing the neighborhood. For
            example with radius 1, it will return list with number of elements
            equals at most 9 (8) if Moore, 5 (4) if Von Neumann (if not
            including the center).
        """

        def torus_adj_2d(pos: Coordinate) -> Coordinate:
            return (pos[0] % self.width, pos[1] % self.height)

        coordinates = set()

        def find_neighbors(pos: Coordinate, radius: int) -> None:
            x, y = pos

            """
            Both: (0,-), (0,+)

            Even: (-,+), (-,0), (+,+), (+,0)
            Odd:  (-,0), (-,-), (+,0), (+,-)
            """
            adjacent = [(x, y - 1), (x, y + 1)]

            if include_center:
                adjacent.append(pos)

            if x % 2 == 0:
                adjacent += [(x - 1, y + 1), (x - 1, y), (x + 1, y + 1), (x + 1, y)]
            else:
                adjacent += [(x - 1, y), (x - 1, y - 1), (x + 1, y), (x + 1, y - 1)]

            if self.torus is False:
                adjacent = list(
                    filter(lambda coords: not self.out_of_bounds(coords), adjacent)
                )
            else:
                adjacent = [torus_adj_2d(coord) for coord in adjacent]

            coordinates.update(adjacent)

            if radius > 1:
                [find_neighbors(coords, radius - 1) for coords in adjacent]

        find_neighbors(pos, radius)

        if not include_center and pos in coordinates:
            coordinates.remove(pos)

        yield from coordinates

    def neighbor_iter(self, pos: Coordinate) -> Iterator[GridContent]:
        """Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
        """
        neighborhood = self.iter_neighborhood(pos)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighborhood(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> List[Coordinate]:
        """Return a list of cells that are in the neighborhood of a
        certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the neighborhood;
            With radius 1
        """
        return list(self.iter_neighborhood(pos, include_center, radius))

    def iter_neighbors(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> Iterator[GridContent]:
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
        neighborhood = self.iter_neighborhood(pos, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(
        self, pos: Coordinate, include_center: bool = False, radius: int = 1
    ) -> List[Coordinate]:
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

    Assumes that all agents are point objects, and have a pos property storing
    their position as an (x, y) tuple. This class uses a numpy array internally
    to store agent objects, to speed up neighborhood lookups.
    """

    _grid = None

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

        self._agent_points = None
        self._index_to_agent: Dict[int, Agent] = {}
        self._agent_to_index: Dict[Agent, int] = {}

    def place_agent(self, agent: Agent, pos: FloatCoordinate) -> None:
        """Place a new agent in the space.

        Args:
            agent: Agent object to place.
            pos: Coordinate tuple for where to place the agent.
        """
        pos = self.torus_adj(pos)
        if self._agent_points is None:
            self._agent_points = np.array([pos])
        else:
            self._agent_points = np.append(self._agent_points, np.array([pos]), axis=0)
        self._index_to_agent[self._agent_points.shape[0] - 1] = agent
        self._agent_to_index[agent] = self._agent_points.shape[0] - 1
        agent.pos = pos

    def move_agent(self, agent: Agent, pos: FloatCoordinate) -> None:
        """Move an agent from its current position to a new position.

        Args:
            agent: The agent object to move.
            pos: Coordinate tuple to move the agent to.
        """
        pos = self.torus_adj(pos)
        idx = self._agent_to_index[agent]
        self._agent_points[idx, 0] = pos[0]
        self._agent_points[idx, 1] = pos[1]
        agent.pos = pos

    def remove_agent(self, agent: Agent) -> None:
        """Remove an agent from the simulation.

        Args:
            agent: The agent object to remove
        """
        if agent not in self._agent_to_index:
            raise Exception("Agent does not exist in the space")
        idx = self._agent_to_index[agent]
        del self._agent_to_index[agent]
        max_idx = max(self._index_to_agent.keys())
        # Delete the agent's position and decrement the index/agent mapping
        self._agent_points = np.delete(self._agent_points, idx, axis=0)
        for a, index in self._agent_to_index.items():
            if index > idx:
                self._agent_to_index[a] = index - 1
                self._index_to_agent[index - 1] = a
        # The largest index is now redundant
        del self._index_to_agent[max_idx]
        agent.pos = None

    def get_neighbors(
        self, pos: FloatCoordinate, radius: float, include_center: bool = True
    ) -> List[GridContent]:
        """Get all objects within a certain radius.

        Args:
            pos: (x,y) coordinate tuple to center the search at.
            radius: Get all the objects within this distance of the center.
            include_center: If True, include an object at the *exact* provided
                            coordinates. i.e. if you are searching for the
                            neighbors of a given agent, True will include that
                            agent in the results.
        """
        deltas = np.abs(self._agent_points - np.array(pos))
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2

        (idxs,) = np.where(dists <= radius ** 2)
        neighbors = [
            self._index_to_agent[x] for x in idxs if include_center or dists[x] > 0
        ]
        return neighbors

    def get_heading(
        self, pos_1: FloatCoordinate, pos_2: FloatCoordinate
    ) -> FloatCoordinate:
        """Get the heading angle between two points, accounting for toroidal space.

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

        dx = np.abs(x1 - x2)
        dy = np.abs(y1 - y2)
        if self.torus:
            dx = min(dx, self.width - dx)
            dy = min(dy, self.height - dy)
        return np.sqrt(dx * dx + dy * dy)

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
        self.G = G
        for node_id in self.G.nodes:
            G.nodes[node_id]["agent"] = list()

    def place_agent(self, agent: Agent, node_id: int) -> None:
        """Place a agent in a node."""

        self._place_agent(agent, node_id)
        agent.pos = node_id

    def get_neighbors(self, node_id: int, include_center: bool = False) -> List[int]:
        """Get all adjacent nodes"""

        neighbors = list(self.G.neighbors(node_id))
        if include_center:
            neighbors.append(node_id)

        return neighbors

    def move_agent(self, agent: Agent, node_id: int) -> None:
        """Move an agent from its current node to a new node."""

        self._remove_agent(agent, agent.pos)
        self._place_agent(agent, node_id)
        agent.pos = node_id

    def _place_agent(self, agent: Agent, node_id: int) -> None:
        """Place the agent at the correct node."""

        self.G.nodes[node_id]["agent"].append(agent)

    def _remove_agent(self, agent: Agent, node_id: int) -> None:
        """Remove an agent from a node."""

        self.G.nodes[node_id]["agent"].remove(agent)

    def remove_agent(self, agent: Agent) -> None:
        """Remove the agent from the network and set its pos variable to None."""
        pos = agent.pos
        self._remove_agent(agent, pos)
        agent.pos = None

    def is_cell_empty(self, node_id: int) -> bool:
        """Returns a bool of the contents of a cell."""
        return not self.G.nodes[node_id]["agent"]

    def get_cell_list_contents(self, cell_list: List[int]) -> List[GridContent]:
        """Returns the contents of a list of cells ((x,y) tuples)"""
        return list(self.iter_cell_list_contents(cell_list))

    def get_all_cell_contents(self) -> List[GridContent]:
        """Returns a list of the contents of the cells
        identified in cell_list."""
        return list(self.iter_cell_list_contents(self.G))

    def iter_cell_list_contents(self, cell_list: List[int]) -> List[GridContent]:
        """Returns an iterator of the contents of the cells
        identified in cell_list."""
        list_of_lists = [
            self.G.nodes[node_id]["agent"]
            for node_id in cell_list
            if not self.is_cell_empty(node_id)
        ]
        return [item for sublist in list_of_lists for item in sublist]
