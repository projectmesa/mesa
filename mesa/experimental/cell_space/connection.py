from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mesa.experimental.cell_space.cell import Cell

import mesa.experimental.cell_space.cell as _cell


class Connection:
    """An immutable collection of connections"""

    def __init__(self) -> None:
        self._naming: dict[str, int] = {}
        self._reverse_naming: dict[int, str] = {}
        self._connections: list[Cell] = []

    def __len__(self) -> int:
        return len(self._connections)

    def __getitem__(self, key: str | int) -> Cell:
        """Get the specified cell in the list of connections based on id or key

        Arg:
            key (str or int): the specific name or id of the connection

        """
        if isinstance(key, str):
            try:
                conn_id = self._naming[key]
                return self._connections[conn_id]
            except KeyError as e:
                raise KeyError("The connection name is not found.") from e

        if isinstance(key, int):
            try:
                return self._connections[key]
            except IndexError as e:
                raise IndexError("The connection id is out of range.") from e

        raise TypeError(
            f"The connection key must be either str or int, but {type(key)} is found."
        )

    def __contains__(self, key: Cell | str | int) -> Cell:
        """Get the specified cell in the list of connections based on id or key

        Arg:
            key (str or int): the specific name or id of the connection

        """
        if isinstance(key, str):
            return key in self._naming

        if isinstance(key, int):
            return key in range(len(self._connections))

        if isinstance(key, _cell.Cell):
            return key in self._connections

        raise TypeError(
            f"The connection key must be either Cell or str or int, but {type(key)} is found."
        )

    def append(self, cell: Cell, name: str | None = None) -> None:
        """Add the new connection to the list of connections with an optional name

        Arg:
            cell (Cell): the cell to add to the list of connections
            name (str, optional): the name of the connection

        """
        if name is None:
            self._connections.append(cell)
            return

        if name in self._naming:
            raise ValueError("The connection key has already existed!")

        conn_idx = len(self._connections)
        self._naming[name] = conn_idx
        self._reverse_naming[conn_idx] = name
        self._connections.append(cell)

    def remove(self, cell: Cell | str | int) -> None:
        """Remove a connection from the list of connections

        Arg:
            cell (Cell or str or int): the cell to add to the list of connections, it can be either a Cell object or a connection name or a connection index

        """
        if isinstance(cell, _cell.Cell):
            conn_idx = self._connections.index(cell)
            self._connections.pop(conn_idx)
            if conn_idx in self._reverse_naming:
                conn_name = self._reverse_naming[conn_idx]
                del self._naming[conn_name]
                del self._reverse_naming[conn_idx]
            return

        if isinstance(cell, str):
            if cell not in self._naming:
                raise ValueError("The connection same does not exist!")

            conn_idx = self._naming[cell]
            self._connections.pop(conn_idx)
            del self._naming[cell]
            del self._reverse_naming[conn_idx]
            return

        if isinstance(cell, int):
            if cell not in range(len(self._connections)):
                raise ValueError("Connection index out of range!")
            self._connections.pop(cell)
            if cell in self._reverse_naming:
                conn_name = self._reverse_naming[cell]
                del self._naming[conn_name]
                del self._reverse_naming[cell]
            return

        raise TypeError(
            f"The argument must be either Cell or str or int, but {type(cell)} is found."
        )
