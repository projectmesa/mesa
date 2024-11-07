"""Mesa visualization module for recording videos of model simulations.

This module uses Matplotlib to create visualizations of model spaces and
measures, and records them as videos.

Please install FFmpeg to use this module:
    - macOS: brew install ffmpeg
    - Linux: sudo apt-get install ffmpeg
    - Windows: download from https://ffmpeg.org/download.html
"""

import shutil
from collections.abc import Callable, Sequence
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

import mesa
from mesa.visualization.mpl_drawing import (
    draw_plot,
    draw_space,
)


def make_space_component(
    agent_portrayal: Callable | None = None,
    propertylayer_portrayal: dict | None = None,
    post_process: Callable | None = None,
    **space_drawing_kwargs,
) -> Callable[[mesa.Model, plt.Axes | None], plt.Axes]:
    """Create a Matplotlib-based space visualization component.

    Args:
        agent_portrayal: Function to portray agents.
        propertylayer_portrayal: Dictionary of PropertyLayer portrayal specifications
        post_process : a callable that will be called with the Axes instance. Allows for fine tuning plots (e.g., control ticks)
        space_drawing_kwargs : additional keyword arguments to be passed on to the underlying space drawer function. See
                               the functions for drawing the various spaces for further details.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", and "zorder". Other field are ignored and will result in a user warning.


    Returns:
        function: A function that returns a Axes instance with the space drawn
    """
    if agent_portrayal is None:

        def agent_portrayal(a):
            return {}

    def _make_space_component(model, ax=None):
        space = getattr(model, "grid", None) or getattr(model, "space", None)
        ax = draw_space(
            space,
            agent_portrayal,
            propertylayer_portrayal,
            ax,
            **space_drawing_kwargs,
        )
        if post_process:
            post_process(ax)
        return ax

    return _make_space_component


def make_plot_component(
    measure: Callable,
    post_process: Callable | None = None,
    **kwargs,
) -> Callable[[mesa.Model, plt.Axes | None], plt.Axes]:
    """Create a plotting function for a specified measure.

    Args:
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        post_process : a callable that will be called with the Axes instance. Allows for fine tuning plots (e.g., control ticks)
        kwargs: Additional keyword arguments to pass to the MeasureRendererMatplotlib constructor.

    Returns:
        function: A function that returns a Axes instance with the measure(s) drawn
    """

    def _make_plot_component(model, ax=None):
        ax = draw_plot(model, measure, ax, **kwargs)
        if post_process:
            post_process(ax)
        return ax

    return _make_plot_component


class VideoViz:
    """Create high-quality video recordings of model simulations."""

    def __init__(
        self,
        model: mesa.Model,
        components: Sequence[Callable[[mesa.Model, plt.Axes | None], plt.Axes]],
        *,
        title: str | None = None,
        figsize: tuple[float, float] | None = None,
        grid: tuple[int, int] | None = None,
    ):
        """Initialize video visualization configuration.

        Args:
            model: The model to simulate and record
            components: Sequence of component objects defining what to visualize
            title: Optional title for the video
            figsize: Optional figure size in inches (width, height)
            grid: Optional (rows, cols) for custom layout. Auto-calculated if None.
        """
        # Check if FFmpeg is available
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg to save animations:\n"
                "  - macOS: brew install ffmpeg\n"
                "  - Linux: sudo apt-get install ffmpeg\n"
                "  - Windows: download from https://ffmpeg.org/download.html"
            )
        self.model = model
        self.components = components
        self.title = title
        self.figsize = figsize
        self.grid = grid or self._calculate_grid(len(components))

        # Setup figure and axes
        self.fig, self.axes = self._setup_figure()

    def record(
        self,
        *,
        steps: int,
        filepath: str | Path,
        dpi: int = 100,
        fps: int = 10,
        codec: str = "h264",
        bitrate: int = 2000,
    ) -> None:
        """Record model simulation to video file.

        Args:
            steps: Number of simulation steps to record
            filepath: Where to save the video file
            dpi: Resolution of the output video
            fps: Frames per second in the output video
            codec: Video codec to use
            bitrate: Video bitrate in kbps (default: 2000)

        Raises:
            RuntimeError: If FFmpeg is not installed
        """
        filepath = Path(filepath)

        def update(frame_num):
            # Update model state
            self.model.step()

            # Render all visualization frames
            for component, ax in zip(self.components, self.axes):
                ax.clear()
                component(self.model, ax)
            return self.axes

        # Create and save animation
        anim = animation.FuncAnimation(
            self.fig, update, frames=steps, interval=1000 / fps, blit=False
        )

        writer = animation.FFMpegWriter(
            fps=fps,
            codec=codec,
            bitrate=bitrate,  # Now passing as integer
        )

        anim.save(filepath, writer=writer, dpi=dpi)

    def _calculate_grid(self, n_frames: int) -> tuple[int, int]:
        """Calculate optimal grid layout for given number of frames."""
        cols = min(3, n_frames)  # Max 3 columns
        rows = int(np.ceil(n_frames / cols))
        return (rows, cols)

    def _setup_figure(self):
        """Setup matplotlib figure and axes."""
        if not self.figsize:
            self.figsize = (5 * self.grid[1], 5 * self.grid[0])
        fig = plt.figure(figsize=self.figsize)
        axes = []

        for i in range(len(self.components)):
            ax = fig.add_subplot(self.grid[0], self.grid[1], i + 1)
            axes.append(ax)

        if self.title:
            fig.suptitle(self.title, fontsize=16)
        fig.tight_layout()
        return fig, axes
