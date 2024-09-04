from .components.altair import make_space_altair
from .components.matplotlib import make_plot_measure, make_space_matplotlib
from .solara_viz import JupyterViz, Slider, SolaraViz, make_text

__all__ = [
    "JupyterViz",
    "SolaraViz",
    "make_text",
    "Slider",
    "make_space_altair",
    "make_space_matplotlib",
    "make_plot_measure",
]
