"""Solara based visualization for Mesa models."""

from mesa.visualization.mpl_drawing import (
    draw_plot,
    draw_space,
)

from .components import make_plot_component, make_space_component
from .components.altair_components import make_space_altair
from .solara_viz import JupyterViz, SolaraViz
from .UserParam import Slider

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "Slider",
    "make_space_altair",
    "draw_space",
    "draw_plot",
    "make_plot_component",
    "make_space_component",
]
