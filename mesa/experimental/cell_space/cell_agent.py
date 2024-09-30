"""An agent with movement methods for cell spaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from mesa.agent import Agent

if TYPE_CHECKING:
    from mesa.experimental.cell_space import Cell


class HasCellProtocol(Protocol):
    """Protocol for discrete space cell holders."""

    cell: Cell


class HasCell:
    """Descriptor for cell movement behavior."""

    _mesa_cell: Cell | None = None

    @property
    def cell(self) -> Cell | None:  # noqa: D102
        return self._mesa_cell

    @cell.setter
    def cell(self, cell: Cell | None) -> None:
        # remove from current cell
        if self.cell is not None:
            self.cell.remove_agent(self)

        # update private attribute
        self._mesa_cell = cell

        # add to new cell
        if cell is not None:
            cell.add_agent(self)


class BasicMovement:
    """Mixin for moving agents in discrete space."""

    def move_to(self: HasCellProtocol, cell: Cell) -> None:
        """Move to a new cell."""
        self.cell = cell

    def move_relative(self: HasCellProtocol, direction: tuple[int, ...]):
        """Move to a cell relative to the current cell.

        Args:
            direction: The direction to move in.
        """
        new_cell = self.cell.connections.get(direction)
        if new_cell is not None:
            self.cell = new_cell
        else:
            raise ValueError(f"No cell in direction {direction}")


class CellAgent(Agent, HasCell, BasicMovement):
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces.

    Attributes:
        cell (Cell): The cell the agent is currently in.
    """

    def remove(self):
        """Remove the agent from the model."""
        super().remove()
        self.cell = None  # ensures that we are also removed from cell


class Grid2DMovingAgent(BasicMovement):
    """Mixin for moving agents in 2D grids."""

    def move(self, direction: str, distance: int = 1):
        """Move the agent in a cardinal direction.

        Args:
            direction: The cardinal direction to move in.
            distance: The distance to move.
        """
        match direction:
            case "N" | "North" | "Up":
                self.move_relative((-1, 0))
            case "S" | "South" | "Down":
                self.move_relative((1, 0))
            case "E" | "East" | "Right":
                self.move_relative((0, 1))
            case "W" | "West" | "Left":
                self.move_relative((0, -1))
            case "NE" | "NorthEast" | "UpRight":
                self.move_relative((-1, 1))
            case "NW" | "NorthWest" | "UpLeft":
                self.move_relative((-1, -1))
            case "SE" | "SouthEast" | "DownRight":
                self.move_relative((1, 1))
            case "SW" | "SouthWest" | "DownLeft":
                self.move_relative((1, -1))
            case _:
                raise ValueError(f"Invalid direction: {direction}")

        for _ in range(distance):
            self.move(direction)
