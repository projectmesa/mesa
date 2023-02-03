import mesa


class Sugar(mesa.Agent):
    """
    Sugar:
    - contains an amount of sugar
    - grows 1 amount of sugar at each turn
    """

    def __init__(self, unique_id, model, pos, max_sugar):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        """
        Sugar growth function, adds one unit of sugar each step until
        max amount
        """
        self.amount = min([self.max_sugar, self.amount + 1])


class Spice(mesa.Agent):
    """
    Spice:
    - contains an amount of spice
    - grows 1 amount of spice at each turn
    """

    def __init__(self, unique_id, model, pos, max_spice):
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = max_spice
        self.max_spice = max_spice

    def step(self):
        """
        Spice growth function, adds one unit of spice each step until
        max amount
        """
        self.amount = min([self.max_spice, self.amount + 1])
