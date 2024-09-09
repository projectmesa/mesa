"""CellCollection class."""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Mapping
from functools import cached_property
from random import Random
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from mesa.spaces.cell import Cell
    from mesa.spaces.cell_agent import CellAgent

T = TypeVar("T", bound="Cell")


class CellCollection(Generic[T]):
    """An immutable collection of cells.

    Attributes:
        cells (List[Cell]): The list of cells this collection represents
        agents (List[CellAgent]) : List of agents occupying the cells in this collection
        random (Random) : The random number generator

    """

    def __init__(
        self,
        cells: Mapping[T, list[CellAgent]] | Iterable[T],
        random: Random | None = None,
    ) -> None:
        """Initialize a CellCollection.

        Args:
            cells: cells to add to the collection
            random: a seeded random number generator.
        """
        if isinstance(cells, dict):
            self._cells = cells
        else:
            self._cells = {cell: cell.agents for cell in cells}

        #
        self._capacity: int = next(iter(self._cells.keys())).capacity

        if random is None:
            random = Random()  # FIXME
        self.random = random

    def __iter__(self):  # noqa
        return iter(self._cells)

    def __getitem__(self, key: T) -> Iterable[CellAgent]:  # noqa
        return self._cells[key]

    # @cached_property
    def __len__(self) -> int:  # noqa
        return len(self._cells)

    def __repr__(self):  # noqa
        return f"CellCollection({self._cells})"

    @cached_property
    def cells(self) -> list[T]:  # noqa
        return list(self._cells.keys())

    @property
    def agents(self) -> Iterable[CellAgent]:  # noqa
        return itertools.chain.from_iterable(self._cells.values())

    def select_random_cell(self) -> T:
        """Select a random cell."""
        return self.random.choice(self.cells)

    def select_random_agent(self) -> CellAgent:
        """Select a random agent.

        Returns:
            CellAgent instance


        """
        return self.random.choice(list(self.agents))

    def select(self, filter_func: Callable[[T], bool] | None = None, n=0):
        """Select cells based on filter function.

        Args:
            filter_func: filter function
            n: number of cells to select

        Returns:
            CellCollection

        """
        # FIXME: n is not considered
        if filter_func is None and n == 0:
            return self

        return CellCollection(
            {
                cell: agents
                for cell, agents in self._cells.items()
                if filter_func is None or filter_func(cell)
            }
        )
