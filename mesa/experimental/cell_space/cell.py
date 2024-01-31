from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from mesa.agent import Agent
from mesa.experimental.cell_space.cell_collection import CellCollection

if TYPE_CHECKING:
    from mesa.experimental.cell_space.cell_agent import CellAgent


class Cell:
    __slots__ = [
        "coordinate",
        "_connections",
        "owner",
        "agents",
        "capacity",
        "properties",
    ]

    def __init__(self, coordinate, owner, capacity: int | None = None) -> None:
        self.coordinate = coordinate
        self._connections: list[Cell] = []  # TODO: change to CellCollection?
        self.agents: dict[
            Agent, None
        ] = {}  # TODO:: change to AgentSet or weakrefs? (neither is very performant, )
        self.capacity = capacity
        self.properties: dict[str, object] = {}
        self.owner = owner

    def connect(self, other) -> None:
        """Connects this cell to another cell."""
        self._connections.append(other)

    def disconnect(self, other) -> None:
        """Disconnects this cell from another cell."""
        self._connections.remove(other)

    def add_agent(self, agent: CellAgent) -> None:
        """Adds an agent to the cell."""
        n = len(self.agents)

        if n == 0:
            self.owner._empties.pop(self.coordinate, None)

        if self.capacity and n >= self.capacity:
            raise Exception(
                "ERROR: Cell is full"
            )  # FIXME we need MESA errors or a proper error

        self.agents[agent] = None

    def remove_agent(self, agent: CellAgent) -> None:
        """Removes an agent from the cell."""
        self.agents.pop(agent, None)
        agent.cell = None
        if len(self.agents) == 0:
            self.owner._empties[self.coordinate] = None

    @property
    def is_empty(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == 0

    @property
    def is_full(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == self.capacity

    def __repr__(self):
        return f"Cell({self.coordinate}, {self.agents})"

    @cache
    def neighborhood(self, radius=1, include_center=False):
        return CellCollection(
            self._neighborhood(radius=radius, include_center=include_center)
        )

    @cache
    def _neighborhood(self, radius=1, include_center=False):
        # if radius == 0:
        #     return {self: self.agents}
        if radius < 1:
            raise ValueError("radius must be larger than one")
        if radius == 1:
            neighborhood = {neighbor: neighbor.agents for neighbor in self._connections}
            if not include_center:
                return neighborhood
            else:
                neighborhood[self] = self.agents
                return neighborhood
        else:
            neighborhood = {}
            for neighbor in self._connections:
                neighborhood.update(
                    neighbor._neighborhood(radius - 1, include_center=True)
                )
            if not include_center:
                neighborhood.pop(self, None)
            return neighborhood
