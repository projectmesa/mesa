"""Solara based visualization for Mesa models."""

from .components import make_plot_component, make_space_component
from .components.altair_components import make_altair_space, make_space_altair
from mesa.visualization.mpl_space_drawing import (
    draw_space,
)
from .solara_viz import JupyterViz, SolaraViz
from .UserParam import Slider

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "Slider",
    "make_space_altair",
    "make_altair_space",
    "draw_space",
    "make_plot_component",
    "make_space_component",
]
