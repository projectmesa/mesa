"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa
from mesa.experimental.devs.simulator import ABMSimulator


class Animal(mesa.Agent):
    def __init__(self, unique_id, model, moore, energy, p_reproduce, energy_from_food):
        super().__init__(unique_id, model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.moore = moore

    def random_move(self):
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

    def spawn_offspring(self):
        self.energy /= 2
        offspring = self.__class__(
            self.model.next_id(),
            self.model,
            self.moore,
            self.energy,
            self.p_reproduce,
            self.energy_from_food,
        )
        self.model.grid.place_agent(offspring, self.pos)

    def feed(self): ...

    def die(self):
        self.model.grid.remove_agent(self)
        self.remove()

    def step(self):
        self.random_move()
        self.energy -= 1

        self.feed()

        if self.energy < 0:
            self.die()
        elif self.random.random() < self.p_reproduce:
            self.spawn_offspring()


class Sheep(Animal):
    """
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    """

    def feed(self):
        # If there is grass available, eat it
        agents = self.model.grid.get_cell_list_contents(self.pos)
        grass_patch = next(obj for obj in agents if isinstance(obj, GrassPatch))
        if grass_patch.fully_grown:
            self.energy += self.energy_from_food
            grass_patch.fully_grown = False


class Wolf(Animal):
    """
    A wolf that walks around, reproduces (asexually) and eats sheep.
    """

    def feed(self):
        agents = self.model.grid.get_cell_list_contents(self.pos)
        sheep = [obj for obj in agents if isinstance(obj, Sheep)]
        if len(sheep) > 0:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy

            # Kill the sheep
            sheep_to_eat.die()


class GrassPatch(mesa.Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    @property
    def fully_grown(self) -> bool:
        return self._fully_grown

    @fully_grown.setter
    def fully_grown(self, value: bool):
        self._fully_grown = value

        if not value:
            self.model.simulator.schedule_event_relative(
                setattr,
                self.grass_regrowth_time,
                function_args=[self, "fully_grown", True],
            )

    def __init__(self, unique_id, model, fully_grown, countdown, grass_regrowth_time):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self._fully_grown = fully_grown
        self.grass_regrowth_time = grass_regrowth_time

        if not self.fully_grown:
            self.model.simulator.schedule_event_relative(
                setattr, countdown, function_args=[self, "fully_grown", True]
            )

    def set_fully_grown(self):
        self.fully_grown = True


class WolfSheep(mesa.Model):
    """
    Wolf-Sheep Predation Model

    A model for simulating wolf and sheep (predator-prey) ecosystem modelling.
    """

    def __init__(
        self,
        height,
        width,
        initial_sheep,
        initial_wolves,
        sheep_reproduce,
        wolf_reproduce,
        grass_regrowth_time,
        wolf_gain_from_food=13,
        sheep_gain_from_food=5,
        moore=False,
        simulator=None,
        seed=None,
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
            moore:
        """
        super().__init__(seed=seed)
        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.simulator = simulator

        # self.sheep_reproduce = sheep_reproduce
        # self.wolf_reproduce = wolf_reproduce
        # self.grass_regrowth_time = grass_regrowth_time
        # self.wolf_gain_from_food = wolf_gain_from_food
        # self.sheep_gain_from_food = sheep_gain_from_food
        # self.moore = moore

        self.grid = mesa.space.MultiGrid(self.height, self.width, torus=False)

        for _ in range(self.initial_sheep):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * sheep_gain_from_food)
            sheep = Sheep(
                self.next_id(),
                self,
                moore,
                energy,
                sheep_reproduce,
                sheep_gain_from_food,
            )
            self.grid.place_agent(sheep, pos)

        # Create wolves
        for _ in range(self.initial_wolves):
            pos = (
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            energy = self.random.randrange(2 * wolf_gain_from_food)
            wolf = Wolf(
                self.next_id(),
                self,
                moore,
                energy,
                wolf_reproduce,
                wolf_gain_from_food,
            )
            self.grid.place_agent(wolf, pos)

        # Create grass patches
        possibly_fully_grown = [True, False]
        for _agent, pos in self.grid.coord_iter():
            fully_grown = self.random.choice(possibly_fully_grown)
            if fully_grown:
                countdown = grass_regrowth_time
            else:
                countdown = self.random.randrange(grass_regrowth_time)
            patch = GrassPatch(
                self.next_id(), self, fully_grown, countdown, grass_regrowth_time
            )
            self.grid.place_agent(patch, pos)

    def step(self):
        """Perform one step of the model."""
        self.agents_by_type[Sheep].shuffle_do("step")
        self.agents_by_type[Wolf].shuffle_do("step")


if __name__ == "__main__":
    import time

    simulator = ABMSimulator()

    model = WolfSheep(25, 25, 60, 40, 0.2, 0.1, 20, simulator=simulator, seed=15)

    simulator.setup(model)

    start_time = time.perf_counter()
    simulator.run(100)
    print(simulator.time)
    print("Time:", time.perf_counter() - start_time)
