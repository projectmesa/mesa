"""Continuous movement with manual discrete-grid resource interactions."""

import numpy as np

from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.examples.experimental.continuous_grid_forager.agents import Forager
from mesa.experimental.continuous_space import ContinuousSpace
from mesa.experimental.scenarios import Scenario


class ForagerScenario(Scenario):
    """Parameters for the continuous-grid forager example."""

    width: int = 4
    height: int = 3
    harvest_amount: float = 2.0


class ContinuousGridForager(Model):
    """One forager that moves continuously and harvests from discrete cells."""

    def __init__(self, scenario: ForagerScenario = ForagerScenario):
        super().__init__(scenario=scenario)

        dimensions = (scenario.width, scenario.height)
        self.space = ContinuousSpace(
            [[0, scenario.width], [0, scenario.height]],
            torus=True,
            random=self.random,
            n_agents=1,
        )
        self.grid = OrthogonalMooreGrid(
            dimensions, torus=True, random=self.random
        )

        self.grid.create_property_layer("resource", dtype=float)
        self.grid.resource[:] = np.arange(
            1, scenario.width * scenario.height + 1, dtype=float
        ).reshape(dimensions)

        self.forager = Forager(
            self,
            self.space,
            position=(0.25, 0.25),
            velocity=(1.0, 0.0),
            harvest_amount=scenario.harvest_amount,
        )

    def step(self):
        """Advance the forager by one movement-and-harvest step."""
        self.forager.step()


if __name__ == "__main__":
    model = ContinuousGridForager()
    starting_cell = model.grid.find_nearest_cell(model.forager.position)
    print(
        f"start: position={tuple(model.forager.position)}, "
        f"cell={starting_cell.coordinate}, resource={starting_cell.resource:.1f}"
    )

    for step in range(1, 4):
        model.step()
        cell = model.grid.find_nearest_cell(model.forager.position)
        print(
            f"step {step}: position={tuple(model.forager.position)}, "
            f"cell={cell.coordinate}, harvested={model.forager.last_harvest:.1f}, "
            f"energy={model.forager.energy:.1f}, resource={cell.resource:.1f}"
        )
