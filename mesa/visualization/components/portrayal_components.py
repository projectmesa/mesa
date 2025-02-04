"""Components for defining visual styles and portrayals in Mesa visualizations.

This module provides classes for configuring the visual appearance of agents and
property layers in Mesa visualization components.
"""

from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from numbers import Number
from typing import ClassVar

import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
from matplotlib.colors import Colormap


@dataclass
class AgentPortrayalStyle:
    """A class to define the visual style of an agent in Mesa visualizations.

    Attributes:
        color: Color specification for the agent. Can be any valid matplotlib color.
        marker: Marker style for the agent (e.g., 'o', 's', '^').
        size: Size of the agent marker in points.
        zorder: The drawing order of the agent relative to other elements.

    Example:
        >>> def agent_portrayal(agent):
        >>>     portrayal = AgentPortrayalStyle(
        >>>         color='tab:orange' if agent.id == 1 else 'tab:blue',
        >>>         marker='^',
        >>>         size=70,
        >>>         zorder=1
        >>>     )
        >>>     return dict(portrayal)
    """

    # fmt:off
    VALID_MARKERS: ClassVar[set[str]] = {
        "o", "s", "^", "v", "<", ">", "D", "p", "h", "H", "8", "*",
        "+", "x", ".", ",", "1", "2", "3", "4", "|", "_",
    }
    # fmt:on

    # Default values
    color: str | tuple | None = "tab:blue"
    marker: str | None = "o"
    size: Number | None = 50
    zorder: int | None = 1

    def __post_init__(self):
        """Validate the attributes after initialization."""
        if self.color is not None:
            try:
                mcolors.to_rgb(self.color)
            except ValueError as err:
                raise ValueError(f"Invalid color specification: {self.color}") from err

        if self.marker is not None:
            if not isinstance(self.marker, str):
                raise ValueError(f"Marker must be a string, got {type(self.marker)}")
            if self.marker not in self.VALID_MARKERS:
                raise ValueError(
                    f"Invalid marker '{self.marker}'. Valid markers are: {', '.join(sorted(self.VALID_MARKERS))}"
                )

        if self.size is not None and not isinstance(self.size, Number):
            raise ValueError(f"Size must be a number, got {type(self.size)}")

        if self.zorder is not None and not isinstance(self.zorder, int):
            raise ValueError(f"Zorder must be an integer, got {type(self.zorder)}")

    def __iter__(self) -> Iterator[tuple[str, any]]:
        """Return an iterator of the style attributes and their values."""
        return iter(asdict(self).items())


@dataclass
class PropertyLayerStyle:
    """Style configuration for a single property layer.

    Args:
        color: A valid matplotlib color string
        colormap: A valid matplotlib colormap name or Colormap object
        vmin: Minimum value for colormap scaling
        vmax: Maximum value for colormap scaling
        alpha: Opacity value between 0 and 1
        colorbar: Whether to show colorbar

    Note: color and colormap are mutually exclusive.
    """

    vmin: float | None = None
    vmax: float | None = None
    alpha: float | None = None
    colorbar: bool | None = None
    color: str | None = None
    colormap: str | Colormap | None = None

    def __post_init__(self):
        """Validate style attributes."""
        # Validate color/colormap exclusivity
        if self.color is None and self.colormap is None:
            raise ValueError("Please specify either color or colormap")
        if self.color is not None and self.colormap is not None:
            raise ValueError("Cannot specify both color and colormap")

        # Validate color if specified
        if self.color is not None:
            try:
                mcolors.to_rgb(self.color)
            except ValueError as err:
                raise ValueError(f"Invalid color specification: {self.color}") from err

        # Validate colormap if specified
        if isinstance(self.colormap, str) and self.colormap not in plt.colormaps():
            raise ValueError(f"Invalid colormap name: {self.colormap}")

        # Validate numeric ranges
        if self.alpha is not None and (
            not isinstance(self.alpha, int | float) or not 0 <= self.alpha <= 1
        ):
            raise ValueError(f"Alpha must be between 0 and 1, got {self.alpha}")
        if self.vmin is not None and self.vmax is not None and self.vmin >= self.vmax:
            raise ValueError(f"vmin ({self.vmin}) must be less than vmax ({self.vmax})")


@dataclass
class PropertyLayerPortrayal:
    """Manager for property layer styles."""

    layers: dict[str, PropertyLayerStyle] = field(default_factory=dict)

    def add_layer(
        self,
        name: str,
        color: str | None = None,
        colormap: str | Colormap | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
        alpha: float | None = None,
        colorbar: bool | None = None,
    ) -> None:
        """Add a new property layer style.

        Args:
            name: Name of the layer
            color: A valid matplotlib color string (mutually exclusive with colormap)
            colormap: A valid matplotlib colormap name or object (mutually exclusive with color)
            vmin: Minimum value for colormap scaling
            vmax: Maximum value for colormap scaling
            alpha: Opacity value between 0 and 1
            colorbar: Whether to show colorbar

        Example:
            >>> portrayal = PropertyLayerPortrayal()
            >>> portrayal.add_layer('temperature', colormap='coolwarm', vmin=0, vmax=100)
            >>> portrayal.add_layer('elevation', color='brown', vmin=0, vmax=100)
            >>> propertylayer_portrayal = dict(portrayal)

        Note: Either color or colormap must be specified, but not both.
        """
        self.layers[name] = PropertyLayerStyle(
            vmin=vmin,
            vmax=vmax,
            alpha=alpha,
            colorbar=colorbar,
            color=color,
            colormap=colormap,
        )

    def __iter__(self) -> Iterator[tuple[str, dict]]:
        """Return an iterator of layer names and their style configurations."""
        return ((name, asdict(style)) for name, style in self.layers.items())
