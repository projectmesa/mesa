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
import numpy as np


class Grid:
    """ Class for a square grid.

    Grid cells are indexed by [x][y], where [0][0] is assumed to be the
    bottom-left and [width-1][height-1] is the top-right. If a grid is
    toroidal, the top and bottom, and left and right, edges wrap to each other

    Properties:
        model: Subtype of Model that the grid is situated in
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.
        multigrid: If True, a cell may hold more than one agent

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
        remove_agent: Removes an agent from the grid.
        is_cell_empty: Returns a bool of the contents of a cell.

    """

    def __init__(self, model, width, height, torus, multigrid=False):
        """ Create a new grid.

        Args:
            model: Subtype of Model that the grid is situated in
            width, height: The width and height of the grid
            torus: Boolean whether the grid wraps or not.
            multigrid: If True, a cell may hold more than one agent
        """

        self.model = model
        self.height = height
        self.width = width
        self.torus = torus
        self.multigrid = multigrid
        self._grid = []

        for x in range(self.width):
            col = []
            for y in range(self.height):
                col.append(self.empty_value)
            self._grid.append(col)

        self.empties = set(itertools.product(
            *(range(self.width), range(self.height))))

    def __getitem__(self, index):
        return self._grid[index]

    def __iter__(self):
        # create an iterator that chains the
        #  rows of grid together as if one list:
        return itertools.chain(*self.grid)

    @property
    def empty_value(self):
        if self.multigrid:
            return set()
        else:
            return None

    def is_cell_empty(self, pos):
        """ Returns a bool of the contents of a cell. """
        x, y = pos
        return self._grid[x][y] == self.empty_value

    def exists_empty_cells(self):
        """ Return True if any cells empty else False. """
        return len(self.empties) > 0

    def coord_iter(self):
        """ Returns an iterator of tuples (agent, x, y) over the whole square grid. """
        for x in range(self.width):
            for y in range(self.height):
                yield self._grid[x][y], x, y

    def neighbors(self, pos, moore=True, radius=1, get_agents=False, include_empty=False):
        """
        Args:
            pos: coordinates (x, y) for the neighborhood to get
            moore: if True, return Moore neighborhood
                        (including diagonals)
                   if False, return Von Neumann neighborhood
                        (exclude diagonals)
            radius: range of the Moore/von Neumann neighborhood
            get_agents:
                if True, return (agent, (x, y)) as a set element
                if False, return (x, y) as a set element
            include_empty:
                if True, treat empty cells as valid adjacent cells
                if False, skip empty cells

        Returns:
            A set of adjacent cells of a single cell at `pos`.

            The number of cells
            in the Moore neighborhood with radius n is (2n+1)^2 -1.
            The number of cells in the Moore neighborhood with radius n is [(2n+1)^2 -1]
            (http://www.conwaylife.com/wiki/Moore_neighbourhood).

            The number of cells in the von Neumann neighbourhood of
            radius n of a single cell is
            [2n(n+1)](http://www.conwaylife.com/wiki/Von_Neumann_neighborhood).
        """
        if moore:
            neighbors = self._moore(pos, radius, get_agents, include_empty)
        else:
            neighbors = self._von_neumann(
                pos, radius, get_agents, include_empty)

        return neighbors

    def row_iter(self, row, include_agents=False):
        """ Return an iterator over a specific row

        Args:
            include_agents: return ((x, y), agent) if True, otherwise (x, y)
        """
        _, y = self._torus_adj((0, row))
        for x in range(self.width):
            if include_agents:
                yield ((x, y), self._grid[x][y])
            else:
                yield (x, y)

    def col_iter(self, col, include_agents=False):
        """ Return an iterator over a specific column """
        x, _ = self._torus_adj((col, 0))
        for y in range(self.height):
            if include_agents:
                yield ((x, y), self._grid[x][y])
            else:
                yield (x, y)

    def _moore(self, pos, radius, get_agents, include_empty):
        neighbors = set()

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = self._torus_adj((pos[0] + dx, pos[1] + dy))
                # If a cell is empty and empty cell should not be returned, skip
                if (self._grid[x][y] == self.empty_value) and (not include_empty):
                    continue
                if (get_agents):
                    neighbors.add((self.grid[x][y], (x, y)))
                else:
                    neighbors.add((x, y))
        return neighbors

    def _von_neumann(self, pos, radius, get_agents, include_empty):
        neighbors = set()

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = self._torus_adj((pos[0] + dx, pos[1] + dy))
                # If a cell is empty and empty cell should not be returned, skip
                if (self.grid[x][y] == self.empty_value) and (not include_empty):
                    continue
                # Skip coordinates that are outside manhattan distance
                if abs(dx) + abs(dy) > radius:
                    break
                if (get_agents):
                    neighbors.add((self.grid[x][y], (x, y)))
                else:
                    neighbors.add((x, y))

        return neighbors

    def _torus_adj(self, pos):
        """ Convert coordinate, handling torus looping. """
        if self.torus:
            x, y = pos[0] % self.width, pos[1] % self.height
            return x, y
        else:
            if (not 0 <= pos[0] < self.width) or (not 0 <= pos[1] < self.height):
                raise IndexError(
                    "Coordinates out of bounds. Grid is non-toroidal.")

    def move_agent(self, agent, pos, replace=False):
        """
        Move an agent from its current position to a new position.

        Args:
            agent: Agent object to move. Assumed to have its current location
                   stored in a 'pos' tuple.
            pos: Tuple of new position to move the agent to.
            replace: if True, replace the possibly existed agent at `pos` with `agent`
        """
        pos = self._torus_adj(pos)
        self._remove_agent(agent.pos, agent)
        self._place_agent(pos, agent, replace)
        agent.pos = pos

    def place_agent(self, agent, pos=("random", "random"), replace=False):
        """ Position an agent on the grid, and set its pos variable.

        Args:
            agent: agent to place at `pos`
            pos: coordinates of the grid (x, y)
            replace: if True, replace the possibly existed agent at `pos` with `agent`
        """
        if (pos[0] == "random") or (pos[1] == "random"):
            pos = self.pick_random_position(agent, pos)
        self._place_agent(pos, agent, replace)
        agent.pos = pos

    def _place_agent(self, pos, agent, replace):
        """ Place the agent at the correct location. """
        x, y = pos
        old_agent = self.grid[x][y]

        if old_agent == self.empty_value:
            self.grid[x][y] = set((agent, )) if self.multigrid else agent
            self.empties.remove(pos)
        else:
            if replace:
                old_agent.pos = None
                self.grid[x][y] = agent
            else:
                if self.multigrid:
                    self._grid[x][y].add(agent)
                else:
                    raise Exception(
                        "Cell already occupied by agent {}".format(old_agent.unique_id))

    def pick_random_position(self, agent, pos):
        if (pos[0], pos[1]) == ("random", "random") and self.exists_empty_cells():
            return agent.random.choice(tuple(self.empties))
        else:
            empties = set()
            if pos[0] == "random":
                # We pick a random cell in a specified row
                for coords, cell in self.row_iter(pos[1], include_agents=True):
                    if cell == self.empty_value:
                        empties.add(coords)
            else:
                # We pick a random cell in a specified column
                for coords, cell in self.col_iter(pos[0], include_agents=True):
                    if cell == self.empty_value:
                        empties.add(coords)

            if len(empties) > 0:
                return agent.random.choice(empties)
            else:
                raise Exception("ERROR: No empty cells")

    def remove_agent(self, agent):
        """ Remove the agent from the grid and set its pos variable to None. """
        x, y = agent.pos
        if self.multigrid:
            self.grid[x][y].remove(agent)
            if len(self.grid[x][y]) == 0:
                self.empties.add((x, y))
        else:
            self.grid[x][y] = None
            self.empties.add((x, y))

        agent.pos = None

    def move_to_empty(self, agent):
        """ Moves agent to a random empty cell, vacating agent's old cell. """

        if not self.exists_empty_cells():
            raise Exception("ERROR: No empty cells")
        else:
            self.pick_random_position(agent, agent.pos)
            self.remove_agent(agent)
            new_pos = agent.random.choice(self.empties)
            self._place_agent(new_pos, agent, replace=False)
            agent.pos = new_pos

    def agents_on_coords(self, cells):
        """ Given a list of cell coordinates (x, y), return a list of respective agents

        Args:
            cells: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A list of agents corresponding to the given positions.
        """
        if not isinstance(cells, list):
            cells = [cells]
        return [self.grid[x][y] for x, y in cells]

    # Deprecated methods below
    def find_empty(self):
        """ Pick a random empty cell. """
        from warnings import warn
        import random

        warn(("`find_empty` is being phased out since it uses the global "
              "`random` instead of the model-level random-number generator. "
              "Consider replacing it with having a model or agent object "
              "explicitly pick one of the grid's list of empty cells."),
             DeprecationWarning)

        if self.exists_empty_cells():
            pos = random.choice(self.empties)
            return pos
        else:
            return None

    def get_neighbors(self, pos, moore,
                      include_center=False, radius=1):
        import warnings
        warnings.warn(
            "Deprecated method. Call neighbors(pos, moore, radius, True) instead. \
            In addition, parameter `include_center` is removeed.Use `self` in the code. ",
            DeprecationWarning)

        return self.neighbors(pos, moore, radius, True)

    def position_agent(self, agent, x="random", y="random"):
        import warnings
        warnings.warn(
            "Deprecated method. Call place_agent(pos) instead.", DeprecationWarning)

        self.place_agent(agent, (x, y))

    def get_cell_list_contents(self, cells):
        import warnings
        warnings.warn(
            "Deprecated method. Call agents_on_coords(cells) instead.", DeprecationWarning)

        return self.agents_on_coords(cells)

    def iter_cell_list_contents(self, cells):
        import warnings
        warnings.warn(
            "Deprecated method. Call agents_on_coords(cells) instead.", DeprecationWarning)

        return self.agents_on_coords(cells)


