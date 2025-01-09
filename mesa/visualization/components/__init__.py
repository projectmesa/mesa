"""custom solara components."""

from __future__ import annotations

from collections.abc import Callable

from .altair_components import SpaceAltair, make_altair_space
from .matplotlib_components import (
    SpaceMatplotlib,
    make_mpl_plot_component,
    make_mpl_space_component,
)


def make_space_component(
    agent_portrayal: Callable | None = None,
    propertylayer_portrayal: dict | None = None,
    post_process: Callable | None = None,
    backend: str = "matplotlib",
    **space_drawing_kwargs,
) -> SpaceMatplotlib | SpaceAltair:
    """Create a Matplotlib-based space visualization component.

    Args:
        agent_portrayal: Function to portray agents.
        propertylayer_portrayal: Dictionary of PropertyLayer portrayal specifications
        post_process : a callable that will be called with the Axes instance. Allows for fine-tuning plots (e.g., control ticks)
        backend: the backend to use {"matplotlib", "altair"}
        space_drawing_kwargs : additional keyword arguments to be passed on to the underlying backend specific space drawer function. See
                               the functions for drawing the various spaces for the appropriate backend further details.


    Returns:
        function: A function that creates a space component
    """
    if backend == "matplotlib":
        return make_mpl_space_component(
            agent_portrayal,
            propertylayer_portrayal,
            post_process,
            **space_drawing_kwargs,
        )
    elif backend == "altair":
        return make_altair_space(
            agent_portrayal,
            propertylayer_portrayal,
            post_process,
            **space_drawing_kwargs,
        )
    else:
        raise ValueError(
            f"unknown backend {backend}, must be one of matplotlib, altair"
        )


def make_plot_component(
    measure: str | dict[str, str] | list[str] | tuple[str],
    post_process: Callable | None = None,
    backend: str = "matplotlib",
    **plot_drawing_kwargs,
):
    """Create a plotting function for a specified measure using the specified backend.

    Args:
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        post_process: a user-specified callable to do post-processing called with the Axes instance.
        backend: the backend to use {"matplotlib", "altair"}
        plot_drawing_kwargs: additional keyword arguments to pass onto the backend specific function for making a plotting component

    Notes:
        altair plotting backend is not yet implemented and planned for mesa 3.1.

    Returns:
        function: A function that creates a plot component
    """
    if backend == "matplotlib":
        return make_mpl_plot_component(measure, post_process, **plot_drawing_kwargs)
    elif backend == "altair":
        raise NotImplementedError("altair line plots are not yet implemented")
    else:
        raise ValueError(
            f"unknown backend {backend}, must be one of matplotlib, altair"
        )
