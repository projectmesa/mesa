"""Frames: coordinate systems shared by one or more spaces.

A frame is a coordinate system with a meaning, such as "physical" or "opinion".
Spaces index a frame in their own way (continuous coordinates, grid cells, Voronoi
regions), and an agent has at most one occupying location per frame. No space has
authority over that location: a write through any member space is converted to
frame coordinates and applied to the agent's other member spaces exactly once.

Spaces take part through a small internal protocol:

- ``_resolve(point)`` returns the space's representation of a frame point (a cell
  for discrete spaces) or raises if the point has none.
- ``_owns(cell)`` tells whether a cell belongs to the space.
- Continuous spaces additionally expose ``in_bounds`` and their position array.

This module deliberately imports nothing from the space packages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from mesa.agent import Agent

__all__ = ["Frame"]


class _Record:
    """The location of one agent in one frame.

    Attributes:
        agent: the agent
        frame: the frame
        cells: the agent's cell in each discrete member space
        continuous: the continuous member space, if any
        holder: the object carrying ``_mesa_index`` for the continuous space
        cell: the last-written value, if it was a cell
        point: the last-written value, if it was a point and no continuous space stores it
        home: the discrete space mirrored by ``agent.cell``, if any
    """

    __slots__ = (
        "_mesa_index",
        "agent",
        "cell",
        "cells",
        "continuous",
        "frame",
        "holder",
        "home",
        "point",
    )

    def __init__(self, agent: Agent, frame: Frame) -> None:
        self.agent = agent
        self.frame = frame
        self.cells: dict[Any, Any] = {}
        self.continuous = None
        self.holder = None
        self.cell = None
        self.point = None
        self.home = None
        self._mesa_index = None

    @property
    def is_empty(self) -> bool:
        return not self.cells and self.continuous is None

    def location(self) -> np.ndarray | None:
        """Return the agent's location in frame coordinates."""
        if self.continuous is not None:
            return self.continuous._positions_ro[self.holder._mesa_index]
        if self.cell is not None:
            return np.asarray(self.cell.position, dtype=float)
        return self.point


def set_cell(agent: Agent, cell) -> None:
    """Handle ``agent.cell = cell`` for a cell agent that has frame records.

    ``agent.cell`` refers to one discrete space, the agent's home. While the agent
    has a home, only cells of that space can be assigned; other spaces are written
    through ``space.move``.
    """
    records = agent._mesa_locations.values()
    home_record = next((r for r in records if r.home is not None), None)

    if home_record is not None:
        home = home_record.home
        if cell is None:
            home_record.frame._leave(home_record, home)
        elif home._owns(cell):
            home_record.frame._write(home_record, home, cell)
        else:
            raise ValueError(
                f"agent.cell moves the agent within its {type(home).__name__}; "
                "use space.move(agent, cell) to move it by a cell of another space."
            )
        return

    old = agent._mesa_cell
    if cell is not None:
        for record in records:
            space = next((s for s in record.frame.spaces if s._owns(cell)), None)
            if space is None:
                continue
            if space in record.cells:
                record.frame._write(record, space, cell)
            else:
                record.frame._enter_discrete(record, space, cell)
            record.home = space
            break
        else:
            # A cell of a frame the agent has no record in: single-space behavior
            cell.add_agent(agent)
    if old is not None:
        old.remove_agent(agent)
    agent._mesa_cell = cell


