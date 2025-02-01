"""Cell spaces for active, property-rich spatial modeling in Mesa.

Cell spaces extend Mesa's spatial modeling capabilities by making the space itself active -
each position (cell) can have properties and behaviors rather than just containing agents.
This enables more sophisticated environmental modeling and agent-environment interactions.

Key components:
- Cells: Active positions that can have properties and contain agents
- CellAgents: Agents that understand how to interact with cells
- Spaces: Different cell organization patterns (grids, networks, etc.)
- PropertyLayers: Efficient property storage and manipulation

This is particularly useful for models where the environment plays an active role,
like resource growth, pollution diffusion, or infrastructure networks. The cell
space system is experimental and under active development.
"""

from mesa.experimental.cell_space.cell import Cell
from mesa.experimental.cell_space.cell_agent import (
    CellAgent,
    FixedAgent,
    Grid2DMovingAgent,
)
from mesa.experimental.cell_space.cell_collection import CellCollection
from mesa.experimental.cell_space.discrete_space import DiscreteSpace
from mesa.experimental.cell_space.grid import (
    Grid,
    HexGrid,
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
)
from mesa.experimental.cell_space.network import Network
from mesa.experimental.cell_space.property_layer import PropertyLayer
from mesa.experimental.cell_space.voronoi import VoronoiGrid

__all__ = [
    "Cell",
    "CellAgent",
    "CellCollection",
    "DiscreteSpace",
    "FixedAgent",
    "Grid",
    "Grid2DMovingAgent",
    "HexGrid",
    "Network",
    "OrthogonalMooreGrid",
    "OrthogonalVonNeumannGrid",
    "PropertyLayer",
    "VoronoiGrid",
]
