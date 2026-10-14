"""The Location descriptor: an agent's location in a frame."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from mesa.experimental.frames.frame import Frame

if TYPE_CHECKING:
    from mesa.agent import Agent

__all__ = ["Location"]


class Location:
    """An agent's location in a frame, as a point in frame coordinates.

    Declare it on an agent class and add the agent to one or more spaces of the
    frame. Assigning a point moves the agent in all of them::

        class Bird(Agent):
            position = Location("physical")

        air.add(bird, [10.0, 20.0])
        ground.add(bird)
        bird.position = [12.0, 21.0]  # air and ground both update

    Reading returns a read-only array, or None while the agent is in no space of
    the frame. Assigning None removes the agent from every space of the frame.

    Args:
        frame: the name of the frame, or a named :class:`Frame`. Frames are created
            per model, so a name is usually the practical choice at class level.
    """

    def __init__(self, frame: str | Frame) -> None:
        """Create a location descriptor."""
        if isinstance(frame, Frame):
            if frame.name is None:
                raise ValueError("Location requires a named frame.")
            frame = frame.name
        self.frame_name: str = frame
        self.name: str | None = None

    def __set_name__(self, owner, name: str) -> None:  # noqa: D105
        self.name = name

    def __get__(self, agent: Agent | None, owner=None) -> np.ndarray | None:  # noqa: D105
        if agent is None:
            return self
        locations = agent._mesa_locations
        if locations is None:
            return None
        record = locations.get(self.frame_name)
        return None if record is None else record.location()

    def __set__(self, agent: Agent, value) -> None:  # noqa: D105
        locations = agent._mesa_locations
        record = None if locations is None else locations.get(self.frame_name)
        if record is None:
            if value is None:
                return
            raise ValueError(
                f"Agent {agent.unique_id} is not in a space of the frame "
                f"{self.frame_name!r}; add it to one first, e.g. space.add(agent, ...)."
            )
        if value is None:
            record.frame._clear(record)
        else:
            record.frame._write(record, None, value)
