"""
The agent class for Mesa framework.

Core Objects: Agent

"""
# mypy
from typing import Optional, TYPE_CHECKING
from random import Random

if TYPE_CHECKING:
    # We ensure that these are not imported during runtime to prevent cyclic
    # dependency.
    from mesa.model import Model
    from mesa.space import Position


class Agent:
    """Base class for a model agent."""

    def __init__(self, unique_id: int, model: "Model") -> None:
        """Create a new agent.

        Args:
            unique_id (int): A unique numeric identified for the agent
            model: (Model): Instance of the model that contains the agent
        """
        self.unique_id = unique_id
        self.model = model
        self.pos: Optional[Position] = None
        self.heading = 90

    def step(self) -> None:
        """A single step of the agent."""
        pass

    def advance(self) -> None:
        pass

    def setxy(self, x,y):
        """Sets the current position to the specified x,y parameters"""
        self.pos = (x,y)

    @property
    def random(self) -> Random:
        return self.model.random
