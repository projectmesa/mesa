from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from mesa.experimental.cell_space.discrete_space import DiscreteSpace

if TYPE_CHECKING:
    from mesa.experimental.cell_space import Cell, Grid


@runtime_checkable
class CellHolder(Protocol):
    cell: Cell | None


class CellAgent:
    cell: Cell | None
    space: DiscreteSpace[Cell]
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces"""

    def move_to(self: CellHolder, cell: Cell) -> None:
        if self.cell is not None:
            self.cell.remove_agent(self)
        self.cell = cell
        cell.add_agent(self)

    def move_relative(self, directions: tuple[int, ...], distance: int = 1):
        new_position = tuple(
            self.cell.coordinate[i] + directions[i] * distance
            for i in range(len(directions))
            if self.cell
        )
        new_cell = self.space[new_position]
        self.move_to(new_cell)


class Grid2DMovingAgent(CellAgent):
    grid: Grid[Cell]

    def move(self, direction: str, distance: int = 1):
        match direction:
            case "N" | "North" | "Up":
                self.move_relative((-1, 0), distance)
            case "S" | "South" | "Down":
                self.move_relative((1, 0), distance)
            case "E" | "East" | "Right":
                self.move_relative((0, 1), distance)
            case "W" | "West" | "Left":
                self.move_relative((0, -1), distance)
            case "NE" | "NorthEast" | "UpRight":
                self.move_relative((-1, 1), distance)
            case "NW" | "NorthWest" | "UpLeft":
                self.move_relative((-1, -1), distance)
            case "SE" | "SouthEast" | "DownRight":
                self.move_relative((1, 1), distance)
            case "SW" | "SouthWest" | "DownLeft":
                self.move_relative((1, -1), distance)
            case _:
                raise ValueError(f"Invalid direction: {direction}")
