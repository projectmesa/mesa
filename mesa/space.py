'''
Mesa Space Module
=================================

Objects used to add a spatial component to a model. 

Grid: base grid, a simple list-of-lists. 

MultiGrid: extension to Grid where each cell is a set of objects.

'''

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

	Methods:
		get_neighbors: Returns the objects surrounding a given cell.
	'''

	width = None
	height = None
	torus = False
	grid = None

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
				row.append(None)
			self.grid.append(row)

	def __getitem__(self, index):
		return self.grid[index]

	def _get_x(self, x):
		'''
		Convert X coordinate, handling torus looping.
		'''
		if x >= 0 and x < self.width:
			return x
		if not self.torus:
			raise Exception("Coordinate out of bounds.")
		else:
			return x % self.width

	def _get_y(self, y):
		'''
		Convert Y coordinate, handling torus looping.
		'''
		if y >= 0 and y < self.height:
			return y
		if not self.torus:
			raise Exception("Coordinate out of bounds.")
		else:
			return y % self.height

	def get_neighbors(self, x, y, moore, include_center=False):
		'''
		Return a list of neighbors to a certain point.

		Args:
			x, y: Coordinates for the neighborhood to get.
			moore: If True, return Moore neighborhood (including diagonals)
				   If False, return Von Neumann neighborhood (exclude diagonals)
			include_center: If True, return the (x, y) cell as well. Otherwise,
							return surrounding cells only.

		Returns:
			A list of non-None objects in the given neighborhood; at most 9 if 
			Moore, 5 if Von-Neumann (8 and 4 if not including the center).
		'''
		neighbors = []
		for dy in [-1, 0, 1]:
			for dx in [-1, 0, 1]:
				if dx == 0 and dy == 0 and not include_center: continue
				if not moore and dy != 0 and dx != 0: continue
				px = self._get_x(x + dx)
				py = self._get_y(y + dy)
				if self.grid[py][px] is not None:
					neighbors.append(self.grid[py][px])
		return neighbors




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

	Methods:
		get_neighbors: Returns the objects surrounding a given cell.
	'''

	width = None
	height = None
	torus = False
	grid = None

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
				row.append(set())
			self.grid.append(row)

	def __getitem__(self, index):
		return self.grid[index]

	def get_neighbors(self, x, y, moore, include_center=False):
		'''
		Return a list of neighbors to a certain point.

		Args:
			x, y: Coordinates for the neighborhood to get.
			moore: If True, return Moore neighborhood (including diagonals)
				   If False, return Von Neumann neighborhood (exclude diagonals)
			include_center: If True, return the (x, y) cell as well. Otherwise,
							return surrounding cells only.

		Returns:
			A list of non-None objects in the given neighborhood; at most 9 if 
			Moore, 5 if Von-Neumann (8 and 4 if not including the center).
		'''
		neighbors = []
		for dy in [-1, 0, 1]:
			for dx in [-1, 0, 1]:
				if dx == 0 and dy == 0 and not include_center: continue
				if not moore and dy != 0 and dx != 0: continue
				px = self._get_x(x + dx)
				py = self._get_y(y + dy)
				for a in self.grid[py][px]:
					neighbors.append(a)
		return neighbors



