"""
The agent class for Mesa framework.

Core Objects: Agent

"""
# mypy
from typing import Optional, TYPE_CHECKING
from random import Random

if TYPE_CHECKING:
    from mesa.model import Model
    from mesa.space import Position


class Agent:
    """ Base class for a model agent. """

    def __init__(self, unique_id: int, model: "Model") -> None:
        """ Create a new agent. """
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # type: Optional[Position]

    def step(self) -> None:
        """ A single step of the agent. """
        pass

    def advance(self) -> None:
        pass

    @property
    def random(self) -> Random:
        return self.model.random
