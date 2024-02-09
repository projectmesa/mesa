from random import Random

from mesa.experimental.cell_space import Cell, DiscreteSpace


class Grid(DiscreteSpace):
    """Base class for all grid and network classes

    Attributes:
        width (int): width of the grid
        height (int): height of the grid
        torus (bool): whether the grid is a torus
        _try_random (bool): whether to get empty cell be repeatedly trying random cell

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
        self._try_random = True

    def select_random_empty_cell(self) -> Cell:
        # FIXME:: currently just a simple boolean to control behavior
        # FIXME:: basically if grid is close to 99% full, creating empty list can be faster
        # FIXME:: note however that the old results don't apply because in this implementation
        # FIXME:: because empties list needs to be rebuild each time
        # This method is based on Agents.jl's random_empty() implementation. See
        # https://github.com/JuliaDynamics/Agents.jl/pull/541. For the discussion, see
        # https://github.com/projectmesa/mesa/issues/1052 and
        # https://github.com/projectmesa/mesa/pull/1565. The cutoff value provided
        # is the break-even comparison with the time taken in the else branching point.
        if self._try_random:
            while True:
                cell = self.all_cells.select_random_cell()
                if cell.is_empty:
                    return cell
        else:
            return super().select_random_empty_cell()


class OrthogonalGrid(Grid):
    def __init__(
        self,
        width: int,
        height: int,
        torus: bool = False,
        moore: bool = True,
        capacity: int | None = None,
        random: Random = None,
        CellKlass: type[Cell] = Cell,
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
        super().__init__(
            width, height, torus, capacity=capacity, CellKlass=CellKlass, random=random
        )
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
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1),
            ]
        else:  # Von Neumann neighborhood
            directions = [
                (-1, 0),
                (0, -1), (0, 1),
                (1, 0),
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
        CellKlass: type[Cell] = Cell,
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
        super().__init__(
            width, height, torus, capacity=capacity, random=random, CellKlass=CellKlass
        )
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
        if i % 2 == 0:
            directions = [
                (-1, -1), (-1, 0),
                (0, -1), (0, 1),
                (1, -1), (1, 0),
            ]
        else:
            directions = [
                (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, 0), (1, 1),
            ]
        # fmt: on

        for di, dj in directions:
            ni, nj = (i + di, j + dj)
            if self.torus:
                ni, nj = ni % self.height, nj % self.width
            if 0 <= ni < self.height and 0 <= nj < self.width:
                cell.connect(self.cells[ni, nj])
