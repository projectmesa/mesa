"""An agent with movement methods for cell spaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:
    from mesa.experimental.cell_space.cell import Cell


class CellDescriptor:
    """Descriptor for cell movement behavior."""

    def __get__(self, instance, owner):  # noqa D105
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):  # noqa D105
        if instance.cell is not None:
            instance.cell.remove_agent(self)
        setattr(instance, self.private_name, value)

        if value is not None:
            value.add_agent(self)

    def __set_name__(self, owner, name):  # noqa D105
        self.public_name = name
        self.private_name = "_" + name


class CellAgent(Agent):
    """Cell Agent is an extension of the Agent class and adds behavior for moving in discrete spaces.

    Attributes:
        unique_id (int): A unique identifier for this agent.
        model (Model): The model instance to which the agent belongs
        pos: (Position | None): The position of the agent in the space
        cell: (Cell | None): the cell which the agent occupies
    """

    cell: Cell = CellDescriptor()
