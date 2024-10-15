"""Experimental init."""

from mesa.experimental import cell_space

try:
    from .solara_viz import JupyterViz, Slider, SolaraViz, make_text

    __all__ = ["cell_space", "JupyterViz", "Slider", "SolaraViz", "make_text"]
except ImportError:
    print(
        "Could not import SolaraViz. If you need it, install with 'pip install --pre mesa[viz]'"
    )
    __all__ = ["cell_space"]
