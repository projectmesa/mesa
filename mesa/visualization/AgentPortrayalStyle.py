from dataclasses import dataclass


@dataclass
class AgentPortrayalStyle:
    """Dataclass to define agent portrayal styles in a proper structured way."""

    color: str = "tab:red"
    marker: str = "o"
    size: int = 30
    zorder: int = 1
    alpha: float = 1.0  # Supports transparency
    linewidths: float = 1.0  # line width for markers
    edgecolors: str = "black"  # edge color for markers
    loc: tuple[float, float] | None = None  # stores agent position

    def to_dict(self):
        """Convert the style to a dictionary (for backward compatibility)."""
        return {
            "color": self.color,
            "marker": self.marker,
            "size": self.size,
            "zorder": self.zorder,
            "alpha": self.alpha,
            "linewidths": self.linewidths,
            "edgecolors": self.edgecolors,
            "loc": self.loc,
        }
