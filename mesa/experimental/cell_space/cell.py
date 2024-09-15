"""The Cell in a cell space."""

from __future__ import annotations

from functools import cache
from random import Random
from typing import TYPE_CHECKING

from mesa.experimental.cell_space.cell_collection import CellCollection

if TYPE_CHECKING:
    from mesa.agent import Agent
    from mesa.experimental.cell_space.cell_agent import CellAgent


class Cell:
    """The cell represents a position in a discrete space.

    Attributes:
        coordinate (Tuple[int, int]) : the position of the cell in the discrete space
        agents (List[Agent]): the agents occupying the cell
        capacity (int): the maximum number of agents that can simultaneously occupy the cell
        properties (dict[str, Any]): the properties of the cell
        random (Random): the random number generator

    """

    __slots__ = [
        "coordinate",
        "connections",
        "agents",
        "capacity",
        "properties",
        "random",
    ]

    # def __new__(cls,
    #     coordinate: tuple[int, ...],
    #     capacity: float | None = None,
    #     random: Random | None = None,):
    #     if capacity != 1:
    #         return object.__new__(cls)
    #     else:
    #         return object.__new__(SingleAgentCell)

    def __init__(
        self,
        coordinate: tuple[int, ...],
        capacity: float | None = None,
        random: Random | None = None,
    ) -> None:
        """Initialise the cell.

        Args:
            coordinate: coordinates of the cell
            capacity (int) : the capacity of the cell. If None, the capacity is infinite
            random (Random) : the random number generator to use

        """
        super().__init__()
        self.coordinate = coordinate
        self.connections: dict[str, Cell] = {}
        self.agents: list[
            Agent
        ] = []  # TODO:: change to AgentSet or weakrefs? (neither is very performant, )
        self.capacity = capacity
        self.properties: dict[str, object] = {}
        self.random = random

    def connect(self, other: Cell, name: str | None = None) -> None:
        """Connects this cell to another cell.

        Args:
            other (Cell): other cell to connect to

        """
        if name is None:
            name = str(other.coordinate)
        self.connections.update({name: other})

    def disconnect(self, other: Cell) -> None:
        """Disconnects this cell from another cell.

        Args:
            other (Cell): other cell to remove from connections

        """
        self.connections = {k: v for k, v in self.connections.items() if v != other}

    def add_agent(self, agent: CellAgent) -> None:
        """Adds an agent to the cell.

        Args:
            agent (CellAgent): agent to add to this Cell

        """
        n = len(self.agents)

        if self.capacity and n >= self.capacity:
            raise Exception(
                "ERROR: Cell is full"
            )  # FIXME we need MESA errors or a proper error

        self.agents.append(agent)

    def remove_agent(self, agent: CellAgent) -> None:
        """Removes an agent from the cell.

        Args:
            agent (CellAgent): agent to remove from this cell

        """
        self.agents.remove(agent)
        agent.cell = None

    @property
    def is_empty(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == 0

    @property
    def is_full(self) -> bool:
        """Returns a bool of the contents of a cell."""
        return len(self.agents) == self.capacity

    def __repr__(self):  # noqa
        return f"Cell({self.coordinate}, {self.agents})"

    # FIXME: Revisit caching strategy on methods
    @cache  # noqa: B019
    def neighborhood(self, radius: int = 1, include_center: bool = False):
        """Returns a list of all neighboring cells."""
        return CellCollection[Cell](
            self._neighborhood(radius=radius, include_center=include_center),
            random=self.random,
        )

    # FIXME: Revisit caching strategy on methods
    @cache  # noqa: B019
    def _neighborhood(
        self, radius: int = 1, include_center: bool = False
    ) -> dict[Cell, list[Agent]]:
        # if radius == 0:
        #     return {self: self.agents}
        if radius < 1:
            raise ValueError("radius must be larger than one")
        if radius == 1:
            neighborhood = {
                neighbor: neighbor.agents for neighbor in self.connections.values()
            }
            if not include_center:
                return neighborhood
            else:
                neighborhood[self] = self.agents
                return neighborhood
        else:
            neighborhood: dict[Cell, list[Agent]] = {}
            for neighbor in self.connections.values():
                neighborhood.update(
                    neighbor._neighborhood(radius - 1, include_center=True)
                )
            if not include_center:
                neighborhood.pop(self, None)
            return neighborhood
