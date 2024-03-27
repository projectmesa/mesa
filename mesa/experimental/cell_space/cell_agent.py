from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from mesa import Agent, Model

if TYPE_CHECKING:
    from mesa.experimental.cell_space.cell import Cell

T = TypeVar("T", bound=Model)
U = TypeVar("U", bound="CellAgent")


class CellAgent(Agent[T], Generic[T, U]):
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces


    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): The model instance to which the agent belongs
        pos: (Position | None): The position of the agent in the space
        cell: (Cell | None): the cell which the agent occupies
    """

    def __init__(self, unique_id: int, model: T) -> None:
        """
        Create a new agent.

        Args:
            unique_id (int): A unique identifier for this agent.
            model (Model): The model instance in which the agent exists.
        """
        super().__init__(unique_id, model)
        self.cell: Cell[U] | None = None

    def move_to(self, cell: Cell[U]) -> None:
        if self.cell is not None:
            self.cell.remove_agent(self)
        self.cell = cell
        cell.add_agent(self)
