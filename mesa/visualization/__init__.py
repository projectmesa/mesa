"""Solara based visualization for Mesa models."""

from .components.altair import make_space_altair
from .components.matplotlib import make_plot_component, make_space_component
from .solara_viz import JupyterViz, SolaraViz
from .UserParam import Slider

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "Slider",
    "make_space_altair",
    "make_space_component",
    "make_plot_component",
]
