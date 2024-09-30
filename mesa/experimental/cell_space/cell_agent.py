"""An agent with movement methods for cell spaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:
    from mesa.experimental.cell_space.cell import Cell


class HasCell:
    """Descriptor for cell movement behavior."""

    _mesa_cell: Cell = None

    @property
    def cell(self) -> Cell | None:
        return getattr(self, "_mesa_cell", None)

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


class CellAgent(Agent, HasCell):
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces.

    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): The model instance to which the agent belongs
        pos: (Position | None): The position of the agent in the space
        cell: (Cell | None): the cell which the agent occupies
    """

    def remove(self):
        """Remove the agent from the model."""
        super().remove()
        self.cell = None  # ensures that we are also removed from cell
