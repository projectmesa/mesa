# -*- coding: utf-8 -*-
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
import random
import math


def accept_tuple_argument(wrapped_function):
    """ Decorator to allow grid methods that take a list of (x, y) position tuples
    to also handle a single position, by automatically wrapping tuple in
    single-item list rather than forcing user to do it.

    """
    def wrapper(*args):
        if isinstance(args[1], tuple) and len(args[1]) == 2:
            return wrapped_function(args[0], [args[1]])
        else:
            return wrapped_function(*args)
    return wrapper


class Grid:
    """ Base class for a square grid.

    Grid cells are indexed by [x][y], where [0][0] is assumed to be the
    bottom-left and [width-1][height-1] is the top-right. If a grid is
    toroidal, the top and bottom, and left and right, edges wrap to each other

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.
        grid: Internal list-of-lists which holds the grid cells themselves.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
        get_neighborhood: Returns the cells surrounding a given cell.
        get_cell_list_contents: Returns the contents of a list of cells
            ((x,y) tuples)
        neighbor_iter: Iterates over position neightbors.
        coord_iter: Returns coordinates as well as cell contents.
        place_agent: Positions an agent on the grid, and set its pos variable.
        move_agent: Moves an agent from its current position to a new position.
        iter_neighborhood: Returns an iterator over cell coordinates that are
        in the neighborhood of a certain point.
        torus_adj: Converts coordinate, handles torus looping.
        out_of_bounds: Determines whether position is off the grid, returns
        the out of bounds coordinate.
        iter_cell_list_contents: Returns an iterator of the contents of the
        cells identified in cell_list.
        get_cell_list_contents: Returns a list of the contents of the cells
        identified in cell_list.
        remove_agent: Removes an agent from the grid.
        is_cell_empty: Returns a bool of the contents of a cell.

    """
    def __init__(self, width, height, torus):
        """ Create a new grid.

        Args:
            width, height: The width and height of the grid
            torus: Boolean whether the grid wraps or not.

        """
        self.height = height
        self.width = width
        self.torus = torus

        self.grid = []

        for x in range(self.width):
            col = []
            for y in range(self.height):
                col.append(self.default_val())
            self.grid.append(col)

        # Add all cells to the empties list.
        self.empties = list(itertools.product(
                            *(range(self.width), range(self.height))))

    @staticmethod
    def default_val():
        """ Default value for new cell elements. """
        return None

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        # create an iterator that chains the
        #  rows of grid together as if one list:
        return itertools.chain(*self.grid)

    def coord_iter(self):
        """ An iterator that returns coordinates as well as cell contents. """
        for row in range(self.width):
            for col in range(self.height):
                yield self.grid[row][col], row, col    # agent, x, y

    def neighbor_iter(self, pos, moore=True):
        """ Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.
            moore: Boolean for whether to use Moore neighborhood (including
                   diagonals) or Von Neumann (only up/down/left/right).

        """
        neighborhood = self.iter_neighborhood(pos, moore=moore)
        return self.iter_cell_list_contents(neighborhood)

    def iter_neighborhood(self, pos, moore,
                          include_center=False, radius=1):
        """ Return an iterator over cell coordinates that are in the
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
        x, y = pos
        coordinates = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0 and not include_center:
                    continue
                # Skip diagonals in Von Neumann neighborhood.
                if not moore and dy != 0 and dx != 0:
                    continue
                # Skip diagonals in Moore neighborhood when distance > radius
                if moore and radius > 1 and (dy ** 2 + dx ** 2) ** .5 > radius:
                    continue
                # Skip if not a torus and new coords out of bounds.
                if not self.torus and (not (0 <= dx + x < self.width) or
                                       not (0 <= dy + y < self.height)):
                    continue

                px = self.torus_adj(x + dx, self.width)
                py = self.torus_adj(y + dy, self.height)

                # Skip if new coords out of bounds.
                if(self.out_of_bounds((px, py))):
                    continue

                coords = (px, py)
                if coords not in coordinates:
                    coordinates.add(coords)
                    yield coords

    def get_neighborhood(self, pos, moore,
                         include_center=False, radius=1):
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
        return list(self.iter_neighborhood(pos, moore, include_center, radius))

    def iter_neighbors(self, pos, moore,
                       include_center=False, radius=1):
        """ Return an iterator over neighbors to a certain point.

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
        neighborhood = self.iter_neighborhood(
            pos, moore, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(self, pos, moore,
                      include_center=False, radius=1):
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
        return list(self.iter_neighbors(
            pos, moore, include_center, radius))

    def torus_adj(self, coord, dim_len):
        """ Convert coordinate, handling torus looping. """
        if self.torus:
            coord %= dim_len
        return coord

    def out_of_bounds(self, pos):
        """
        Determines whether position is off the grid, returns the out of
        bounds coordinate.
        """
        x, y = pos
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    @accept_tuple_argument
    def iter_cell_list_contents(self, cell_list):
        """
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            An iterator of the contents of the cells identified in cell_list

        """
        return (
            self[x][y] for x, y in cell_list if not self.is_cell_empty((x, y)))

    @accept_tuple_argument
    def get_cell_list_contents(self, cell_list):
        """
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A list of the contents of the cells identified in cell_list

        """
        return list(self.iter_cell_list_contents(cell_list))

    def move_agent(self, agent, pos):
        """
        Move an agent from its current position to a new position.

        Args:
            agent: Agent object to move. Assumed to have its current location
                   stored in a 'pos' tuple.
            pos: Tuple of new position to move the agent to.

        """
        self._remove_agent(agent.pos, agent)
        self._place_agent(pos, agent)
        agent.pos = pos

    def place_agent(self, agent, pos):
        """ Position an agent on the grid, and set its pos variable. """
        self._place_agent(pos, agent)
        agent.pos = pos

    def _place_agent(self, pos, agent):
        """ Place the agent at the correct location. """
        x, y = pos
        self.grid[x][y] = agent
        if pos in self.empties:
            self.empties.remove(pos)

    def remove_agent(self, agent):
        """ Remove the agent from the grid and set its pos variable to None. """
        pos = agent.pos
        self._remove_agent(pos, agent)
        agent.pos = None

    def _remove_agent(self, pos, agent):
        """ Remove the agent from the given location. """
        x, y = pos
        self.grid[x][y] = None
        self.empties.append(pos)

    def is_cell_empty(self, pos):
        """ Returns a bool of the contents of a cell. """
        x, y = pos
        return True if self.grid[x][y] == self.default_val() else False

    def move_to_empty(self, agent):
        """ Moves agent to a random empty cell, vacating agent's old cell. """
        pos = agent.pos
        new_pos = self.find_empty()
        if new_pos is None:
            raise Exception("ERROR: No empty cells")
        else:
            self._place_agent(new_pos, agent)
            agent.pos = new_pos
            self._remove_agent(pos, agent)

    def find_empty(self):
        """ Pick a random empty cell. """
        if self.exists_empty_cells():
            pos = random.choice(self.empties)
            return pos
        else:
            return None

    def exists_empty_cells(self):
        """ Return True if any cells empty else False. """
        return len(self.empties) > 0


class SingleGrid(Grid):
    """ Grid where each cell contains exactly at most one object. """
    empties = []

    def __init__(self, width, height, torus):
        """ Create a new single-item grid.

        Args:
            width, height: The width and width of the grid
            torus: Boolean whether the grid wraps or not.

        """
        super().__init__(width, height, torus)

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
            coords = self.find_empty()
            if coords is None:
                raise Exception("ERROR: Grid full")
        else:
            coords = (x, y)
        agent.pos = coords
        self._place_agent(coords, agent)

    def _place_agent(self, pos, agent):
        if self.is_cell_empty(pos):
            super()._place_agent(pos, agent)
        else:
            raise Exception("Cell not empty")


class MultiGrid(Grid):
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
    @staticmethod
    def default_val():
        """ Default value for new cell elements. """
        return set()

    def _place_agent(self, pos, agent):
        """ Place the agent at the correct location. """
        x, y = pos
        self.grid[x][y].add(agent)
        if pos in self.empties:
            self.empties.remove(pos)

    def _remove_agent(self, pos, agent):
        """ Remove the agent from the given location. """
        x, y = pos
        self.grid[x][y].remove(agent)
        if self.is_cell_empty(pos):
            self.empties.append(pos)

    @accept_tuple_argument
    def iter_cell_list_contents(self, cell_list):
        """
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A iterator of the contents of the cells identified in cell_list

        """
        return itertools.chain.from_iterable(
            self[x][y] for x, y in cell_list if not self.is_cell_empty((x, y)))


class ContinuousSpace:
    """ Continuous space where each agent can have an arbitrary position.

    Assumes that all agents are point objects, and have a pos property storing
    their position as an (x, y) tuple. This class uses a MultiGrid internally
    to store agent objects, to speed up neighborhood lookups.

    """
    _grid = None

    def __init__(self, x_max, y_max, torus, x_min=0, y_min=0,
                 grid_width=100, grid_height=100):
        """ Create a new continuous space.

        Args:
            x_max, y_max: Maximum x and y coordinates for the space.
            torus: Boolean for whether the edges loop around.
            x_min, y_min: (default 0) If provided, set the minimum x and y
                          coordinates for the space. Below them, values loop to
                          the other edge (if torus=True) or raise an exception.
            grid_width, _height: (default 100) Determine the size of the
                                 internal storage grid. More cells will slow
                                 down movement, but speed up neighbor lookup.
                                 Probably only fiddle with this if one or the
                                 other is impacting your model's performance.

        """
        self.x_min = x_min
        self.x_max = x_max
        self.width = x_max - x_min
        self.y_min = y_min
        self.y_max = y_max
        self.height = y_max - y_min
        self.torus = torus

        self.cell_width = (self.x_max - self.x_min) / grid_width
        self.cell_height = (self.y_max - self.y_min) / grid_height

        self._grid = MultiGrid(grid_width, grid_height, torus)

    def place_agent(self, agent, pos):
        """ Place a new agent in the space.

        Args:
            agent: Agent object to place.
            pos: Coordinate tuple for where to place the agent.

        """
        pos = self.torus_adj(pos)
        self._place_agent(pos, agent)
        agent.pos = pos

    def move_agent(self, agent, pos):
        """ Move an agent from its current position to a new position.

        Args:
            agent: The agent object to move.
            pos: Coordinate tuple to move the agent to.

        """
        pos = self.torus_adj(pos)
        self._remove_agent(agent.pos, agent)
        self._place_agent(pos, agent)
        agent.pos = pos

    def _place_agent(self, pos, agent):
        """ Place an agent at a given point, and update the internal grid. """
        cell = self._point_to_cell(pos)
        self._grid._place_agent(cell, agent)

    def _remove_agent(self, pos, agent):
        """ Remove an agent at a given point, and update the internal grid. """
        cell = self._point_to_cell(pos)
        self._grid._remove_agent(cell, agent)

    def get_neighbors(self, pos, radius, include_center=True):
        """ Get all objects within a certain radius.

        Args:
            pos: (x,y) coordinate tuple to center the search at.
            radius: Get all the objects within this distance of the center.
            include_center: If True, include an object at the *exact* provided
                            coordinates. i.e. if you are searching for the
                            neighbors of a given agent, True will include that
                            agent in the results.

        """
        # Get candidate objects
        scale = max(self.cell_width, self.cell_height)
        cell_radius = math.ceil(radius / scale)
        cell_pos = self._point_to_cell(pos)
        possible_objs = self._grid.get_neighbors(cell_pos,
                                                 True, True, cell_radius)
        neighbors = []
        # Iterate over candidates and check actual distance.
        for obj in possible_objs:
            dist = self.get_distance(pos, obj.pos)
            if dist <= radius and (include_center or dist > 0):
                neighbors.append(obj)
        return neighbors

    def get_distance(self, pos_1, pos_2):
        """ Get the distance between two point, accounting for toroidal space.

        Args:
            pos_1, pos_2: Coordinate tuples for both points.

        """
        x1, y1 = pos_1
        x2, y2 = pos_2
        if not self.torus:
            dx = x1 - x2
            dy = y1 - y2
        else:
            d_x = abs(x1 - x2)
            d_y = abs(y1 - y2)
            dx = min(d_x, self.width - d_x)
            dy = min(d_y, self.height - d_y)
        return math.sqrt(dx ** 2 + dy ** 2)

    def torus_adj(self, pos):
        """ Adjust coordinates to handle torus looping.

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
            return (x, y)

    def _point_to_cell(self, pos):
        """ Get the cell coordinates that a given x,y point falls in. """
        if self.out_of_bounds(pos):
            raise Exception("Point out of bounds.")

        x, y = pos
        cell_x = math.floor((x - self.x_min) / self.cell_width)
        cell_y = math.floor((y - self.y_min) / self.cell_height)
        return (cell_x, cell_y)

    def out_of_bounds(self, pos):
        """ Check if a point is out of bounds. """
        x, y = pos
        return (x < self.x_min or x >= self.x_max or
                y < self.y_min or y >= self.y_max)
