from abc import ABC, abstractmethod

import mesa
from mesa.discrete_space import (
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

# Define type hints for space types
OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network


class AbstractRenderer(ABC):
    """Abstract base class for a visualization backend."""

    def __init__(self, space_drawer, meshes: list | None = None):
        self.space_drawer = space_drawer

        self.space_mesh = meshes[0]
        self.agent_mesh = meshes[1]
        self.propertylayer_mesh = meshes[2]

        self._canvas = None

    def _get_agent_pos(self, agent, space):
        """Get agent position based on space type."""
        if isinstance(space, NetworkGrid):
            return agent.pos, agent.pos
        elif isinstance(space, Network):
            return agent.cell.coordinate, agent.cell.coordinate
        else:
            x = agent.pos[0] if agent.pos is not None else agent.cell.coordinate[0]
            y = agent.pos[1] if agent.pos is not None else agent.cell.coordinate[1]
            return x, y

    @abstractmethod
    def initialize_canvas(self, **kwargs):
        """Set up the drawing canvas (e.g., Matplotlib Axes, Altair Chart)."""

    @abstractmethod
    def draw_structure(self, **kwargs):
        """Draw the space structure (grid lines, etc.)."""

    @abstractmethod
    def draw_agents(self, agent_portrayal, **kwargs):
        """Collect agent data and draw them."""

    @abstractmethod
    def draw_propertylayer(self, propertylayer_portrayal, **kwargs):
        """Draw property layers."""

    @abstractmethod
    def render(self, agent_portrayal, propertylayer_portrayal, **kwargs):
        """Render the entire visualization."""

    @property
    @abstractmethod
    def canvas(self):
        """Return the current canvas object."""

    def clear_meshes(self):
        """Clear all stored mesh objects."""
        self.space_mesh = None
        self.agent_mesh = None
        self.propertylayer_mesh = None
