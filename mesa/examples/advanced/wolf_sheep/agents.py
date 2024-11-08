from mesa.experimental.cell_space import CellAgent, FixedAgent


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

    def feed(self): ...

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
        if self.model.grass:
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
    def fully_grown(self):
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
