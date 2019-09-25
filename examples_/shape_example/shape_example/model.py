from mesa import Model, Agent
from mesa.space import SingleGrid
from mesa.time import RandomActivation


class Walker(Agent):
    def __init__(self, unique_id, model, pos, heading=(1, 0)):
        super().__init__(unique_id, model)
        self.pos = pos
        self.heading = heading
        self.headings = {(1, 0), (0, 1), (-1, 0), (0, -1)}


class ShapeExample(Model):
    def __init__(self, N=2, width=20, height=10):
        self.N = N    # num of agents
        self.headings = ((1, 0), (0, 1), (-1, 0), (0, -1))  # tuples are fast
        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.make_walker_agents()
        self.running = True

    def make_walker_agents(self):
        unique_id = 0
        while True:
            if unique_id == self.N:
                break
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            pos = (x, y)
            heading = self.random.choice(self.headings)
            # heading = (1, 0)
            if self.grid.is_cell_empty(pos):
                print("Creating agent {2} at ({0}, {1})"
                      .format(x, y, unique_id))
                a = Walker(unique_id, self, pos, heading)
                self.schedule.add(a)
                self.grid.place_agent(a, pos)
                unique_id += 1

    def step(self):
        self.schedule.step()
