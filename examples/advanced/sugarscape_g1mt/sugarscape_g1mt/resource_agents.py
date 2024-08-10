import mesa


class Resource(mesa.Agent):
    """
    Resource:
    - contains an amount of sugar and spice
    - grows 1 amount of sugar at each turn
    - grows 1 amount of spice at each turn
    """

    def __init__(self, unique_id, model, max_sugar, max_spice):
        super().__init__(unique_id, model)
        self.sugar_amount = max_sugar
        self.max_sugar = max_sugar
        self.spice_amount = max_spice
        self.max_spice = max_spice

    def step(self):
        """
        Growth function, adds one unit of sugar and spice each step up to
        max amount
        """
        self.sugar_amount = min([self.max_sugar, self.sugar_amount + 1])
        self.spice_amount = min([self.max_spice, self.spice_amount + 1])