class SingleGrid(Grid):
    """Depreciated class."""

    def __init__(self, width, height, torus):
        super().__init__(width, height, torus, multigrid=False)


class MultiGrid(Grid):
    """Depreciated class."""

    def __init__(self, width, height, torus):
        super().__init__(width, height, torus, multigrid=True)


class HexGrid(Grid):
    """ Hexagonal Grid: Extends Grid to handle hexagonal neighbors.

    Functions according to odd-q rules.
    See http://www.redblobgames.com/grids/hexagons/#coordinates for more.

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
        get_neighborhood: Returns the cells surrounding a given cell.
        neighbor_iter: Iterates over position neightbors.
        iter_neighborhood: Returns an iterator over cell coordinates that are
            in the neighborhood of a certain point.

    """

    def __getitem__(self, index):
        return self.grid[index]

    def iter_neighborhood(self, pos,
                          include_center=False, radius=1):
        """ Return an iterator over cell coordinates that are in the
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

        def torus_adj_2d(pos):
            return (pos[0] % self.width, pos[1] % self.height)

        coordinates = set()

        def find_neighbors(pos, radius):
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
                adjacent += [(x - 1, y + 1), (x - 1, y),
                             (x + 1, y + 1), (x + 1, y)]
            else:
                adjacent += [(x - 1, y), (x - 1, y - 1),
                             (x + 1, y), (x + 1, y - 1)]

            if self.torus is False:
                adjacent = list(
                    filter(lambda coords:
                           not self.out_of_bounds(coords), adjacent))
            else:
                adjacent = [torus_adj_2d(coord) for coord in adjacent]

            coordinates.update(adjacent)

            if radius > 1:
                [find_neighbors(coords, radius - 1) for coords in adjacent]

        find_neighbors(pos, radius)

        if not include_center and pos in coordinates:
            coordinates.remove(pos)

        for i in coordinates:
            yield i

    def neighbor_iter(self, pos):
        """ Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.

        """
        neighborhood = self.iter_neighborhood(pos)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighborhood(self, pos,
                         include_center=False, radius=1):
        """ Return a list of cells that are in the neighborhood of a
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

    def iter_neighbors(self, pos,
                       include_center=False, radius=1):
        """ Return an iterator over neighbors to a certain point.

        Args:
            pos: Coordinates for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            An iterator of non-None objects in the given neighborhood

        """
        neighborhood = self.iter_neighborhood(
            pos, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(self, pos,
                      include_center=False, radius=1):
        """ Return a list of neighbors to a certain point.

        Args:
            pos: Coordinate tuple for the neighborhood to get.
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of non-None objects in the given neighborhood

        """
        return list(self.iter_neighbors(
            pos, include_center, radius))


class SingleGrid(Grid):
    """Depreciated class."""

    def __init__(self, width, height, torus):
        super().__init__(width, height, torus, multigrid=False)


class MultiGrid(Grid):
    """Depreciated class."""

    def __init__(self, width, height, torus):
        super().__init__(width, height, torus, multigrid=True)


class ContinuousSpace:
    """ Continuous space where each agent can have an arbitrary position.

    Assumes that all agents are point objects, and have a pos property storing
    their position as an (x, y) tuple. This class uses a numpy array internally
    to store agent objects, to speed up neighborhood lookups.

    """
    _grid = None

    def __init__(self, x_max, y_max, torus, x_min=0, y_min=0):
        """ Create a new continuous space.

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
        self._index_to_agent = {}
        self._agent_to_index = {}

    def place_agent(self, agent, pos):
        """ Place a new agent in the space.

        Args:
            agent: Agent object to place.
            pos: Coordinate tuple for where to place the agent.

        """
        pos = self.torus_adj(pos)
        if self._agent_points is None:
            self._agent_points = np.array([pos])
        else:
            self._agent_points = np.append(
                self._agent_points, np.array([pos]), axis=0)
        self._index_to_agent[self._agent_points.shape[0] - 1] = agent
        self._agent_to_index[agent] = self._agent_points.shape[0] - 1
        agent.pos = pos

    def move_agent(self, agent, pos):
        """ Move an agent from its current position to a new position.

        Args:
            agent: The agent object to move.
            pos: Coordinate tuple to move the agent to.

        """
        pos = self.torus_adj(pos)
        idx = self._agent_to_index[agent]
        self._agent_points[idx, 0] = pos[0]
        self._agent_points[idx, 1] = pos[1]
        agent.pos = pos

    def remove_agent(self, agent):
        """ Remove an agent from the simulation.

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
        deltas = np.abs(self._agent_points - np.array(pos))
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2

        idxs, = np.where(dists <= radius ** 2)
        neighbors = [self._index_to_agent[x]
                     for x in idxs if include_center or dists[x] > 0]
        return neighbors

    def get_heading(self, pos_1, pos_2):
        """ Get the heading angle between two points, accounting for toroidal space.

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

    def get_distance(self, pos_1, pos_2):
        """ Get the distance between two point, accounting for toroidal space.

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
            if isinstance(pos, tuple):
                return (x, y)
            else:
                return np.array((x, y))

    def out_of_bounds(self, pos):
        """ Check if a point is out of bounds. """
        x, y = pos
        return (x < self.x_min or x >= self.x_max or
                y < self.y_min or y >= self.y_max)


class NetworkGrid:
    """ Network Grid where each node contains zero or more agents. """

    def __init__(self, G):
        self.G = G
        for node_id in self.G.nodes:
            G.nodes[node_id]['agent'] = list()

    def place_agent(self, agent, node_id):
        """ Place a agent in a node. """

        self._place_agent(agent, node_id)
        agent.pos = node_id

    def get_neighbors(self, node_id, include_center=False):
        """ Get all adjacent nodes """

        neighbors = list(self.G.neighbors(node_id))
        if include_center:
            neighbors.append(node_id)

        return neighbors

    def move_agent(self, agent, node_id):
        """ Move an agent from its current node to a new node. """

        self._remove_agent(agent, agent.pos)
        self._place_agent(agent, node_id)
        agent.pos = node_id

    def _place_agent(self, agent, node_id):
        """ Place the agent at the correct node. """

        self.G.node[node_id]['agent'].append(agent)

    def _remove_agent(self, agent, node_id):
        """ Remove an agent from a node. """

        self.G.node[node_id]['agent'].remove(agent)

    def is_cell_empty(self, node_id):
        """ Returns a bool of the contents of a cell. """
        return False if self.G.node[node_id]['agent'] else True

    def get_cell_list_contents(self, cell_list):
        return list(self.iter_cell_list_contents(cell_list))

    def get_all_cell_contents(self):
        return list(self.iter_cell_list_contents(self.G))

    def iter_cell_list_contents(self, cell_list):
        list_of_lists = [self.G.node[node_id]['agent']
                         for node_id in cell_list if not self.is_cell_empty(node_id)]
        return [item for sublist in list_of_lists for item in sublist]