class Frame:
    """A coordinate system that one or more spaces index.

    Args:
        name: the meaning of the frame, e.g. ``"physical"``. Used by
            :class:`~mesa.experimental.frames.Location` to find the frame.
        ndim: the number of dimensions. Taken from the first space if omitted.

    Attributes:
        spaces: the spaces indexing this frame
        torus: whether the frame wraps; set by the first space that joins
        bounds: the wrapping extent as ``[[min, max], ...]``; only set for a torus

    Notes:
        Create frames per model instance, typically in ``Model.__init__``. A frame
        keeps references to its spaces, so sharing one across models leaks state.
    """

    def __init__(self, name: str | None = None, ndim: int | None = None) -> None:
        """Create a frame."""
        self.name = name
        self.ndim = ndim
        self.torus: bool | None = None
        self.bounds: np.ndarray | None = None
        self.spaces: list = []

    @property
    def key(self):
        """The key under which agents store their location in this frame."""
        return self if self.name is None else self.name

    def __repr__(self) -> str:  # noqa: D105
        return f"Frame({self.name!r}, ndim={self.ndim})"

    # ------------------------------------------------------------------
    # spaces
    # ------------------------------------------------------------------
    def _join(self, space, ndim: int | None, torus: bool = False, bounds=None) -> None:
        """Register a space, checking that it is compatible with the frame."""
        if ndim is not None:
            if self.ndim is None:
                self.ndim = ndim
            elif self.ndim != ndim:
                raise ValueError(
                    f"{type(space).__name__} has {ndim} dimensions, but {self!r} has {self.ndim}."
                )
        # Only a torus needs its extent, to wrap points the same way in every space
        bounds = np.asarray(bounds, dtype=float) if torus else None
        if not self.spaces:
            self.torus = torus
            self.bounds = bounds
        elif torus != self.torus:
            raise ValueError(
                f"All spaces in {self!r} must agree on torus; got torus={torus} "
                f"for {type(space).__name__} while the frame has torus={self.torus}."
            )
        elif torus and not np.allclose(bounds, self.bounds):
            raise ValueError(
                f"Spaces in the torus {self!r} must cover the same extent; "
                f"{type(space).__name__} covers {bounds.tolist()}, the frame {self.bounds.tolist()}."
            )
        self.spaces.append(space)

    # ------------------------------------------------------------------
    # records
    # ------------------------------------------------------------------
    def _lookup(self, agent: Agent) -> _Record | None:
        locations = agent._mesa_locations
        if locations is None:
            return None
        record = locations.get(self.key)
        if record is not None and record.frame is not self:
            raise ValueError(
                f"Agent {agent.unique_id} is already located in another frame named {self.name!r}."
            )
        return record

    def _record(self, agent: Agent) -> _Record:
        """Return the agent's record, creating it from single-space state if needed."""
        record = self._lookup(agent)
        if record is not None:
            return record

        record = _Record(agent, self)
        # Adopt the location of a CellAgent or ContinuousSpaceAgent
        cell = getattr(agent, "_mesa_cell", None)
        if cell is not None:
            for space in self.spaces:
                if space._owns(cell):
                    record.cells[space] = record.cell = cell
                    record.home = space
                    break
        if getattr(agent, "_mesa_index", None) is not None:
            space = agent.space
            if any(space is member for member in self.spaces):
                record.continuous = space
                record.holder = agent
                record.cell = None
        return record

    def _attach(self, record: _Record) -> None:
        agent = record.agent
        if agent._mesa_locations is None:
            agent._mesa_locations = {}
        agent._mesa_locations[self.key] = record
        if record.holder is agent:
            agent._mesa_stack = record

    @staticmethod
    def _check_movable(agent: Agent) -> None:
        if getattr(agent, "_mesa_fixed", False):
            raise TypeError(
                f"{type(agent).__name__} is fixed to its cell and cannot be in several spaces of a frame."
            )

    def _ensure_attached(self, record: _Record) -> None:
        locations = record.agent._mesa_locations
        if locations is None or locations.get(self.key) is not record:
            self._attach(record)

    def _detach(self, record: _Record) -> None:
        agent = record.agent
        locations = agent._mesa_locations
        if locations is not None and locations.get(self.key) is record:
            del locations[self.key]
            if not locations:
                agent._mesa_locations = None
        if getattr(agent, "_mesa_stack", None) is record:
            agent._mesa_stack = None

    # ------------------------------------------------------------------
    # writes
    # ------------------------------------------------------------------
    def _normalize(self, point) -> np.ndarray:
        point = np.array(point, dtype=float)
        if self.ndim is not None and point.shape != (self.ndim,):
            raise ValueError(
                f"Expected a point with {self.ndim} coordinates in {self!r}, got {point.tolist()}."
            )
        if self.torus:
            lower = self.bounds[:, 0]
            point = lower + np.mod(point - lower, self.bounds[:, 1] - lower)
        return point

    def _write(self, record: _Record, source, value) -> None:
        """Move an agent, updating all its member spaces or none.

        Args:
            record: the agent's record in this frame
            source: the discrete space ``value`` is a cell of, or None for a point
            value: a cell of ``source``, or a point in frame coordinates
        """
        agent = record.agent
        # The position of a cell is already a point of the frame
        point = None if source is not None else self._normalize(value)

        # 1. Resolve the target in every member space. Nothing is mutated yet.
        cells = record.cells
        targets = {}
        for space in cells:
            if space is source:
                targets[space] = value
            else:
                if point is None:
                    point = np.asarray(value.position, dtype=float)
                targets[space] = space._resolve(point)
        continuous = record.continuous
        if continuous is not None:
            if point is None:
                point = np.asarray(value.position, dtype=float)
            # In a torus every space covers the whole frame, so any point fits
            if not self.torus and not continuous.in_bounds(point):
                raise ValueError(
                    f"point {point.tolist()} is outside the bounds of the space"
                )

        # 2. Enter the new cells, rolling back if one of them is full.
        entered = []
        try:
            for space, cell in targets.items():
                if cell is not cells[space]:
                    cell.add_agent(agent)
                    entered.append(cell)
        except Exception:
            for cell in entered:
                cell.remove_agent(agent)
            raise

        # 3. Commit. Nothing below can fail.
        for space, cell in targets.items():
            old = cells[space]
            if cell is not old:
                if old is not None:
                    old.remove_agent(agent)
                cells[space] = cell
        if continuous is not None:
            continuous._agent_positions[record.holder._mesa_index] = point
            record.cell = record.point = None
        elif source is not None:
            record.cell, record.point = value, None
        else:
            point.flags.writeable = False
            record.cell, record.point = None, point
        if record.home is not None:
            agent._mesa_cell = cells[record.home]

    def _enter_discrete(self, record: _Record, space, cell=None) -> None:
        """Add the agent to a discrete space, at a cell or at its current location."""
        if space in record.cells:
            raise ValueError(
                f"Agent {record.agent.unique_id} is already in this {type(space).__name__}."
            )
        self._check_movable(record.agent)
        new = record.is_empty
        if cell is None:
            if new:
                raise ValueError(
                    f"Agent {record.agent.unique_id} has no location in {self!r} yet; pass a cell."
                )
            cell = space._resolve(record.location())
            cell.add_agent(record.agent)
            record.cells[space] = cell
        elif new:
            cell.add_agent(record.agent)
            record.cells[space] = record.cell = cell
        else:
            record.cells[space] = None
            try:
                self._write(record, space, cell)
            except Exception:
                del record.cells[space]
                raise
        self._ensure_attached(record)

    def _enter_continuous(self, record: _Record, space, point=None) -> None:
        """Add the agent to a continuous space, at a point or at its current location."""
        if record.continuous is not None:
            raise ValueError(
                f"Agent {record.agent.unique_id} is already in a continuous space in {self!r}."
            )
        self._check_movable(record.agent)
        new = record.is_empty
        if point is None:
            if new:
                raise ValueError(
                    f"Agent {record.agent.unique_id} has no location in {self!r} yet; pass a position."
                )
            current = record.location()
        else:
            current = self._normalize(point)
        if not space.in_bounds(current):
            raise ValueError(
                f"point {current.tolist()} is outside the bounds of the space"
            )

        space._add_agent(record.agent, holder=record)
        space._agent_positions[record._mesa_index] = current
        record.continuous, record.holder = space, record
        if point is not None and not new:
            try:
                self._write(record, None, current)
            except Exception:
                space._remove_agent(record.agent)
                record.continuous = record.holder = None
                raise
        record.cell = record.point = None
        self._ensure_attached(record)

    def _leave(self, record: _Record, space) -> None:
        """Remove the agent from one space, keeping its location in the frame."""
        agent = record.agent
        if space is record.continuous:
            if record.holder is not record:
                raise ValueError(
                    "A ContinuousSpaceAgent cannot leave its space; use agent.remove()."
                )
            point = np.array(record.location())
            point.flags.writeable = False
            space._remove_agent(agent)
            record.continuous = record.holder = None
            record.point = point
        else:
            cell = record.cells.pop(space)
            cell.remove_agent(agent)
            if record.cell is cell:
                point = np.array(cell.position, dtype=float)
                point.flags.writeable = False
                record.cell, record.point = None, point
            if space is record.home:
                record.home = None
                agent._mesa_cell = None
        if record.is_empty:
            self._detach(record)

    def _clear(self, record: _Record) -> None:
        """Remove the agent from every space in the frame."""
        agent = record.agent
        for cell in record.cells.values():
            cell.remove_agent(agent)
        record.cells.clear()
        if record.home is not None:
            record.home = None
            agent._mesa_cell = None
        # A ContinuousSpaceAgent removes itself from its own space
        if record.continuous is not None and record.holder is record:
            record.continuous._remove_agent(agent)
        record.continuous = record.holder = None
        self._detach(record)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def location_of(self, agent: Agent) -> np.ndarray | None:
        """Return the agent's location in frame coordinates, or None if it has none.

        The returned array is read-only. Use :meth:`move` to change it.
        """
        record = self._lookup(agent)
        if record is None:
            # An agent in a single space has no record; build a throwaway one
            record = self._record(agent)
            if record.is_empty:
                return None
        return record.location()

    def move(self, agent: Agent, point) -> None:
        """Move the agent to a point, updating every space in the frame it is in.

        The move is atomic: if any space rejects it (a full cell, a point outside
        the space), the agent stays where it was and the exception propagates.

        Args:
            agent: the agent to move
            point: the new location in frame coordinates
        """
        record = self._record(agent)
        if record.is_empty:
            raise ValueError(
                f"Agent {agent.unique_id} is not in a space of {self!r}; add it to one first."
            )
        self._check_movable(agent)
        self._write(record, None, point)
        self._ensure_attached(record)
