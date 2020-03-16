from .grid import Grid


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

    def iter_neighborhood(self, pos, include_center=False, radius=1):
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

        for i in coordinates:
            yield i

    def neighbor_iter(self, pos):
        """ Iterate over position neighbors.

        Args:
            pos: (x,y) coords tuple for the position to get the neighbors of.

        """
        neighborhood = self.iter_neighborhood(pos)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighborhood(self, pos, include_center=False, radius=1):
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

    def iter_neighbors(self, pos, include_center=False, radius=1):
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
        neighborhood = self.iter_neighborhood(pos, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    def get_neighbors(self, pos, include_center=False, radius=1):
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
        return list(self.iter_neighbors(pos, include_center, radius))
