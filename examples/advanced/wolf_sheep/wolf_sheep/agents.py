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
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(model)
        self.fully_grown = fully_grown
        self.countdown = countdown

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
