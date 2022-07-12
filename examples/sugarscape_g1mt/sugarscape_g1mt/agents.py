import math

import mesa

# Note: GAS refers to the book by Epstein, "Growing Artificial Societies:
# Social Science from the Bottom Up," published in 1996.


def get_distance(pos_1, pos_2):
    """Calculate Euclidean distance between two positions.
    Args:
        pos_1, pos_2: Coordinate tuples for both points.
    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)


class Sugar(mesa.Agent):
    """
    Sugar is a FSM that
    - contains an amount of sugar
    - grows 1 amount of sugar at each turn (Epstein's rule G1).
    """

    def __init__(self, pos, model, max_sugar):
        super().__init__(pos, model)
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        self.amount = min([self.max_sugar, self.amount + 1])


class Spice(mesa.Agent):
    """
    Spice is a FSM that
    - contains an amount of spice
    - grows 1 amount of spice at each turn (Epstein's rule G1).
    """

    def __init__(self, pos, model, max_spice):
        super().__init__(pos, model)
        self.amount = max_spice
        self.max_spice = max_spice

    def step(self):
        self.amount = min([self.max_spice, self.amount + 1])


class Trader(mesa.Agent):
    def __init__(
        self,
        pos,
        model,
        moore=False,
        sugar=0,
        spice=0,
        metabolism_sugar=0,
        metabolism_spice=0,
        vision=0,
    ):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.sugar = sugar
        self.spice = spice
        self.metabolism_sugar = metabolism_sugar
        self.metabolism_spice = metabolism_spice
        self.vision = vision

        self.prices = []

    def get_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent
        return None

    def get_sugar_amount(self, pos):
        sugar_patch = self.get_sugar(pos)
        if sugar_patch:
            return sugar_patch.amount
        return 0

    def get_spice(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if isinstance(agent, Spice):
                return agent
        return None

    def get_spice_amount(self, pos):
        spice_patch = self.get_spice(pos)
        if spice_patch:
            return spice_patch.amount
        return 0

    def get_trader(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if isinstance(agent, Trader):
                return agent

    def is_occupied(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for a in this_cell:
            if isinstance(a, Trader):
                return True
        return False

    def move(self):
        # Epstein multicommodity agent movement rule M.
        # See GAS page 98-99.

        # Our extra sanity check. The agent must still have enough resource
        # before the movement.
        assert self.sugar > 0
        assert self.spice > 0

        # 1. Get neighborhood within vision.
        neighbors = [
            i
            for i in self.model.grid.get_neighborhood(
                self.pos, self.moore, False, radius=self.vision
            )
            if not self.is_occupied(i)
        ]
        # TODO maybe just use include_center
        neighbors.append(self.pos)

        # 2. Find the patch which produces maximum welfare.
        eps = 1e-7
        welfares = [
            self.calculate_welfare(
                self.sugar + self.get_sugar_amount(pos),
                self.spice + self.get_spice_amount(pos),
            )
            for pos in neighbors
        ]
        max_welfare = max(welfares)
        candidate_indices = [
            i for i in range(len(welfares)) if abs(welfares[i] - max_welfare) < eps
        ]
        candidates = [neighbors[i] for i in candidate_indices]

        # 3. Find the nearest patch among the candidate.
        min_dist = min([get_distance(self.pos, pos) for pos in candidates])
        final_candidates = [
            pos
            for pos in candidates
            if abs(get_distance(self.pos, pos) - min_dist) < eps
        ]
        self.random.shuffle(final_candidates)

        # 4. Move agent.
        self.model.grid.move_agent(self, final_candidates[0])

    def eat(self):
        # Fetch sugar and spice patch
        sugar_patch = self.get_sugar(self.pos)
        # Sometimes the position has absolutely no sugar content, and so we
        # check for its existence.
        if sugar_patch:
            self.sugar = self.sugar - self.metabolism_sugar + sugar_patch.amount
            sugar_patch.amount = 0

        spice_patch = self.get_spice(self.pos)
        # Likewise for spice.
        if spice_patch:
            self.spice = self.spice - self.metabolism_spice + spice_patch.amount
            spice_patch.amount = 0

    def is_starved(self):
        return (self.sugar <= 0) or (self.spice <= 0)

    def maybe_die(self):
        if self.is_starved():
            # Starved to death
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def calculate_sell_spice_amount(self, price):
        # GAS page 105.
        # The quantities to be exchanged are as follows: if p > 1 then p units
        # of spice for 1 unit of sugar; if p < 1 then 1/p units of sugar for 1
        # unit of spice.
        if price >= 1:
            sugar = 1
            spice = int(price)
        else:
            sugar = int(1 / price)
            spice = 1
        return sugar, spice

    def sell_spice(self, other, sugar, spice):
        self.sugar += sugar
        other.sugar -= sugar
        self.spice -= spice
        other.spice += spice

    def maybe_sell_spice(self, other, price, welfare_self, welfare_other):
        sugar_exchanged, spice_exchanged = self.calculate_sell_spice_amount(price)
        # Preparing the new sugar spice amount -- what if the exchange were to occur.
        self_sugar = self.sugar + sugar_exchanged
        other_sugar = other.sugar - sugar_exchanged
        self_spice = self.spice - spice_exchanged
        other_spice = other.spice + spice_exchanged

        # Our extra rule (not specified by Epstein) to prevent the
        # buyer/seller running out of sugar/spice.
        if (
            (self_sugar <= 0)
            or (other_sugar <= 0)
            or (self_spice <= 0)
            or (other_spice <= 0)
        ):
            return False

        both_agents_better_off = (
            welfare_self < self.calculate_welfare(self_sugar, self_spice)
        ) and (welfare_other < other.calculate_welfare(other_sugar, other_spice))
        mrs_not_crossing = self.calculate_MRS(
            self_sugar, self_spice
        ) > other.calculate_MRS(other_sugar, other_spice)
        if not (both_agents_better_off and mrs_not_crossing):
            # To prevent infinite loop of trading.
            return False

        # Perform the actual sell operation
        self.sell_spice(other, sugar_exchanged, spice_exchanged)
        return True

    def trade_with_neighbors(self):
        # von Neumann neighbors
        neighbor_agents = [
            self.get_trader(pos)
            for pos in self.model.grid.get_neighborhood(
                self.pos, self.moore, False, radius=self.vision
            )
            if self.is_occupied(pos)
        ]
        if len(neighbor_agents) == 0:
            return []

        self.random.shuffle(neighbor_agents)
        count = 0
        for a in neighbor_agents:
            if a:
                self.trade(a)
                count += 1
        if count > 0:
            prices = [p for p in self.prices if p]
            self.prices = []
            return prices
        return []

    def trade(self, other):
        # Epstein rule T for a pair of agents, page 105

        # Our extra sanity check. The agent must still have enough resource
        # before the trade.
        assert self.sugar > 0
        assert self.spice > 0

        # This may happen if other agent no longer has enough resource, but has
        # yet to execute maybe_die.
        if other.sugar <= 0 or other.spice <= 0:
            return

        # Agent and neighbor compute their MRSs; if these are equal then end,
        # else continue
        mrs_self = self.calculate_MRS()
        welfare_self = self.calculate_welfare()
        welfare_other = other.calculate_welfare()
        mrs_other = other.calculate_MRS()
        if math.isclose(mrs_self, mrs_other):
            return

        # The direction of exchange is as follows: spice flows from the
        # agent with the higher MRS to the agent with the lower MRS
        # while, sugar goes in the opposite direction

        # The geometric mean of the two MRSsis calculated- this will serve as
        # the price, p.
        if mrs_self < 1e-6 or mrs_other < 1e-6:
            return
        price = math.sqrt(mrs_self * mrs_other)
        self.prices.append(price)

        # If this trade will (a) make both agents better off (increases the
        # welfare of both agents), and (b) not cause the agents' MRSs to cross
        # over one another, then the trade is made and return to start, else
        # end.
        if mrs_self > mrs_other:
            # self is a sugar buyer
            sold = self.maybe_sell_spice(other, price, welfare_self, welfare_other)
            if not sold:
                return
        else:
            # self is a spice buyer
            sold = other.maybe_sell_spice(self, price, welfare_other, welfare_self)
            if not sold:
                return
        # continue trading
        self.trade(other)

    def calculate_welfare(self, sugar=None, spice=None):
        # Calculate the welfare given sugar and spice amount.
        # See GAS page 97 equation 1.
        if sugar is None:
            # If not specified, then use the whole sugar in possession.
            sugar = self.sugar
        if spice is None:
            # If not specified, then use the whole spice in possession.
            spice = self.spice

        if sugar < 0 or spice < 0:
            return 0.0

        m_total = self.metabolism_sugar + self.metabolism_spice
        # Note that this is a Cobb-Douglas functional form.
        return sugar ** (self.metabolism_sugar / m_total) * spice ** (
            self.metabolism_spice / m_total
        )

    def calculate_MRS(self, sugar=None, spice=None):
        # Calculate the MRS given sugar and spice amount.
        if sugar is None:
            # If not specified, then use the whole sugar in possession.
            sugar = self.sugar
        if spice is None:
            # If not specified, then use the whole spice in possession.
            spice = self.spice
        # See GAS page 102 equation 3.
        return (spice / self.metabolism_spice) / (sugar / self.metabolism_sugar)
