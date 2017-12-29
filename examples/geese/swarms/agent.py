from mesa import Agent


class SwarmAgent(Agent):
    """ An minimalistic swarm agent """
    def __init__(self, unique_id, model):
        super().__init__(unique_id,model)
        self.wealth = 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()

    def advance(self):
        pass

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore = True,
            include_center = False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice (cellmates)
            other.wealth += 1
            self.wealth -= 1
