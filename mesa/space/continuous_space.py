import numpy as np


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
            self._agent_points = np.append(self._agent_points, np.array([pos]), axis=0)
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

        (idxs,) = np.where(dists <= radius ** 2)
        neighbors = [
            self._index_to_agent[x] for x in idxs if include_center or dists[x] > 0
        ]
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
        return x < self.x_min or x >= self.x_max or y < self.y_min or y >= self.y_max
