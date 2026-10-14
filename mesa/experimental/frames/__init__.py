"""Frames and locations: one coordinate system, several spaces.

A :class:`Frame` is a coordinate system with a meaning. Spaces that share a frame
describe the same locations in different ways, and an agent that is in several of
them has a single location that all of them agree on. See discussion
https://github.com/mesa/mesa/discussions/2585.
"""

from mesa.experimental.frames.frame import Frame
from mesa.experimental.frames.location import Location

__all__ = ["Frame", "Location"]
