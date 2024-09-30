"""An agent with movement methods for cell spaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from mesa.experimental.cell_space.discrete_space import DiscreteSpace

if TYPE_CHECKING:
    from mesa.experimental.cell_space import Cell

T = TypeVar("T", bound="Cell")


class DiscreteSpaceAgent(Protocol[T]):
    cell: T | None
    space: DiscreteSpace[T]

    def move_to(self, cell: T) -> None: ...

    def move_relative(self, directions: tuple[int, ...], distance: int = 1): ...


class CellAgent:
    """Cell Agent is an Agent class that adds behavior for moving in discrete spaces

    Attributes:
        space (DiscreteSpace): the discrete space the agent is in
        cell (Cell): the cell the agent is in
    """

    def __init__(
        self,
        space: DiscreteSpace[Cell],
        cell: Cell | None = None,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.space = space
        self.cell = cell
        if cell is not None:
            cell.add_agent(self)

    @property
    def coordinate(self) -> tuple[int, ...]:
        return self.cell.coordinate if self.cell else ()

    def move_to(self, cell: Cell) -> None:
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


class Grid2DMovingAgent:
    def move(self: DiscreteSpaceAgent[Cell], direction: str, distance: int = 1):
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
