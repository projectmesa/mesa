import os
import warnings
from dataclasses import fields

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

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

# Type aliases
OrthogonalGrid = SingleGrid | MultiGrid | OrthogonalMooreGrid | OrthogonalVonNeumannGrid
HexGrid = HexSingleGrid | HexMultiGrid | mesa.discrete_space.HexGrid

from PIL import Image

from .abstract_renderer import AbstractRenderer

CORRECTION_FACTOR_MARKER_ZOOM = 0.01


class MatplotlibBackend(AbstractRenderer):
    """A renderer that uses Matplotlib."""

    def initialize_canvas(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(constrained_layout=True)
            self.fig = fig
        self._canvas = ax

    def draw_structure(self, **kwargs):
        ax = kwargs.pop("ax")
        return self.space_drawer.draw_matplotlib(ax, **kwargs)

    def _collect_agent_data(self, space, agent_portrayal, default_size=None):
        """Collect plotting data for all agents in the space.

        Args:
            agent_portrayal: Callable that returns AgentPortrayalStyle for each agent
            default_size: Default marker size if not specified

        Returns:
            Dictionary containing agent plotting data arrays
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

    def draw_agents(self, arguments, **kwargs):
        """Draw agents using matplotlib backend."""

        ax = kwargs.pop("ax")

        def _get_zoom_factor(ax, img):
            """Calculate zoom factor for image markers based on axis limits."""
            ax.get_figure().canvas.draw()
            bbox = ax.get_window_extent().transformed(
                ax.get_figure().dpi_scale_trans.inverted()
            )  # in inches
            width, height = (
                bbox.width * ax.get_figure().dpi,
                bbox.height * ax.get_figure().dpi,
            )  # in pixel

            xr = ax.get_xlim()
            yr = ax.get_ylim()

            x_pixel_per_data = width / (xr[1] - xr[0])
            y_pixel_per_data = height / (yr[1] - yr[0])

            zoom_x = (x_pixel_per_data / img.width) * CORRECTION_FACTOR_MARKER_ZOOM
            zoom_y = (y_pixel_per_data / img.height) * CORRECTION_FACTOR_MARKER_ZOOM

            return min(zoom_x, zoom_y)

        loc = arguments.pop("loc")

        loc_x = loc[:, 0]
        loc_y = loc[:, 1]
        marker = arguments.pop("marker")
        zorder = arguments.pop("zorder")
        malpha = arguments.pop("alpha")
        msize = arguments.pop("s")

        # we check if edgecolor, linewidth, and alpha are specified
        # at the agent level, if not, we remove them from the arguments dict
        # and fallback to the default value in ax.scatter / use what is passed via **kwargs
        for entry in ["edgecolors", "linewidths"]:
            if len(arguments[entry]) == 0:
                arguments.pop(entry)
            else:
                if entry in kwargs:
                    raise ValueError(
                        f"{entry} is specified in agent portrayal and via plotting kwargs, you can only use one or the other"
                    )

        ax.get_figure().canvas.draw()
        for mark in set(marker):
            if isinstance(mark, (str | os.PathLike)) and os.path.isfile(mark):
                # images
                for m_size in np.unique(msize):
                    image = Image.open(mark)
                    im = OffsetImage(
                        image,
                        zoom=_get_zoom_factor(ax, image) * m_size,
                    )
                    im.image.axes = ax

                    mask_marker = [m == mark for m in list(marker)] & (m_size == msize)
                    for z_order in np.unique(zorder[mask_marker]):
                        for m_alpha in np.unique(malpha[mask_marker]):
                            mask = (
                                (z_order == zorder) & (m_alpha == malpha) & mask_marker
                            )
                            for x, y in zip(loc_x[mask], loc_y[mask]):
                                ab = AnnotationBbox(
                                    im,
                                    (x, y),
                                    frameon=False,
                                    pad=0.0,
                                    zorder=z_order,
                                    **kwargs,
                                )
                                ax.add_artist(ab)

            else:
                # ordinary markers
                mask_marker = [m == mark for m in list(marker)]
                for z_order in np.unique(zorder[mask_marker]):
                    zorder_mask = z_order == zorder & mask_marker
                    ax.scatter(
                        loc_x[zorder_mask],
                        loc_y[zorder_mask],
                        marker=mark,
                        zorder=z_order,
                        **{k: v[zorder_mask] for k, v in arguments.items()},
                        **kwargs,
                    )
        return ax

    def draw_propertylayer(self, space, property_layers, propertylayer_portrayal, ax):
        """Draw property layers using matplotlib backend."""
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
                    ax.imshow(rgba_data, origin="lower")
                else:
                    ax.imshow(
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
                ax.add_collection(collection)
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
                cbar = plt.colorbar(sm, ax=ax, label=layer_name)
        return ax, cbar

    def render(
        self,
        space,
        agent_portrayal=None,
        propertylayer_portrayal=None,
        ax: Axes | None = None,
        **kwargs,
    ):
        """Render the complete space with structure, agents, and property layers."""
        structure_kwargs = kwargs.pop("structure_kwargs", {})
        agent_kwargs = kwargs.pop("agent_kwargs", {})

        ax = ax if ax is not None else self._canvas

        if self.space_mesh is None:
            self.draw_structure(ax, **structure_kwargs)
        if agent_portrayal is not None and self.agent_mesh is None:
            arguments = self._collect_agent_data(space, agent_portrayal)
            arguments = self._map_coordinates(arguments)
            self.draw_agents(ax, arguments, **agent_kwargs)
        if propertylayer_portrayal is not None and self.propertylayer_mesh is None:
            self.draw_propertylayer(propertylayer_portrayal, ax)

        return ax

    @property
    def canvas(self):
        if self._canvas is None:
            self.initialize_canvas()
        return self._canvas
