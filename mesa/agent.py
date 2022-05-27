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

    def move_forward_or_backward(self, amount, sign):
        """Does the calculation to find  the agent's next move and is used within the forward and backward functions"""
        new_x = float(self.pos[0]) + sign * math.cos(self.heading * math.pi / 180) * amount
        new_y = float(self.pos[1]) + sign * math.sin(self.heading * math.pi / -180) * amount
        next_pos = (new_x, new_y)
        try:
            self.model.space.move_agent(self, next_pos)
        except:
            print("agent.py (forward_backwards): could not move agent within self.model.space")

    def move_forward(self, amount):
        """Moves the agent forward by the amount given"""
        self.move_forward_or_backward(amount, 1)

    def move_backward(self, amount):
        """Moves the agent backwards from where its facing by the given amount"""
        self.move_forward_or_backward(amount, -1)

    def turn_right(self, degree):
        """Turns the agent right by the given degree"""
        self.heading = (self.heading - degree) % 360

    def turn_left(self, degree):
        """Turns the agent left by the given degree"""
        self.heading = (self.heading + degree) % 360


    @property
    def random(self) -> Random:
        return self.model.random
