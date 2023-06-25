import math

import mesa

from .resource_agents import Spice, Sugar


# Helper function
def get_distance(pos_1, pos_2):
    """
    Calculate the Euclidean distance between two positions

    used in trade.move()
    """

    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)


class Trader(mesa.Agent):
    """
    Trader:
    - has a metabolism of sugar and spice
    - harvest and trade sugar and spice to survive
    """

    def __init__(
        self,
        unique_id,
        model,
        pos,
        moore=False,
        sugar=0,
        spice=0,
        metabolism_sugar=0,
        metabolism_spice=0,
        vision=0,
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore
        self.sugar = sugar
        self.spice = spice
        self.metabolism_sugar = metabolism_sugar
        self.metabolism_spice = metabolism_spice
        self.vision = vision
        self.prices = []
        self.trade_partners = []

    def get_sugar(self, pos):
        """
        used in self.get_sugar_amount()
        """

        this_cell = self.model.grid.get_cell_list_contents(pos)
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent
        return None

    def get_sugar_amount(self, pos):
        """
        used in self.move() as part of self.calculate_welfare()
        """

        sugar_patch = self.get_sugar(pos)
        if sugar_patch:
            return sugar_patch.amount
        return 0

    def get_spice(self, pos):
        """
        used in self.get_spice_amount()
        """

        this_cell = self.model.grid.get_cell_list_contents(pos)
        for agent in this_cell:
            if type(agent) is Spice:
                return agent
        return None

    def get_spice_amount(self, pos):
        """
        used in self.move() as part of self.calculate_welfare()
        """

        spice_patch = self.get_spice(pos)
        if spice_patch:
            return spice_patch.amount
        return 0

    def get_trader(self, pos):
        """
        helper function used in self.trade_with_neighbors()
        """

        this_cell = self.model.grid.get_cell_list_contents(pos)

        for agent in this_cell:
            if isinstance(agent, Trader):
                return agent

    def is_occupied_by_other(self, pos):
        """
        helper function part 1 of self.move()
        """

        if pos == self.pos:
            # agent's position is considered unoccupied as agent can stay there
            return False
        # get contents of each cell in neighborhood
        this_cell = self.model.grid.get_cell_list_contents(pos)
        return any(isinstance(a, Trader) for a in this_cell)

    def calculate_welfare(self, sugar, spice):
        """
        helper function

        part 2 self.move()
        self.trade()
        """

        # calculate total resources
        m_total = self.metabolism_sugar + self.metabolism_spice
        # Cobb-Douglas functional form; starting on p. 97
        # on Growing Artificial Societies
        return sugar ** (self.metabolism_sugar / m_total) * spice ** (
            self.metabolism_spice / m_total
        )

    def is_starved(self):
        """
        Helper function for self.maybe_die()
        """

        return (self.sugar <= 0) or (self.spice <= 0)

    def calculate_MRS(self, sugar, spice):
        """
        Helper function for
          - self.trade()
          - self.maybe_self_spice()

        Determines what trader agent needs and can give up
        """

        return (spice / self.metabolism_spice) / (sugar / self.metabolism_sugar)

    def calculate_sell_spice_amount(self, price):
        """
        helper function for self.maybe_sell_spice() which is called from
        self.trade()
        """

        if price >= 1:
            sugar = 1
            spice = int(price)
        else:
            sugar = int(1 / price)
            spice = 1
        return sugar, spice

    def sell_spice(self, other, sugar, spice):
        """
        used in self.maybe_sell_spice()

        exchanges sugar and spice between traders
        """

        self.sugar += sugar
        other.sugar -= sugar
        self.spice -= spice
        other.spice += spice

    def maybe_sell_spice(self, other, price, welfare_self, welfare_other):
        """
        helper function for self.trade()
        """

        sugar_exchanged, spice_exchanged = self.calculate_sell_spice_amount(price)

        # Assess new sugar and spice amount - what if change did occur
        self_sugar = self.sugar + sugar_exchanged
        other_sugar = other.sugar - sugar_exchanged
        self_spice = self.spice - spice_exchanged
        other_spice = other.spice + spice_exchanged

        # double check to ensure agents have resources

        if (
            (self_sugar <= 0)
            or (other_sugar <= 0)
            or (self_spice <= 0)
            or (other_spice <= 0)
        ):
            return False

        # trade criteria #1 - are both agents better off?
        both_agents_better_off = (
            welfare_self < self.calculate_welfare(self_sugar, self_spice)
        ) and (welfare_other < other.calculate_welfare(other_sugar, other_spice))

        # trade criteria #2 is their mrs crossing with potential trade
        mrs_not_crossing = self.calculate_MRS(
            self_sugar, self_spice
        ) > other.calculate_MRS(other_sugar, other_spice)

        if not (both_agents_better_off and mrs_not_crossing):
            return False

        # criteria met, execute trade
        self.sell_spice(other, sugar_exchanged, spice_exchanged)

        return True

    def trade(self, other):
        """
        helper function used in trade_with_neighbors()

        other is a trader agent object
        """

        # sanity check to verify code is working as expected
        assert self.sugar > 0
        assert self.spice > 0
        assert other.sugar > 0
        assert other.spice > 0

        # calculate marginal rate of substitution in Growing Artificial Societies p. 101
        mrs_self = self.calculate_MRS(self.sugar, self.spice)
        mrs_other = other.calculate_MRS(other.sugar, other.spice)

        # calculate each agents welfare
        welfare_self = self.calculate_welfare(self.sugar, self.spice)
        welfare_other = other.calculate_welfare(other.sugar, other.spice)

        if math.isclose(mrs_self, mrs_other):
            return

        # calcualte price
        price = math.sqrt(mrs_self * mrs_other)

        if mrs_self > mrs_other:
            # self is a sugar buyer, spice seller
            sold = self.maybe_sell_spice(other, price, welfare_self, welfare_other)
            # no trade - criteria not met
            if not sold:
                return
        else:
            # self is a spice buyer, sugar seller
            sold = other.maybe_sell_spice(self, price, welfare_other, welfare_self)
            # no trade - criteria not met
            if not sold:
                return

        # Capture data
        self.prices.append(price)
        self.trade_partners.append(other.unique_id)

        # continue trading
        self.trade(other)

    ######################################################################
    #                                                                    #
    #                      MAIN TRADE FUNCTIONS                          #
    #                                                                    #
    ######################################################################

    def move(self):
        """
        Function for trader agent to identify optimal move for each step in 4 parts
        1 - identify all possible moves
        2 - determine which move maximizes welfare
        3 - find closest best option
        4 - move
        """

        # 1. identify all possible moves

        neighbors = [
            i
            for i in self.model.grid.get_neighborhood(
                self.pos, self.moore, True, self.vision
            )
            if not self.is_occupied_by_other(i)
        ]

        # 2. determine which move maximizes welfare

        welfares = [
            self.calculate_welfare(
                self.sugar + self.get_sugar_amount(pos),
                self.spice + self.get_spice_amount(pos),
            )
            for pos in neighbors
        ]

        # 3. Find closest best option

        # find the highest welfare in welfares
        max_welfare = max(welfares)
        # get the index of max welfare cells
        candidate_indices = [
            i for i in range(len(welfares)) if math.isclose(welfares[i], max_welfare)
        ]

        # convert index to positions of those cells
        candidates = [neighbors[i] for i in candidate_indices]

        min_dist = min(get_distance(self.pos, pos) for pos in candidates)

        final_candidates = [
            pos
            for pos in candidates
            if math.isclose(get_distance(self.pos, pos), min_dist, rel_tol=1e-02)
        ]
        final_candidate = self.random.choice(final_candidates)

        # 4. Move Agent
        self.model.grid.move_agent(self, final_candidate)

    def eat(self):
        # get sugar
        sugar_patch = self.get_sugar(self.pos)

        if sugar_patch:
            self.sugar += sugar_patch.amount
            sugar_patch.amount = 0
        self.sugar -= self.metabolism_sugar

        # get_spice
        spice_patch = self.get_spice(self.pos)

        if spice_patch:
            self.spice += spice_patch.amount
            spice_patch.amount = 0
        self.spice -= self.metabolism_spice

    def maybe_die(self):
        """
        Function to remove Traders who have consumed all their sugar or spice
        """

        if self.is_starved():
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def trade_with_neighbors(self):
        """
        Function for trader agents to decide who to trade with in three parts

        1- identify neighbors who can trade
        2- trade (2 sessions)
        3- collect data
        """

        neighbor_agents = [
            self.get_trader(pos)
            for pos in self.model.grid.get_neighborhood(
                self.pos, self.moore, False, self.vision
            )
            if self.is_occupied_by_other(pos)
        ]

        if len(neighbor_agents) == 0:
            return

            # iterate through traders in neighboring cells and trade
        for a in neighbor_agents:
            if a:
                self.trade(a)

        return
