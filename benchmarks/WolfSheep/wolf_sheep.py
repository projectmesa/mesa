"""Wolf-Sheep Predation Model for performance benchmarking.

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import math

from mesa import Model
from mesa.experimental.cell_space import CellAgent, FixedAgent, OrthogonalVonNeumannGrid
from mesa.experimental.devs import ABMSimulator


class Animal(CellAgent):
    """The base animal class."""

    def __init__(self, model, energy, p_reproduce, energy_from_food, cell):
        """Initializes an animal.

        Args:
            model: a model instance
            energy: starting amount of energy
            p_reproduce: probability of sexless reproduction
            energy_from_food: energy obtained from 1 unit of food
            cell: the cell in which the animal starts
        """
        super().__init__(model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.cell = cell

    def spawn_offspring(self):
        """Create offspring."""
        self.energy /= 2
        self.__class__(
            self.model,
            self.energy,
            self.p_reproduce,
            self.energy_from_food,
            self.cell,
        )

    def feed(self): ...  # noqa: D102

    def step(self):
        """One step of the agent."""
        self.cell = self.cell.neighborhood.select_random_cell()
        self.energy -= 1

        self.feed()

        if self.energy < 0:
            self.remove()
        elif self.random.random() < self.p_reproduce:
            self.spawn_offspring()


class Sheep(Animal):
    """A sheep that walks around, reproduces (asexually) and gets eaten."""

    def feed(self):
        """If possible eat the food in the current location."""
        # If there is grass available, eat it
        grass_patch = next(
            obj for obj in self.cell.agents if isinstance(obj, GrassPatch)
        )
        if grass_patch.fully_grown:
            self.energy += self.energy_from_food
            grass_patch.fully_grown = False


class Wolf(Animal):
    """A wolf that walks around, reproduces (asexually) and eats sheep."""

    def feed(self):
        """If possible eat the food in the current location."""
        sheep = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy_from_food

            # Kill the sheep
            sheep_to_eat.remove()


class GrassPatch(FixedAgent):
    """A patch of grass that grows at a fixed rate and it is eaten by sheep."""

    @property
    def fully_grown(self):  # noqa: D102
        return self._fully_grown

    @fully_grown.setter
    def fully_grown(self, value: bool) -> None:
        self._fully_grown = value

        if not value:
            self.model.simulator.schedule_event_relative(
                setattr,
                self.grass_regrowth_time,
                function_args=[self, "fully_grown", True],
            )

    def __init__(self, model, countdown, grass_regrowth_time, cell):
        """Creates a new patch of grass.

        Args:
            model: a model instance
            countdown: Time for the patch of grass to be fully grown again
            grass_regrowth_time : time to fully regrow grass
            cell: the cell to which the patch of grass belongs
        """
        super().__init__(model)
        self._fully_grown = True if countdown == 0 else False  # Noqa: SIM210
        self.grass_regrowth_time = grass_regrowth_time
        self.cell = cell

        if not self.fully_grown:
            self.model.simulator.schedule_event_relative(
                setattr, countdown, function_args=[self, "fully_grown", True]
            )


class WolfSheep(Model):
    """Wolf-Sheep Predation Model.

    A model for simulating wolf and sheep (predator-prey) ecosystem modelling.
    """

    def __init__(
        self,
        simulator,
        height,
        width,
        initial_sheep,
        initial_wolves,
        sheep_reproduce,
        wolf_reproduce,
        grass_regrowth_time,
        wolf_gain_from_food=13,
        sheep_gain_from_food=5,
        seed=None,
    ):
        """Create a new Wolf-Sheep model with the given parameters.

        Args:
            simulator: ABMSimulator instance
            width: width of the grid
            height: height of the grid
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
            seed : the random seed
        """
        super().__init__(seed=seed)
        # Set parameters
        self.height = height
        self.width = width
        self.simulator = simulator

        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves

        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=False,
            capacity=math.inf,
            random=self.random,
        )

        # Create sheep:
        for _ in range(self.initial_sheep):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * sheep_gain_from_food)
            Sheep(self, energy, sheep_reproduce, sheep_gain_from_food, self.grid[pos])

        # Create wolves
        for _ in range(self.initial_wolves):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * wolf_gain_from_food)
            Wolf(self, energy, wolf_reproduce, wolf_gain_from_food, self.grid[pos])

        # Create grass patches
        possibly_fully_grown = [True, False]
        for cell in self.grid:
            fully_grown = self.random.choice(possibly_fully_grown)
            countdown = 0 if fully_grown else self.random.randrange(grass_regrowth_time)
            GrassPatch(self, countdown, grass_regrowth_time, cell)

    def step(self):
        """Run one step of the model."""
        self.agents_by_type[Sheep].shuffle_do("step")
        self.agents_by_type[Wolf].shuffle_do("step")


if __name__ == "__main__":
    import time

    simulator = ABMSimulator()
    model = WolfSheep(
        simulator,
        25,
        25,
        60,
        40,
        0.2,
        0.1,
        20,
        seed=15,
    )

    simulator.setup(model)

    start_time = time.perf_counter()
    simulator.run(100)
    print("Time:", time.perf_counter() - start_time)
