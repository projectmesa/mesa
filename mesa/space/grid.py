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

from typing import Iterable, Iterator, List, Optional, Set, Tuple, Union
from mesa.agent import Agent

Coordinate = Tuple[int, int]
GridContent = List[Agent]


def accept_tuple_argument(wrapped_function):
    """ Decorator to allow grid methods that take a list of (x, y) coord tuples
    to also handle a single position, by automatically wrapping tuple in
    single-item list rather than forcing user to do it.

    """

    def wrapper(*args):
        if isinstance(args[1], tuple) and len(args[1]) == 2:
            return wrapped_function(args[0], [args[1]])
        else:
            return wrapped_function(*args)

    return wrapper


class MultiGrid:
    """ Base class for a square grid.

    Grid cells are indexed by [x][y], where [0][0] is assumed to be the
    bottom-left and [width-1][height-1] is the top-right. If a grid is
    toroidal, the top and bottom, and left and right, edges wrap to each other

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.
        grid: Internal list-of-lists which holds the grid cells themselves.
        empties: List of empty cells

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
        get_neighborhood: Returns the cells surrounding a given cell.
        get_contents: Returns the contents of a list of cells ((x,y) tuples)
        coord_iter: Returns coordinates as well as cell contents.
        place_agent: Positions an agent on the grid, and set its pos variable.
        move_agent: Moves an agent from its current position to a new position.
        torus_adj: Converts coordinate, handles torus looping.
        out_of_bounds: Determines whether position is off the grid
        is_cell_empty: Returns a bool of the contents of a cell.

    """

    def __init__(self, width: int, height: int, torus: bool) -> None:
        """ Create a new grid.

        Args:
            width, height: The width and height of the grid
            torus: Boolean whether the grid wraps or not.

        """
        self.height = height
        self.width = width
        self.torus = torus

        self._grid = []  # type: List[List[GridContent]]

        for x in range(self.width):
            col = []  # type: List[GridContent]
            for y in range(self.height):
                col.append([])
            self._grid.append(col)

        # Add all cells to the empties list.
        self._empties = set(itertools.product(range(self.width), range(self.height)))
        self._all_cells = frozenset(self._empties)

        # Neighborhood Cache
        self._neighborhood_cache = dict()

    def __getitem__(self, pos: Coordinate) -> GridContent:
        if isinstance(pos, int):
            return self._grid[x]
        x, y = pos
        return self._grid[x][y]

    def __iter__(self) -> Iterator[GridContent]:
        """
        create an iterator that chains the
        rows of grid together as if one list:
        """
        return itertools.chain.from_iterable(self._grid)

    def coord_iter(self) -> Iterator[Tuple[GridContent, int, int]]:
        """ An iterator that returns coordinates as well as cell contents. """
        for row in range(self.width):
            for col in range(self.height):
                yield self[row, col], row, col  # agent, x, y

    def torus_adj(self, pos: Coordinate) -> Coordinate:
        """ Convert coordinate, handling torus looping. """
        if not self.out_of_bounds(pos):
            return pos
        elif not self.torus:
            raise Exception("Point out of bounds, and space non-toroidal.")
        else:
            x, y = pos[0] % self.width, pos[1] % self.height
        return x, y

    def out_of_bounds(self, pos: Coordinate) -> bool:
        """
        Determines whether position is off the grid, returns the out of
        bounds coordinate.
        """
        return tuple(pos) not in self._all_cells

    def place_agent(self, agent: Agent, pos: Coordinate) -> Agent:
        """ Position an agent on the grid, and set its pos variable. """
        x, y = pos
        self._grid[x][y].append(agent)
        self._empties.discard(pos)
        setattr(agent, "pos", pos)
        return agent

    def remove_agent(self, agent: Agent) -> Agent:
        """ Remove the agent from the grid and set its pos variable to None. """
        x, y = getattr(agent, "pos")
        content = self._grid[x][y]
        content.remove(agent)
        if not content:
            self._empties.add((x, y))
        setattr(agent, "pos", None)
        return agent

    def move_agent(self, agent: Agent, pos: Coordinate) -> Agent:
        """
        Move an agent from its current position to a new position.

        Args:
            agent: Agent object to move. Assumed to have its current location
                   stored in a 'pos' tuple.
            pos: Tuple of new position to move the agent to.

        """
        pos = self.torus_adj(pos)
        self.remove_agent(agent)
        self.place_agent(agent, pos)
        return agent

    @accept_tuple_argument
    def get_contents(self, cell_list: Iterable[Coordinate]) -> List[GridContent]:
        """Docstring."""
        return [self[pos] for pos in cell_list if not self.is_cell_empty(pos)]

    def get_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> List[Coordinate]:
        """ Return a list of cells that are in the neighborhood of a
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
            x, y = pos
            coordinates = set()  # type: Set[Coordinate]
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and not include_center:
                        continue
                    # Skip coordinates that are outside manhattan distance
                    if not moore and abs(dx) + abs(dy) > radius:
                        continue
                    # Skip if not a torus and new coords out of bounds.
                    coord = (x + dx, y + dy)

                    if self.out_of_bounds(coord):
                        if not self.torus:
                            continue
                        else:
                            coord = self.torus_adj(coord)

                    if coord not in coordinates:
                        coordinates.add(coord)

            neighborhood = sorted(coordinates)
            self._neighborhood_cache[cache_key] = neighborhood
        return neighborhood

    def get_neighbors(
        self,
        pos: Coordinate,
        moore: bool = True,
        include_center: bool = False,
        radius: int = 1,
    ) -> List[Agent]:
        """ Return a list of neighbors to a certain point.

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
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        neighbors = self.get_contents(neighborhood)
        return list(itertools.chain.from_iterable(neighbors))

    def neighbor_iter(
        self, pos: Coordinate, moore: bool = True
    ) -> Iterator[GridContent]:
        """ Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
            moore: Boolean for whether to use Moore neighborhood (including
                   diagonals) or Von Neumann (only up/down/left/right).

        """
        neighbors = self.get_neighbors(pos, moore)
        return (neighbor for neighbor in neighbors)

    def iter_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[Coordinate]:
        """Depreciated."""
        yield from self.get_neighborhood(pos, moore, include_center, radius)

    def iter_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[GridContent]:
        """Depreciated."""
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        yield from self.get_contents(neighborhood)

    @accept_tuple_argument
    def iter_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> Iterator[GridContent]:
        """Depreciated."""
        yield from self.get_contents(cell_list)

    @accept_tuple_argument
    def get_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> List[GridContent]:
        """Depreciated"""
        return list(itertools.chain(*self.get_contents(cell_list)))

    def is_cell_empty(self, pos: Coordinate) -> bool:
        """ Returns a bool of the contents of a cell. """
        return pos in self._empties

    def move_to_empty(self, agent: Agent) -> None:
        """ Moves agent to a random empty cell, vacating agent's old cell. """
        pos = agent.pos
        if len(self._empties) == 0:
            raise Exception("ERROR: No empty cells")
        new_pos = agent.random.choice(self.empties)
        self.move_agent(agent, new_pos)

    def find_empty(self) -> Optional[Coordinate]:
        """ Pick a random empty cell. """
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
            pos = random.choice(self.empties)
            return pos
        else:
            return None

    @property
    def empties(self) -> List[Coordinate]:
        return sorted(self._empties)

    def exists_empty_cells(self) -> bool:
        """ Return True if any cells empty else False. """
        return len(self._empties) > 0


