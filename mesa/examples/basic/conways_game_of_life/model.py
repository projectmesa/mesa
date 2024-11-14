from mesa import Model
from mesa.examples.basic.conways_game_of_life.agents import Cell
from mesa.space import SingleGrid


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed)
        # Use a simple grid, where edges wrap around.
        self.grid = SingleGrid(width, height, torus=True)

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for _contents, (x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self)
            if self.random.random() < initial_fraction_alive:
                cell.state = cell.ALIVE
            self.grid.place_agent(cell, (x, y))

        self.running = True

    def step(self):
        """Perform the model step in two stages:
        - First, all cells assume their next state (whether they will be dead or alive)
        - Then, all cells change state to their next state.
        """
        self.agents.do("determine_state")
        self.agents.do("assume_state")
