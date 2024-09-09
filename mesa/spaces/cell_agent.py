"""An agent with movement methods for cell spaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent, Model

if TYPE_CHECKING:
    from mesa.spaces.cell import Cell


class CellAgent(Agent):
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces.

    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): The model instance to which the agent belongs
        pos: (Position | None): The position of the agent in the space
        cell: (Cell | None): the cell which the agent occupies
    """

    def __init__(self, model: Model) -> None:
        """Create a new agent.

        Args:
            model (Model): The model instance in which the agent exists.
        """
        super().__init__(model)
        self.cell: Cell | None = None

    def move_to(self, cell) -> None:
        """Move agent to cell.

        Args:
            cell: cell to which agent is to move

        """
        if self.cell is not None:
            self.cell.remove_agent(self)
        self.cell = cell
        cell.add_agent(self)