class SingleGrid(MultiGrid):
    """ Grid where each cell contains exactly at most one object. """

    def __init__(self, width: int, height: int, torus: bool) -> None:
        """ Create a new single-item grid.

        Args:
            width, height: The width and width of the grid
            torus: Boolean whether the grid wraps or not.

        """
        super().__init__(width, height, torus)

    def __getitem__(self, pos):
        if isinstance(pos, int):
            return self._grid[pos]
        x, y = pos
        content = self._grid[x][y]
        return content[0] if content else None

    def position_agent(self, agent, x="random", y="random"):
        """ Position an agent on the grid.
        This is used when first placing agents! Use 'move_to_empty()'
        when you want agents to jump to an empty cell.
        Use 'swap_pos()' to swap agents positions.
        If x or y are positive, they are used, but if "random",
        we get a random position.
        Ensure this random position is not occupied (in Grid).

        """
        if x == "random" or y == "random":
            if len(self._empties) == 0:
                raise Exception("ERROR: Grid full")
            coords = agent.random.choice(self.empties)
        else:
            coords = (x, y)
        agent.pos = coords
        self.place_agent(agent, coords)

    def place_agent(self, agent: Agent, pos: Coordinate) -> Agent:
        if self.is_cell_empty(pos):
            return super().place_agent(agent, pos)
        else:
            raise Exception("Cell not empty")

    def get_neighbors(
        self,
        pos: Coordinate,
        moore: bool = True,
        include_center: bool = False,
        radius: int = 1,
    ) -> List[Agent]:
        """ Return a list of neighbors to a certain point.

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
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        return self.get_contents(neighborhood)
        # return list(itertools.chain.from_iterable(neighbors))

    @accept_tuple_argument
    def get_cell_list_contents(self, cell_list):
        return self.get_contents(cell_list)


class Grid(SingleGrid):
    """ Grid where each cell can contain more than one object.

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

    def place_agent(self, agent, pos):
        if not self.is_cell_empty(pos):
            x, y = pos
            self._grid[x][y].clear()
            self._empties.add(pos)
        return super().place_agent(agent, pos)
