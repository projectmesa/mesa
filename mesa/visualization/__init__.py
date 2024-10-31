"""Solara based visualization for Mesa models."""

from .components import make_plot_component, make_space_component
from .components.altair_components import make_altair_space
from .components.matplotlib_components import (
    make_mpl_plot_component,
    make_mpl_space_component,
    make_plot_measure,
    make_space_matplotlib,
)
from .components.mpl_space_drawing import (
    draw_continuous_space,
    draw_hex_grid,
    draw_network,
    draw_orthogonal_grid,
    draw_property_layers,
    draw_space,
    draw_voroinoi_grid,
)
from .solara_viz import JupyterViz, SolaraViz
from .UserParam import Slider

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "Slider",
    "make_altair_space",
    "make_mpl_space_component",
    "make_mpl_plot_component",
    "make_plot_measure",
    "make_space_matplotlib",
    "draw_continuous_space",
    "draw_hex_grid",
    "draw_network",
    "draw_orthogonal_grid",
    "draw_property_layers",
    "draw_space",
    "draw_voroinoi_grid",
    "make_plot_component",
    "make_space_component",
]
