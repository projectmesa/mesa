"""Solara based visualization for Mesa models.

.. note::
    SolaraViz is experimental and still in active development for Mesa 3.0. While we attempt to minimize them, there might be API breaking changes between Mesa 3.0 and 3.1.

    There won't be breaking changes between Mesa 3.0.x patch releases.
"""

from mesa.visualization.mpl_space_drawing import (
    draw_space,
)

from .components import make_plot_component, make_space_component
from .components.altair_components import make_space_altair
from .solara_viz import JupyterViz, SolaraViz
from .user_param import Slider

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "Slider",
    "make_space_altair",
    "draw_space",
    "make_plot_component",
    "make_space_component",
]
