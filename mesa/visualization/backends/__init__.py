"""Visualization backends for Mesa space rendering.

This module provides different backend implementations for visualizing
Mesa agent-based model spaces and components.

Note:
    These backends are used internally by the space renderer and are not intended for
    direct use by end users. See `SpaceRenderer` for actual usage and setting up
    visualizations.

Available Backends:
    1. AltairBackend
    2. MatplotlibBackend

"""

from .altair_backend import AltairBackend
from .matplotlib_backend import MatplotlibBackend

__all__ = [
    "AltairBackend",
    "MatplotlibBackend",
]
