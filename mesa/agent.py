"""
The agent class for Mesa framework.

Core Objects: Agent
"""
# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

# mypy
from typing import TYPE_CHECKING
from random import Random

if TYPE_CHECKING:
    # We ensure that these are not imported during runtime to prevent cyclic
    # dependency.
    from mesa.model import Model
    from mesa.space import Position


class Agent:
    """Base class for a model agent."""

    def __init__(self, unique_id: int, model: Model) -> None:
        """Create a new agent.

        Args:
            unique_id (int): A unique numeric identified for the agent
            model: (Model): Instance of the model that contains the agent
        """
        self.unique_id = unique_id
        self.model = model
        self.pos: Position | None = None

    def step(self) -> None:
        """A single step of the agent."""
        pass

    def advance(self) -> None:
        pass

    @property
    def random(self) -> Random:
        return self.model.random
