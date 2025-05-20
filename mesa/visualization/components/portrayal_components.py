"""Portrayal Components Module.

This module defines data structures for styling visual elements in Mesa agent-based model visualizations.
It provides user-facing classes to specify how agents and property layers should appear in the rendered space.

Classes:
- AgentPortrayalStyle: Controls the appearance of individual agents (e.g., color, shape, size, etc.).
- PropertyLayerStyle: Controls the appearance of background property layers (e.g., color gradients or uniform fills).

These components are designed to be passed into Mesa visualizations to customize and standardize how data is presented.
"""

from dataclasses import dataclass
from typing import Any

@dataclass
class AgentPortrayalStyle:
    """Represents the visual styling options for an agent in a visualization.

    User facing component to control how agents are drawn.
    Allows specifying properties like color, size,
    marker shape, position, and other plot attributes.
    """

    x: float
    y: float
    color: str | tuple | None = "tab:blue"
    marker: str | None = "o"
    size: int | float | None = 50
    zorder: int | None = 1
    alpha: float | None = 1.0
    edgecolors: str | tuple | None = None
    linewidths: float | int | None = 1.0

    def update(self, *updates_fields: tuple[str, Any]):
        """Updates attributes from variable (field_name, new_value) tuple arguments.

        Example:
            >>> def agent_portrayal(agent):
            >>>     primary_style = AgentPortrayalStyle(color="blue", marker="^", size=10, x=agent.pos[0], y=agent.pos[1])
            >>>     if agent.type == 1:
            >>>         primary_style.update(("color", "red"), ("size", 30))
            >>>     return primary_style
        """
        for field_to_change, field_to_change_to in updates_fields:
            if hasattr(self, field_to_change):
                setattr(self, field_to_change, field_to_change_to)
            else:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{field_to_change}'"
                )


@dataclass
class PropertyLayerStyle:
    """Represents the visual styling options for a property layer in a visualization.

    User facing component to control how property layers are drawn.
    Allows specifying properties like colormap, single color, value limits,
    and colorbar visibility.

    Note: You can specify either a 'colormap' (for varying data) or a single
    'color' (for a uniform layer appearance), but not both simultaneously.
    """

    colormap: str | None = None
    color: str | None = None
    alpha: float = 0.8
    colorbar: bool = True
    vmin: float | None = None
    vmax: float | None = None

    def __post_init__(self):
        """Validate that color and colormap are not simultaneously specified."""
        if self.color is not None and self.colormap is not None:
            raise ValueError("Specify either 'color' or 'colormap', not both.")
        if self.color is None and self.colormap is None:
            raise ValueError("Specify one of 'color' or 'colormap'")
