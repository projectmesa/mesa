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

    def forward_backward(self, amount, sign):
        """Does the calculation to find  the agent's next move and is used within the forward and backward functions"""
        new_x = float(self.pos[0]) + sign * math.cos(self.heading * math.pi / 180) * amount
        new_y = float(self.pos[1]) + sign * math.sin(self.heading * math.pi / -180) * amount
        next_move = (new_x, new_y)
        self.model.space.move_agent(self, next_move)

    def forward(self, amount):
        """Moves the agent forward by the amount given"""
        self.forward_backward(amount, 1)

    def back(self, amount):
        """Moves the agent backwards from where its facing by the given amount"""
        self.forward_backward(amount, -1)

    def right(self, degree):
        """Turns the agent right by the given degree"""
        self.heading = (self.heading - degree) % 360

    def left(self, degree):
        """Turns the agent left by the given degree"""
        self.heading = (self.heading + degree) % 360

    def setxy(self, x, y):
        """Sets the current position to the specified x,y parameters"""
        self.pos = (x, y)

    def distancexy(self, x, y):
        """Gives you the distance of the agent and the given coordinate"""
        return math.dist(self.pos, (x, y))

    def distance(self, another_agent):
        """Gives you the distance between the agent and another agent"""
        return self.distancexy(another_agent.pos[0], another_agent.pos[1])

    def die(self):
        """Removes the agent from the schedule and the grid"""
        self.model.schedule.remove(self)
        self.model.space.remove_agent(self)

    @property
    def random(self) -> Random:
        return self.model.random
