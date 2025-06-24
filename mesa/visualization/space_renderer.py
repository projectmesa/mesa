"""Space rendering module for Mesa visualizations.

This module provides functionality to render Mesa model spaces with different
backends, supporting various space types and visualization components.
"""

import warnings
from collections.abc import Callable
from typing import Literal

import numpy as np

import mesa
from mesa.discrete_space import (
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
    VoronoiGrid,
)
from mesa.space import (
    ContinuousSpace,
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    NetworkGrid,
    SingleGrid,
    _HexGrid,
)
from mesa.visualization.backends import AltairBackend, MatplotlibBackend
from mesa.visualization.space_drawers import (
    ContinuousSpaceDrawer,
    HexSpaceDrawer,
    NetworkSpaceDrawer,
    OrthogonalSpaceDrawer,
    VoronoiSpaceDrawer,
)

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid
Network = NetworkGrid | mesa.discrete_space.Network


class SpaceRenderer:
    """Renders Mesa spaces using different visualization backends.

    Supports multiple space types and backends for flexible visualization
    of agent-based models.
    """

    def __init__(
        self,
        model: mesa.Model,
        backend: Literal["matplotlib", "altair"] | None = "matplotlib",
    ):
        """Initialize the space renderer.

        Args:
            model (mesa.Model): The Mesa model to render.
            backend (Literal["matplotlib", "altair"] | None): The visualization backend to use.
        """
        self.space = getattr(model, "grid", getattr(model, "space", None))

        self.space_drawer = self._get_space_drawer()
        self.space_mesh = None
        self.agent_mesh = None
        self.propertylayer_mesh = None

        self.backend = backend

        if backend == "matplotlib":
            self.backend_renderer = MatplotlibBackend(
                self.space_drawer,
            )
        elif backend == "altair":
            self.backend_renderer = AltairBackend(
                self.space_drawer,
            )
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        self.backend_renderer.initialize_canvas()

    def _get_space_drawer(self):
        """Get appropriate space drawer based on space type.

        Returns:
            Space drawer instance for the model's space type.

        Raises:
            ValueError: If the space type is not supported.
        """
        if isinstance(self.space, HexGrid | _HexGrid):
            return HexSpaceDrawer(self.space)
        elif isinstance(self.space, OrthogonalGrid):
            return OrthogonalSpaceDrawer(self.space)
        elif isinstance(self.space, ContinuousSpace):
            return ContinuousSpaceDrawer(self.space)
        elif isinstance(self.space, VoronoiGrid):
            return VoronoiSpaceDrawer(self.space)
        elif isinstance(self.space, Network):
            return NetworkSpaceDrawer(self.space)
        raise ValueError(
            f"Unsupported space type: {type(self.space).__name__}. "
            "Supported types are OrthogonalGrid, HexGrid, ContinuousSpace, VoronoiGrid, and Network."
        )

    def _map_coordinates(self, arguments):
        """Map agent coordinates to appropriate space coordinates.

        Args:
            arguments (dict): Dictionary containing agent data with coordinates.

        Returns:
            dict: Dictionary with mapped coordinates appropriate for the space type.
        """
        mapped_arguments = arguments.copy()

        if isinstance(self.space, OrthogonalGrid | VoronoiGrid | ContinuousSpace):
            # Use the coordinates directly for Orthogonal grids, Voronoi grids and Continuous spaces
            mapped_arguments["loc"] = arguments["loc"].astype(float)

        elif isinstance(self.space, HexGrid):
            # Map rectangular coordinates to hexagonal grid coordinates
            loc = arguments["loc"].astype(float)
            if loc.size > 0:
                # Calculate hexagon centers
                loc[:, 0] = loc[:, 0] * self.space_drawer.x_spacing + (
                    (loc[:, 1] - 1) % 2
                ) * (self.space_drawer.x_spacing / 2)
                loc[:, 1] = loc[:, 1] * self.space_drawer.y_spacing
            mapped_arguments["loc"] = loc

        elif isinstance(self.space, Network):
            # Map coordinates for Network spaces
            loc = arguments["loc"].astype(float)
            pos = np.asarray(list(self.space_drawer.pos.values()))
            # For network only both x and y contains the correct coordinates
            # use one of them
            x = loc[:, 0]
            if x is None:
                x = loc[:, 1]

            # Ensure x is an integer index for the position mapping
            x = x.astype(int)

            mapped_arguments["loc"] = pos[x - 1]  # Adjust for 1-based indexing

        return mapped_arguments

    def draw_structure(self, **kwargs):
        """Draw the space structure.

        Args:
            **kwargs: Additional keyword arguments for the drawing function.

        Returns:
            The visual representation of the space structure.
        """
        # Store space_kwargs for internal use
        self.space_kwargs = kwargs

        self.space_mesh = self.backend_renderer.draw_structure(**self.space_kwargs)
        return self.space_mesh

    def draw_agents(self, agent_portrayal: Callable, **kwargs):
        """Draw agents on the space.

        Args:
            agent_portrayal (Callable): Function that takes an agent and returns AgentPortrayalStyle.
            **kwargs: Additional keyword arguments for the drawing function.

        Returns:
            The visual representation of the agents.
        """
        # Store data for internal use
        self.agent_portrayal = agent_portrayal
        self.agent_kwargs = kwargs

        # Prepare data for agent plotting
        arguments = self.backend_renderer.collect_agent_data(
            self.space, agent_portrayal, default_size=self.space_drawer.s_default
        )
        arguments = self._map_coordinates(arguments)

        self.agent_mesh = self.backend_renderer.draw_agents(
            arguments, **self.agent_kwargs
        )
        return self.agent_mesh

    def draw_propertylayer(self, propertylayer_portrayal: Callable | dict):
        """Draw property layers on the space.

        Args:
            propertylayer_portrayal (Callable | dict): Function that returns PropertyLayerStyle
                or dict with portrayal parameters.

        Returns:
            The visual representation of the property layers.

        Raises:
            Exception: If no property layers are found on the space.
        """
        # Import here to avoid circular imports
        from mesa.visualization.components import PropertyLayerStyle

        def _dict_to_callable(portrayal_dict):
            """Convert legacy dict portrayal to callable.

            Args:
                portrayal_dict (dict): Dictionary with portrayal parameters.

            Returns:
                Callable: Function that returns PropertyLayerStyle.
            """

            def style_callable(layer_object):
                layer_name = layer_object.name
                params = portrayal_dict.get(layer_name)

                warnings.warn(
                    "Dict propertylayer_portrayal is deprecated. "
                    "Use a callable returning PropertyLayerStyle instead.",
                    PendingDeprecationWarning,
                    stacklevel=2,
                )

                if params is None:
                    return None

                return PropertyLayerStyle(
                    color=params.get("color"),
                    colormap=params.get("colormap"),
                    alpha=params.get("alpha", PropertyLayerStyle.alpha),
                    vmin=params.get("vmin"),
                    vmax=params.get("vmax"),
                    colorbar=params.get("colorbar", PropertyLayerStyle.colorbar),
                )

            return style_callable

        # Get property layers
        try:
            # old style spaces
            property_layers = self.space.properties
        except AttributeError:
            # new style spaces
            property_layers = self.space._mesa_property_layers

        # Convert portrayal to callable if needed
        if isinstance(propertylayer_portrayal, dict):
            self.propertylayer_portrayal = _dict_to_callable(propertylayer_portrayal)
        else:
            self.propertylayer_portrayal = propertylayer_portrayal

        number_of_propertylayers = sum(
            [1 for layer in property_layers if layer != "empty"]
        )
        if number_of_propertylayers < 1:
            raise Exception("No property layers were found on the space.")

        self.propertylayer_mesh = self.backend_renderer.draw_propertylayer(
            self.space, property_layers, self.propertylayer_portrayal
        )
        return self.propertylayer_mesh

    def render(
        self,
        agent_portrayal: Callable | None = None,
        propertylayer_portrayal: Callable | dict | None = None,
        **kwargs,
    ):
        """Render the complete space with structure, agents, and property layers.

        Args:
            agent_portrayal (Callable | None): Function that returns AgentPortrayalStyle.
                If None, agents won't be drawn.
            propertylayer_portrayal (Callable | dict | None): Function that returns
                PropertyLayerStyle or dict with portrayal parameters. If None,
                property layers won't be drawn.
            **kwargs: Additional keyword arguments for drawing functions.
                - space_kwargs (dict): Arguments for draw_structure().
                - agent_kwargs (dict): Arguments for draw_agents().
        """
        space_kwargs = kwargs.pop("space_kwargs", {})
        agent_kwargs = kwargs.pop("agent_kwargs", {})
        if self.space_mesh is None:
            self.draw_structure(**space_kwargs)
        if self.agent_mesh is None and agent_portrayal is not None:
            self.draw_agents(agent_portrayal, **agent_kwargs)
        if self.propertylayer_mesh is None and propertylayer_portrayal is not None:
            self.draw_propertylayer(propertylayer_portrayal)

    @property
    def canvas(self):
        """Get the current canvas object.

        Returns:
            The backend-specific canvas object.
        """
        return self.backend_renderer.canvas
