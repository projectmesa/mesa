"""
Mesa Space Module
=================

Classes used to add a spatial component to a model.

Grids
-----

Grid: base grid, a simple list-of-lists.
SingleGrid: grid which strictly enforces one object per cell.
MultiGrid: extension to Grid where each cell is a set of objects.

HexGrid: Extends Grid to handle hexagonal neighbors.

Other Spaces
------------

ContinuousSpace: Continuous space where each agent can have an arbitrary position.
NetworkGrid: A Network of nodes based on networkx

"""
from .hexgrid import HexGrid
from .grid import Grid, SingleGrid, MultiGrid
from .network import NetworkGrid
from .continuous_space import ContinuousSpace

__all__ = [
    "ContinuousSpace",
    "Grid",
    "HexGrid",
    "MultiGrid",
    "NetworkGrid",
    "SingleGrid"
]
