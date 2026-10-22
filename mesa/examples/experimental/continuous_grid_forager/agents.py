"""Agents for the continuous-grid forager example."""

import numpy as np

from mesa.experimental.continuous_space import ContinuousSpaceAgent


class Forager(ContinuousSpaceAgent):
    """A continuously moving agent that harvests from its looked-up grid cell."""

    def __init__(
        self,
        model,
        space,
        position=(0.25, 0.25),
        velocity=(1.0, 0.0),
        harvest_amount=2.0,
    ):
        super().__init__(space, model)
        self.position = position
        self.velocity = np.asarray(velocity, dtype=float)
        self.harvest_amount = harvest_amount
        self.energy = 0.0
        self.last_harvest = 0.0
        self.last_cell_coordinate = None

    def step(self):
        """Move, manually look up the cell, and harvest its resource."""
        # Keep positions in [0, width) x [0, height), then use matching
        # toroidal boundaries for the continuous space and grid.
        self.position = np.mod(self.position + self.velocity, self.space.size)

        cell = self.model.grid.find_nearest_cell(self.position)
        self.last_cell_coordinate = cell.coordinate
        self.last_harvest = min(cell.resource, self.harvest_amount)
        cell.resource -= self.last_harvest
        self.energy += self.last_harvest
