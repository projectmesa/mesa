"""The Cell in a cell space."""

from __future__ import annotations

from collections.abc import Callable
from functools import cache, cached_property
from random import Random
from typing import TYPE_CHECKING, Any

from mesa.experimental.cell_space.cell_agent import CellAgent
from mesa.experimental.cell_space.cell_collection import CellCollection
from mesa.space import PropertyLayer

if TYPE_CHECKING:
    from mesa.agent import Agent

Coordinate = tuple[int, ...]


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
        "_mesa_property_layers",
        "__dict__",
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
        coordinate: Coordinate,
        capacity: int | None = None,
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
        self.connections: dict[Coordinate, Cell] = {}
        self.agents: list[
            Agent
        ] = []  # TODO:: change to AgentSet or weakrefs? (neither is very performant, )
        self.capacity: int | None = capacity
        self.properties: dict[Coordinate, object] = {}
        self.random = random
        self._mesa_property_layers: dict[str, PropertyLayer] = {}

    def connect(self, other: Cell, key: Coordinate | None = None) -> None:
        """Connects this cell to another cell.

        Args:
            other (Cell): other cell to connect to
            key (Tuple[int, ...]): key for the connection. Should resemble a relative coordinate

        """
        if key is None:
            key = other.coordinate
        self.connections[key] = other

    def disconnect(self, other: Cell) -> None:
        """Disconnects this cell from another cell.

        Args:
            other (Cell): other cell to remove from connections

        """
        keys_to_remove = [k for k, v in self.connections.items() if v == other]
        for key in keys_to_remove:
            del self.connections[key]

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

    @cached_property
    def neighborhood(self) -> CellCollection[Cell]:
        """Returns the direct neighborhood of the cell.

        This is equivalent to cell.get_neighborhood(radius=1)

        """
        return self.get_neighborhood()

    # FIXME: Revisit caching strategy on methods
    @cache  # noqa: B019
    def get_neighborhood(
        self, radius: int = 1, include_center: bool = False
    ) -> CellCollection[Cell]:
        """Returns a list of all neighboring cells for the given radius.

        For getting the direct neighborhood (i.e., radius=1) you can also use
        the `neighborhood` property.

        Args:
            radius (int): the radius of the neighborhood
            include_center (bool): include the center of the neighborhood

        Returns:
            a list of all neighboring cells

        """
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

    # PropertyLayer methods
    def get_property(self, property_name: str) -> Any:
        """Get the value of a property."""
        return self._mesa_property_layers[property_name].data[self.coordinate]

    def set_property(self, property_name: str, value: Any):
        """Set the value of a property."""
        self._mesa_property_layers[property_name].set_cell(self.coordinate, value)

    def modify_property(
        self, property_name: str, operation: Callable, value: Any = None
    ):
        """Modify the value of a property."""
        self._mesa_property_layers[property_name].modify_cell(
            self.coordinate, operation, value
        )

    def __getstate__(self):
        """Return state of the Cell with connections set to empty."""
        # fixme, once we shift to 3.11, replace this with super. __getstate__
        state = (self.__dict__, {k: getattr(self, k) for k in self.__slots__})
        state[1][
            "connections"
        ] = {}  # replace this with empty connections to avoid infinite recursion error in pickle/deepcopy
        return state
