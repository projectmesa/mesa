import random
import math

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector


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
        super(Citizen, self).__init__(unique_id, model)
        self.breed = 'citizen'
        self.unique_id = unique_id
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
        super(Cop, self).__init__(unique_id, model)
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


class CivilViolenceModel(Model):
    """
    Model 1 from "Modeling civil violence: An agent-based computational
    approach," by Joshua Epstein.
    http://www.pnas.org/content/99/suppl_3/7243.full
    Attributes:
        height: grid height
        width: grid width
        citizen_density: approximate % of cells occupied by citizens.
        cop_density: approximate % of calles occupied by cops.
        citizen_vision: number of cells in each direction (N, S, E and W) that
            citizen can inspect
        cop_vision: number of cells in each direction (N, S, E and W) that cop
            can inspect
        legitimacy:  (L) citizens' perception of regime legitimacy, equal
            across all citizens
        max_jail_term: (J_max)
        active_threshold: if (grievance - (risk_aversion * arrest_probability))
            > threshold, citizen rebels
        arrest_prob_constant: set to ensure agents make plausible arrest
            probability estimates
        movement: binary, whether agents try to move at step end
        max_iters: model may not have a natural stopping point, so we set a
            max.

    """

    def __init__(self, height, width, citizen_density, cop_density,
                 citizen_vision, cop_vision, legitimacy,
                 max_jail_term, active_threshold=.1, arrest_prob_constant=2.3,
                 movement=True, max_iters=1000):
        super(CivilViolenceModel, self).__init__()
        self.height = height
        self.width = width
        self.citizen_density = citizen_density
        self.cop_density = cop_density
        self.citizen_vision = citizen_vision
        self.cop_vision = cop_vision
        self.legitimacy = legitimacy
        self.max_jail_term = max_jail_term
        self.active_threshold = active_threshold
        self.arrest_prob_constant = arrest_prob_constant
        self.movement = movement
        self.running = True
        self.max_iters = max_iters
        self.iteration = 0
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=True)
        model_reporters = {
            "Quiescent": lambda m: self.count_type_citizens(m, "Quiescent"),
            "Active": lambda m: self.count_type_citizens(m, "Active"),
            "Jailed": lambda m: self.count_jailed(m)}
        agent_reporters = {
            "x": lambda a: a.pos[0],
            "y": lambda a: a.pos[1],
            'breed': lambda a: a.breed,
            "jail_sentence": lambda a: getattr(a, 'jail_sentence', None),
            "condition": lambda a: getattr(a, "condition", None),
            "arrest_probability": lambda a: getattr(a, "arrest_probability",
                                                    None)
        }
        self.dc = DataCollector(model_reporters=model_reporters,
                                agent_reporters=agent_reporters)
        unique_id = 0
        if self.cop_density + self.citizen_density > 1:
            raise ValueError(
                'Cop density + citizen density must be less than 1')
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.cop_density:
                cop = Cop(unique_id, (x, y), vision=self.cop_vision,
                          model=self)
                unique_id += 1
                self.grid[y][x] = cop
                self.schedule.add(cop)
            elif random.random() < (
                    self.cop_density + self.citizen_density):
                citizen = Citizen(unique_id, (x, y),
                                  hardship=random.random(),
                                  regime_legitimacy=self.legitimacy,
                                  risk_aversion=random.random(),
                                  threshold=self.active_threshold,
                                  vision=self.citizen_vision, model=self)
                unique_id += 1
                self.grid[y][x] = citizen
                self.schedule.add(citizen)

    def step(self):
        """
        Advance the model by one step and collect data.
        """
        self.schedule.step()
        self.dc.collect(self)
        self.iteration += 1
        if self.iteration > self.max_iters:
            self.running = False

    @staticmethod
    def count_type_citizens(model, condition, exclude_jailed=True):
        """
        Helper method to count agents by Quiescent/Active.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == 'cop':
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.condition == condition:
                count += 1
        return count

    @staticmethod
    def count_jailed(model):
        """
        Helper method to count jailed agents.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == 'citizen' and agent.jail_sentence:
                count += 1
        return count
