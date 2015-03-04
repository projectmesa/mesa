'''
Mesa Space Module
=================================

Objects used to add a spatial component to a model.

Grid: base grid, a simple list-of-lists.

MultiGrid: extension to Grid where each cell is a set of objects.

'''
# Instruction for PyLint to suppress variable name errors, since we have a
# good reason to use one-character variable names for x and y.
# pylint: disable=invalid-name

import itertools


class Grid(object):
    '''
    Base class for a square grid.

    Grid cells are indexed by [y][x], where [0][0] is assumed to be the top-left
    and [height-1][width-1] is the bottom-right. If a grid is toroidal, the top
    and bottom, and left and right, edges wrap to each other

    Properties:
        width, height: The grid's width and height.
        torus: Boolean which determines whether to treat the grid as a torus.

        grid: Internal list-of-lists which holds the grid cells themselves.
        default_val: Lambda function to populate each grid cell with None.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
        get_neighborhood: Returns the cells surrounding a given cell.
        get_cell_list_contents: Returns the contents of a list of cells ((x,y) tuples)
    '''

    default_val = lambda s: None


    class GridOccupiedIter:
        """
        Return just the (un)occupied cells of the grid.
        occupied is a flag indicating if we want the occupied (True)
            or unoccupied (occupied=False) cells
        """

        def __init__(self, grid, occupied=True):
            self.grid = grid
            self.x = 0
            self.y = 0
            self.occupied = occupied


        def __iter__(self):
            return self


        def __next__(self):
            while self.y < self.grid.height:
                while self.x < self.grid.width:
                    occupied = not self.grid.is_cell_empty((self.x, self.y))
                    if occupied == self.occupied:
                        ret = [self.grid[self.y][self.x],
                              self.x, self.y]
                        self.x += 1
                        return ret
                    else:
                        self.x += 1
                self.x = 0
                self.y += 1
            else:
                raise StopIteration()


    def __init__(self, height, width, torus):
        '''
        Create a new grid.

        Args:
            height, width: The height and width of the grid
            torus: Boolean whether the grid wraps or not.
        '''
        self.height = height
        self.width = width
        self.torus = torus

        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(self.default_val())
            self.grid.append(row)

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        # create an iterator that chains the
        #  rows of grid together as if one list:
        return itertools.chain(*self.grid)


    def occupied_iter(self, occupied=True):
        return Grid.GridOccupiedIter(self, occupied=occupied)

    def torus_adj(self, coord, dim_len):
        """
        Convert coordinate, handling torus looping.
        """
        if self.torus:
            coord %= dim_len
        return coord


    def out_of_bounds(self, x, y):
        """
        Is point x, y off the grid?
        """
        return(x < 0 or x >= self.width
           or y < 0 or y >= self.height)


    def get_neighborhood(self, x, y, moore,
                         include_center=False, radius=1):
        """
        Return a list of cells that are in the 
        neighborhood of a certain point.

        Args:
            x, y: Coordinates for the neighborhood to get.
            moore: If True, return Moore neighborhood
                        (including diagonals)
                   If False, return Von Neumann neighborhood 
                        (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the neighborhood;
                With radius 1, at most 9 if
                Moore, 5 if Von Neumann
                (8 and 4 if not including the center).
        """
        coordinates = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0 and not include_center:
                    continue
                if not moore:
                    # Skip diagonals in Von Neumann neighborhood.
                    if dy != 0 and dx != 0:
                        continue

                px = self.torus_adj(x + dx, self.width)
                py = self.torus_adj(y + dy, self.height)

                # Skip if new coords out of bounds.
                if(self.out_of_bounds(px, py)):
                    continue

                coordinates.append((px, py))
        return coordinates


    def get_neighbors(self, x, y, moore, include_center=False, radius=1):
        '''
        Return a list of neighbors to a certain point.

        Args:
            x, y: Coordinates for the neighborhood to get.
            moore: If True, return Moore neighborhood (including diagonals)
                   If False, return Von Neumann neighborhood (exclude diagonals)
            include_center: If True, return the (x, y) cell as well. Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of non-None objects in the given neighborhood; at most 9 if
            Moore, 5 if Von-Neumann (8 and 4 if not including the center).
        '''
        neighborhood = self.get_neighborhood(x, y, moore, include_center, radius)
        return self.get_cell_list_contents(neighborhood)

    def get_cell_list_contents(self, cell_list):
        '''
        Args:
            cell_list: Array-like of (x, y) tuples

        Returns:
            A list of the contents of the cells identified in cell_list
        '''
        contents = []
        for x, y in cell_list:
            self._add_members(contents, x, y)
        return contents

    def _add_members(self, target_list, x, y):
        '''
        Helper method to append the contents of a cell to the given list.
        Override for other grid types.
        '''
        if self.grid[y][x] is not None:
            target_list.append(self.grid[y][x])

    def is_cell_empty(self, coords):
        x, y = coords
        return True if self.grid[y][x] is None else False


class MultiGrid(Grid):
    '''
    Grid where each cell can contain more than one object.

    Grid cells are indexed by [y][x], where [0][0] is assumed to be the top-left
    and [height-1][width-1] is the bottom-right. If a grid is toroidal, the top
    and bottom, and left and right, edges wrap to each other.

    Each grid cell holds a set object.

    Properties:
        width, height: The grid's width and height.

        torus: Boolean which determines whether to treat the grid as a torus.

        grid: Internal list-of-lists which holds the grid cells themselves.
        default_val: Lambda function to populate grid cells with an empty set.

    Methods:
        get_neighbors: Returns the objects surrounding a given cell.
    '''

    default_val = lambda s: set()

    def _add_members(self, target_list, x, y):
        '''
        Helper method to add all objects in the given cell to the target_list.
        '''
        for a in self.grid[y][x]:
            target_list.append(a)

