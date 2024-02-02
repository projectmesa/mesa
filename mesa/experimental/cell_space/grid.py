from mesa.experimental.cell_space import Cell, DiscreteSpace
from random import Random

class Grid(DiscreteSpace):
    """Base class for all grid and network classes


    """
    def __init__(
            self,
            width: int,
            height: int,
            torus: bool = False,
            capacity: int | None = None,
            random: Random = None,
            CellKlass: type[Cell] = Cell,
    ) -> None:
        super().__init__(capacity=capacity, random=random, CellKlass=CellKlass)
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
        random: Random = None,
        CellKlass: type[Cell] = Cell
    ) -> None:
        """Orthogonal grid

        Args:
            width (int): width of the grid
            height (int): height of the grid
            torus (bool): whether the space is a torus
            moore (bool): whether the space used Moore or von Neumann neighborhood
            capacity (int): the number of agents that can simultaneously occupy a cell
            random (random):
            CellKlass (type[Cell]): The Cell class to use in the OrthogonalGrid


        """
        super().__init__(width, height, torus, capacity=capacity, CellKlass=CellKlass, random=random)
        self.moore = moore
        self.cells = {
            (i, j): self.CellKlass((i, j), capacity, random=self.random)
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
            self,
            width: int,
            height: int,
            torus: bool = False,
            capacity: int = None,
            random: Random = None,
            CellKlass: type[Cell] = Cell
    ) -> None:
        """Hexagonal Grid

        Args:
            width (int): width of the grid
            height (int): height of the grid
            torus (bool): whether the space is a torus
            capacity (int): the number of agents that can simultaneously occupy a cell
            random (random):
            CellKlass (type[Cell]): The Cell class to use in the HexGrid
        """
        super().__init__(width, height, torus, capacity=capacity, random=random, CellKlass=CellKlass)
        self.cells = {
            (i, j): self.CellKlass((i, j), capacity,  random=self.random)
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
