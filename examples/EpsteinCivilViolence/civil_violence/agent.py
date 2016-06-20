from mesa import Agent
import random
import math


class Citizen(Agent):
    """
    A member of the general population, may or may not be in active rebellion.
    Summary of rule: If grievance - risk > threshold, rebel.

    Attributes:
        unique_id: unique int
        x, y: Grid coordinates
        hardship: Agent's 'perceived hardship (i.e., physical or economic
            privation).' Exogenous, drawn from U(0,1).
        regime_legitimacy: Agent's perception of regime legitimacy, equal
            across agents.  Exogenous.
        risk_aversion: Exogenous, drawn from U(0,1).
        threshold: if (grievance - (risk_aversion * arrest_probability)) >
            threshold, go/remain Active
        vision: number of cells in each direction (N, S, E and W) that agent
            can inspect
        condition: Can be "Quiescent" or "Active;" deterministic function of
            greivance, perceived risk, and
        grievance: deterministic function of hardship and regime_legitimacy;
            how aggrieved is agent at the regime?
        arrest_probability: agent's assessment of arrest probability, given
            rebellion

    """

    def __init__(self, unique_id, pos, hardship, regime_legitimacy,
                 risk_aversion, threshold, vision, model):
        """
        Create a new Citizen.
        Args:
            unique_id: unique int
            x, y: Grid coordinates
            hardship: Agent's 'perceived hardship (i.e., physical or economic
                privation).' Exogenous, drawn from U(0,1).
            regime_legitimacy: Agent's perception of regime legitimacy, equal
                across agents.  Exogenous.
            risk_aversion: Exogenous, drawn from U(0,1).
            threshold: if (grievance - (risk_aversion * arrest_probability)) >
                threshold, go/remain Active
            vision: number of cells in each direction (N, S, E and W) that
                agent can inspect. Exogenous.
            model: model instance
        """
        super().__init__(unique_id, model)
        self.breed = 'citizen'
        self.pos = pos
        self.hardship = hardship
        self.regime_legitimacy = regime_legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.condition = "Quiescent"
        self.vision = vision
        self.jail_sentence = 0
        self.grievance = self.hardship * (1 - self.regime_legitimacy)
        self.arrest_probability = None

    def step(self, model):
        """
        Decide whether to activate, then move if applicable.
        """
        if self.jail_sentence:
            self.jail_sentence -= 1
            return  # no other changes or movements if agent is in jail.
        self.update_neighbors(model)
        self.update_estimated_arrest_probability(model)
        net_risk = self.risk_aversion * self.arrest_probability
        if self.condition == 'Quiescent' and (
                self.grievance - net_risk) > self.threshold:
            self.condition = 'Active'
        elif self.condition == 'Active' and (
                self.grievance - net_risk) <= self.threshold:
            self.condition = 'Quiescent'
        if model.movement and self.empty_neighbors:
            new_pos = random.choice(self.empty_neighbors)
            model.grid.move_agent(self, new_pos)

    def update_neighbors(self, model):
        """
        Look around and see who my neighbors are
        """
        self.neighborhood = model.grid.get_neighborhood(self.pos,
                                                        moore=False, radius=1)
        self.neighbors = model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [c for c in self.neighborhood if
                                model.grid.is_cell_empty(c)]

    def update_estimated_arrest_probability(self, model):
        """
        Based on the ratio of cops to actives in my neighborhood, estimate the
        p(Arrest | I go active).

        """
        cops_in_vision = len([c for c in self.neighbors if c.breed == 'cop'])
        actives_in_vision = 1.  # citizen counts herself
        for c in self.neighbors:
            if (c.breed == 'citizen' and
                    c.condition == 'Active' and
                    c.jail_sentence == 0):
                actives_in_vision += 1
        self.arrest_probability = 1 - math.exp(
            -1 * model.arrest_prob_constant * (
                cops_in_vision / actives_in_vision))


class Cop(Agent):
    """
    A cop for life.  No defection.
    Summary of rule: Inspect local vision and arrest a random active agent.

    Attributes:
        unique_id: unique int
        x, y: Grid coordinates
        vision: number of cells in each direction (N, S, E and W) that cop is
            able to inspect
    """

    def __init__(self, unique_id, pos, vision, model):
        """
        Create a new Cop.
        Args:
            unique_id: unique int
            x, y: Grid coordinates
            vision: number of cells in each direction (N, S, E and W) that
                agent can inspect. Exogenous.
            model: model instance
        """
        super().__init__(unique_id, model)
        self.breed = 'cop'
        self.pos = pos
        self.vision = vision

    def step(self, model):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """
        self.update_neighbors(model)
        active_neighbors = []
        for agent in self.neighbors:
            if agent.breed == 'citizen' and \
                    agent.condition == 'Active' and \
                    agent.jail_sentence == 0:
                active_neighbors.append(agent)
        if active_neighbors:
            arrestee = random.choice(active_neighbors)
            sentence = random.randint(0, model.max_jail_term)
            arrestee.jail_sentence = sentence
        if model.movement and self.empty_neighbors:
            new_pos = random.choice(self.empty_neighbors)
            model.grid.move_agent(self, new_pos)

    def update_neighbors(self, model):
        """
        Look around and see who my neighbors are.
        """
        self.neighborhood = model.grid.get_neighborhood(self.pos,
                                                        moore=False, radius=1)
        self.neighbors = model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [c for c in self.neighborhood if
                                model.grid.is_cell_empty(c)]
