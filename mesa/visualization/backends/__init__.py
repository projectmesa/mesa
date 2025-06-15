"""Visualization backends for Mesa space rendering.

This module provides different backend implementations for visualizing
Mesa agent-based model spaces and components.

Available Backends:
    AltairBackend
    MatplotlibBackend
"""

from .altair_backend import AltairBackend
from .matplotlib_backend import MatplotlibBackend

__all__ = [
    "AltairBackend",
    "MatplotlibBackend",
]
