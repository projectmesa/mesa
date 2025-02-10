"""This module defines the types used in the visualization modules."""

from mesa.experimental.cell_space import (
    HexGrid as ExperimentalHexGrid,
)
from mesa.experimental.cell_space import (
    Network as ExperimentalNetwork,
)
from mesa.experimental.cell_space import (
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
)
from mesa.space import (
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    NetworkGrid,
    SingleGrid,
)

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | ExperimentalHexGrid
Network = NetworkGrid | ExperimentalNetwork
