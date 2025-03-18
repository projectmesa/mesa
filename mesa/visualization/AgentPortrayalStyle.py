class AgentPortrayalStyle:
    """Class to define agent portrayal styles in a structured way."""

    def __init__(self, color="red", marker="o", size=10, zorder=1):
        self.color = color
        self.marker = marker
        self.size = size
        self.zorder = zorder

    def to_dict(self):
        """Convert the style to a dictionary (for backward compatibility)."""
        return {
            "color": self.color,
            "marker": self.marker,
            "size": self.size,
            "zorder": self.zorder,
        }
