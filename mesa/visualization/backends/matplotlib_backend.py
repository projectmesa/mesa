# noqa: D100
import os
import warnings
from dataclasses import fields

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

import mesa
from mesa.discrete_space import (
    OrthogonalMooreGrid,
    OrthogonalVonNeumannGrid,
)
from mesa.space import (
    HexMultiGrid,
    HexSingleGrid,
    MultiGrid,
    SingleGrid,
)
from mesa.visualization.backends.abstract_renderer import AbstractRenderer

OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid


CORRECTION_FACTOR_MARKER_ZOOM = 0.01


class MatplotlibBackend(AbstractRenderer):
    """Matplotlib-based renderer for Mesa spaces.

    Provides visualization capabilities using Matplotlib for rendering
    space structures, agents, and property layers.
    """

    def initialize_canvas(self, ax=None):
        """Initialize the matplotlib canvas.

        Args:
            ax (matplotlib.axes.Axes, optional): Existing axes to use.
                If None, creates new figure and axes.
        """
        if ax is None:
            fig, ax = plt.subplots(constrained_layout=True)
            self.fig = fig
        self.ax = ax

    def draw_structure(self, **kwargs):
        """Draw the space structure using matplotlib.

        Args:
            **kwargs: Additional arguments passed to the space drawer.
            Checkout respective `SpaceDrawer` class on details how to pass **kwargs.

        Returns:
            The matplotlib axes with the drawn structure.
        """
        return self.space_drawer.draw_matplotlib(self.ax, **kwargs)

    def collect_agent_data(self, space, agent_portrayal, default_size=None):
        """Collect plotting data for all agents in the space.

        Args:
            space: The Mesa space containing agents.
            agent_portrayal (Callable): Function that returns AgentPortrayalStyle for each agent.
            default_size (float, optional): Default marker size if not specified in portrayal.

        Returns:
            dict: Dictionary containing agent plotting data arrays.
        """
        # Initialize data collection arrays
        arguments = {
            "loc": [],
            "s": [],
            "c": [],
            "marker": [],
            "zorder": [],
            "alpha": [],
            "edgecolors": [],
            "linewidths": [],
        }
        # Import here to prevent circular imports
        from mesa.visualization.components import AgentPortrayalStyle

        # Get default values from AgentPortrayalStyle
        style_fields = {f.name: f.default for f in fields(AgentPortrayalStyle)}
        class_default_size = style_fields.get("size")

        for agent in space.agents:
            portray_input = agent_portrayal(agent)

            if isinstance(portray_input, dict):
                warnings.warn(
                    "Returning a dict from agent_portrayal is deprecated. "
                    "Please return an AgentPortrayalStyle instance instead.",
                    PendingDeprecationWarning,
                    stacklevel=2,
                )
                # Handle legacy dict input
                dict_data = portray_input.copy()
                agent_x, agent_y = self._get_agent_pos(agent, space)

                # Extract values with defaults
                aps = AgentPortrayalStyle(
                    x=agent_x,
                    y=agent_y,
                    size=dict_data.pop("size", style_fields.get("size")),
                    color=dict_data.pop("color", style_fields.get("color")),
                    marker=dict_data.pop("marker", style_fields.get("marker")),
                    zorder=dict_data.pop("zorder", style_fields.get("zorder")),
                    alpha=dict_data.pop("alpha", style_fields.get("alpha")),
                    edgecolors=dict_data.pop("edgecolors", None),
                    linewidths=dict_data.pop(
                        "linewidths", style_fields.get("linewidths")
                    ),
                )

                # Warn about unused keys
                if dict_data:
                    ignored_keys = list(dict_data.keys())
                    warnings.warn(
                        f"The following keys were ignored: {', '.join(ignored_keys)}",
                        UserWarning,
                        stacklevel=2,
                    )
            else:
                aps = portray_input
                # Set defaults if not provided
                if aps.edgecolors is None:
                    aps.edgecolors = aps.color
                if aps.x is None and aps.y is None:
                    aps.x, aps.y = self._get_agent_pos(agent, space)

            # Collect agent data
            arguments["loc"].append((aps.x, aps.y))

            # Determine final size
            size_to_collect = aps.size or default_size or class_default_size
            arguments["s"].append(size_to_collect)
            arguments["c"].append(aps.color)
            arguments["marker"].append(aps.marker)
            arguments["zorder"].append(aps.zorder)
            arguments["alpha"].append(aps.alpha)
            if aps.edgecolors is not None:
                arguments["edgecolors"].append(aps.edgecolors)
            arguments["linewidths"].append(aps.linewidths)

        # Convert to numpy arrays
        data = {
            k: (np.asarray(v, dtype=object) if k == "marker" else np.asarray(v))
            for k, v in arguments.items()
        }

        # Handle marker array specially to preserve tuples
        arr = np.empty(len(arguments["marker"]), dtype=object)
        arr[:] = arguments["marker"]
        data["marker"] = arr

        return data

    def _get_zoom_factor(self, img):
        """Calculate zoom factor for image markers based on axis limits."""
        self.ax.get_figure().canvas.draw()
        bbox = self.ax.get_window_extent().transformed(
            self.ax.get_figure().dpi_scale_trans.inverted()
        )
        width, height = (
            bbox.width * self.ax.get_figure().dpi,
            bbox.height * self.ax.get_figure().dpi,
        )

        xr, yr = self.ax.get_xlim(), self.ax.get_ylim()

        # Handle cases where axis limits are the same
        x_range = xr[1] - xr[0]
        y_range = yr[1] - yr[0]
        if x_range == 0 or y_range == 0:
            return 0.1  # Return a default zoom if the axis has no range

        x_pixel_per_data = width / x_range
        y_pixel_per_data = height / y_range

        zoom_x = (x_pixel_per_data / img.width) * CORRECTION_FACTOR_MARKER_ZOOM
        zoom_y = (y_pixel_per_data / img.height) * CORRECTION_FACTOR_MARKER_ZOOM

        return min(zoom_x, zoom_y)

    def _draw_image_markers(self, x, y, zorders, alphas, sizes, marker_path, **kwargs):
        """Draw agents that use an image file as a marker."""
        image = Image.open(marker_path)

        # Group by z-order, then alpha to draw agents in batches
        for z_order in np.unique(zorders):
            z_mask = zorders == z_order
            for alpha in np.unique(alphas[z_mask]):
                a_mask = alphas == alpha
                mask = z_mask & a_mask

                # Filter data for the current batch
                batch_x, batch_y, batch_sizes = x[mask], y[mask], sizes[mask]

                for i in range(len(batch_x)):
                    zoom = self._get_zoom_factor(image) * batch_sizes[i]
                    im = OffsetImage(image, zoom=zoom)
                    im.image.axes = self.ax
                    im.set_alpha(alpha)

                    ab = AnnotationBbox(
                        im,
                        (batch_x[i], batch_y[i]),
                        frameon=False,
                        pad=0.0,
                        zorder=z_order,
                        **kwargs,
                    )
                    self.ax.add_artist(ab)

    def _draw_standard_markers(self, x, y, zorders, marker_shape, arguments, **kwargs):
        """Draw agents that use a standard matplotlib marker."""
        # Group by z-order for efficient batching with a single scatter call
        for z_order in np.unique(zorders):
            mask = zorders == z_order

            # Create a dictionary with argument values filtered for the current batch
            batch_args = {k: v[mask] for k, v in arguments.items()}

            self.ax.scatter(
                x[mask],
                y[mask],
                marker=marker_shape,
                zorder=z_order,
                **batch_args,
                **kwargs,
            )

    def draw_agents(self, arguments, **kwargs):
        """Draw agents by dispatching to specialized marker-drawing methods.

        Args:
            arguments: Dictionary containing agent data arrays.
            **kwargs: Additional keyword arguments for customization.
            Checkout respective `SpaceDrawer` class on details how to pass **kwargs.

        Returns:
            matplotlib.axes.Axes: The Matplotlib Axes with the agents drawn upon it. Nothings is drawn if
            there are no agents.
        """
        if arguments["loc"].size == 0:
            return None

        loc = arguments.pop("loc")
        marker = arguments.pop("marker")
        zorder = arguments.pop("zorder")

        # Alpha is handled differently by each draw method
        arguments.pop("alpha")

        # Validate that properties aren't specified in multiple places
        for entry in ["edgecolors", "linewidths"]:
            if len(arguments[entry]) == 0:
                arguments.pop(entry)
            elif entry in kwargs:
                raise ValueError(
                    f"{entry} is specified in agent portrayal and via plotting kwargs, "
                    "you can only use one or the other"
                )

        loc_x, loc_y = loc[:, 0], loc[:, 1]

        # Group agents by their marker and delegate to the correct drawing function
        for marker_shape in set(marker):
            mask = np.array(marker) == marker_shape

            # Filter all data arrays based on the current marker
            x_group, y_group = loc_x[mask], loc_y[mask]
            zorder_group = zorder[mask]

            # Get agent-specific properties for the group
            group_args = {key: val[mask] for key, val in arguments.items()}

            if isinstance(marker_shape, str | os.PathLike) and os.path.isfile(
                marker_shape
            ):
                # This group uses an image marker
                self._draw_image_markers(
                    x=x_group,
                    y=y_group,
                    zorders=zorder_group,
                    alphas=arguments["alpha"][
                        mask
                    ],  # Pass only the alphas for this group
                    sizes=arguments["s"][mask],  # Pass only the sizes for this group
                    marker_path=marker_shape,
                    **kwargs,
                )
            else:
                # This group uses a standard matplotlib marker
                self._draw_standard_markers(
                    x=x_group,
                    y=y_group,
                    zorders=zorder_group,
                    marker_shape=marker_shape,
                    arguments=group_args,
                    **kwargs,
                )
        return self.ax

    def draw_propertylayer(self, space, property_layers, propertylayer_portrayal):
        """Draw property layers using matplotlib backend.

        Args:
            space: The Mesa space object.
            property_layers (dict): Dictionary of property layers to visualize.
            propertylayer_portrayal (Callable): Function that returns PropertyLayerStyle.

        Returns:
            tuple: (matplotlib.axes.Axes, colorbar) - The matplotlib axes and colorbar objects.
        """
        # Draw each layer
        for layer_name in property_layers:
            if layer_name == "empty":
                continue

            layer = property_layers.get(layer_name)
            portrayal = propertylayer_portrayal(layer)

            if portrayal is None:
                continue

            data = layer.data.astype(float) if layer.data.dtype == bool else layer.data

            # Check dimensions
            if (space.width, space.height) != data.shape:
                warnings.warn(
                    f"Layer {layer_name} dimensions ({data.shape}) "
                    f"don't match space dimensions ({space.width}, {space.height})",
                    UserWarning,
                    stacklevel=2,
                )
                continue

            # Get portrayal parameters
            color = portrayal.color
            colormap = portrayal.colormap
            alpha = portrayal.alpha
            vmin = portrayal.vmin if portrayal.vmin is not None else np.min(data)
            vmax = portrayal.vmax if portrayal.vmax is not None else np.max(data)

            # Set up colormap
            if color:
                rgba_color = to_rgba(color)
                cmap = LinearSegmentedColormap.from_list(
                    layer_name, [(0, 0, 0, 0), (*rgba_color[:3], alpha)]
                )
            elif colormap:
                cmap = colormap
                if isinstance(cmap, list):
                    cmap = LinearSegmentedColormap.from_list(layer_name, cmap)
                elif isinstance(cmap, str):
                    cmap = plt.get_cmap(cmap)
            else:
                raise ValueError(
                    f"PropertyLayer {layer_name} must include 'color' or 'colormap'"
                )

            # Draw based on space type
            if isinstance(space, OrthogonalGrid):
                if color:
                    data = data.T
                    normalized_data = (data - vmin) / (vmax - vmin)
                    rgba_data = np.full((*data.shape, 4), rgba_color)
                    rgba_data[..., 3] *= normalized_data * alpha
                    rgba_data = np.clip(rgba_data, 0, 1)
                    self.ax.imshow(rgba_data, origin="lower")
                else:
                    self.ax.imshow(
                        data.T,
                        cmap=cmap,
                        alpha=alpha,
                        vmin=vmin,
                        vmax=vmax,
                        origin="lower",
                    )
            elif isinstance(space, HexGrid):
                hexagons = self.space_drawer.hexagons
                norm = Normalize(vmin=vmin, vmax=vmax)
                colors = data.ravel()

                if color:
                    normalized_colors = np.clip(norm(colors), 0, 1)
                    rgba_colors = np.full((len(colors), 4), rgba_color)
                    rgba_colors[:, 3] = normalized_colors * alpha
                else:
                    rgba_colors = cmap(norm(colors))
                    rgba_colors[..., 3] *= alpha

                collection = PolyCollection(hexagons, facecolors=rgba_colors, zorder=-1)
                self.ax.add_collection(collection)
            else:
                raise NotImplementedError(
                    f"PropertyLayer visualization not implemented for {type(space)}"
                )

            # Add colorbar if requested
            cbar = None
            if portrayal.colorbar:
                norm = Normalize(vmin=vmin, vmax=vmax)
                sm = ScalarMappable(norm=norm, cmap=cmap)
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=self.ax, label=layer_name)
        return self.ax, cbar
