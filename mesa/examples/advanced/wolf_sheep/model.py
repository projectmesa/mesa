"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import math
import random

import numpy as np

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.examples.advanced.wolf_sheep.agents import GrassPatch, Sheep, Wolf
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
from mesa.experimental.cell_space.property_layer import PropertyLayer
from mesa.experimental.devs import ABMSimulator


def is_trapped_in_wall(
    cell, wall_coord, width, height
):  # true if cell is trapped of walls
    north = (cell.coordinate[0] - 1, cell.coordinate[1])
    south = (cell.coordinate[0] + 1, cell.coordinate[1])
    west = (cell.coordinate[0], cell.coordinate[1] - 1)
    east = (cell.coordinate[0], cell.coordinate[1] + 1)

    coord = (cell.coordinate[0], cell.coordinate[1])

    # 'corner' cases (pun intended)
    if coord == (0, 0):  # top left corner
        return {east, south}.issubset(wall_coord)
    if coord == (height - 1, 0):  # bottom left corner
        return {north, east}.issubset(wall_coord)
    if coord == (0, width - 1):  # top right corner
        return {west, south}.issubset(wall_coord)
    if coord == (height - 1, width - 1):  # bottom right corner
        return {north, west}.issubset(wall_coord)

    return {north, south, west, east}.issubset(wall_coord)


class WolfSheep(Model):
    """Wolf-Sheep Predation Model.

    A model for simulating wolf and sheep (predator-prey) ecosystem modelling.
    """

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        width=20,
        height=20,
        initial_sheep=100,
        initial_wolves=50,
        sheep_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass=True,
        grass_regrowth_time=30,
        sheep_gain_from_food=4,
        seed=None,
        simulator: ABMSimulator = None,
    ):
        """Create a new Wolf-Sheep model with the given parameters.

        Args:
            height: Height of the grid
            width: Width of the grid
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled
            seed: Random seed
            simulator: ABMSimulator instance for event scheduling
        """
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)

        # Initialize model parameters
        self.height = height
        self.width = width
        self.grass = grass

        # Create grid using experimental cell space
        self.grid = OrthogonalVonNeumannGrid(
            (
                self.height,
                self.width,
            ),  # use tuple instead of list, otherwise it would fail the dimension check in add_property_layer
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        # Set up data collection
        model_reporters = {
            "Wolves": lambda m: len(m.agents_by_type[Wolf]),
            "Sheep": lambda m: len(m.agents_by_type[Sheep]),
        }
        if grass:
            model_reporters["Grass"] = lambda m: len(
                m.agents_by_type[GrassPatch].select(lambda a: a.fully_grown)
            )

        self.datacollector = DataCollector(model_reporters)

        wall_arr = [[False] * self.width for i in range(self.height)]

        wall_coord = {
            (random.randrange(self.height), random.randrange(self.width))
            for i in range((width * height) // 10)
        }  # set is used because the random number gen might return the same coordinate
        for i, j in wall_coord:
            wall_arr[i][j] = True

        wall_arr = np.array(wall_arr)

        self.grid.add_property_layer(PropertyLayer.from_data("wall", wall_arr))

        possible_cells = []
        for cell in self.grid.all_cells.cells:
            if (
                (
                    cell.coordinate[0],
                    cell.coordinate[1],
                )
                not in wall_coord
                and not is_trapped_in_wall(cell, wall_coord, width, height)
            ):  # so we don't create an animal at wall cells. and make sure the animal is not trapped in walls
                possible_cells.append(cell)

        # Create sheep:
        Sheep.create_agents(
            self,
            initial_sheep,
            energy=self.rng.random((initial_sheep,)) * 2 * sheep_gain_from_food,
            p_reproduce=sheep_reproduce,
            energy_from_food=sheep_gain_from_food,
            cell=self.random.choices(possible_cells, k=initial_sheep),
        )
        # Create Wolves:
        Wolf.create_agents(
            self,
            initial_wolves,
            energy=self.rng.random((initial_wolves,)) * 2 * wolf_gain_from_food,
            p_reproduce=wolf_reproduce,
            energy_from_food=wolf_gain_from_food,
            cell=self.random.choices(possible_cells, k=initial_wolves),
        )

        # Create grass patches if enabled
        if grass:
            possibly_fully_grown = [True, False]
            for cell in self.grid:
                fully_grown = self.random.choice(possibly_fully_grown)
                countdown = (
                    0 if fully_grown else self.random.randrange(0, grass_regrowth_time)
                )
                GrassPatch(self, countdown, grass_regrowth_time, cell)

        # Collect initial data
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """Execute one step of the model."""
        # First activate all sheep, then all wolves, both in random order
        self.agents_by_type[Sheep].shuffle_do("step")
        self.agents_by_type[Wolf].shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)
