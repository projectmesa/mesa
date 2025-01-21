"""Solara based visualization for Mesa models."""

from mesa.visualization.mpl_space_drawing import (
    draw_space,
)

from .components import make_plot_component, make_space_component
from .components.altair_components import make_space_altair
from .solara_viz import JupyterViz, SolaraViz
from .user_param import Slider

__all__ = [
    "JupyterViz",
    "Slider",
    "SolaraViz",
    "draw_space",
    "make_plot_component",
    "make_space_altair",
    "make_space_component",
]
