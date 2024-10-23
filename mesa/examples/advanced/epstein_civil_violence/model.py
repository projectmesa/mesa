import mesa

from mesa.examples.advanced.epstein_civil_violence.agents import Citizen, Cop


class EpsteinCivilViolence(mesa.Model):
    """
    Model 1 from "Modeling civil violence: An agent-based computational
    approach," by Joshua Epstein.
    http://www.pnas.org/content/99/suppl_3/7243.full
    Attributes:
        height: grid height
        width: grid width
        citizen_density: approximate % of cells occupied by citizens.
        cop_density: approximate % of cells occupied by cops.
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

    def __init__(
        self,
        width=40,
        height=40,
        citizen_density=0.7,
        cop_density=0.074,
        citizen_vision=7,
        cop_vision=7,
        legitimacy=0.8,
        max_jail_term=1000,
        active_threshold=0.1,
        arrest_prob_constant=2.3,
        movement=True,
        max_iters=1000,
        seed=None
    ):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.citizen_density = citizen_density
        self.cop_density = cop_density
        self.citizen_vision = citizen_vision
        self.cop_vision = cop_vision
        self.legitimacy = legitimacy
        self.max_jail_term = max_jail_term
        self.active_threshold = active_threshold
        self.arrest_prob_constant = arrest_prob_constant
        self.movement = movement
        self.max_iters = max_iters
        self.iteration = 0

        self.grid = mesa.experimental.cell_space.OrthogonalMooreGrid((width, height), capacity=1, torus=True, random=self.random)

        model_reporters = {
            "Quiescent": lambda m: self.count_type_citizens(m, "Quiescent"),
            "Active": lambda m: self.count_type_citizens(m, "Active"),
            "Jailed": self.count_jailed,
            "Cops": self.count_cops,
        }
        agent_reporters = {
            "x": lambda a: a.cell.coordinate[0],
            "y": lambda a: a.cell.coordinate[1],
            "breed": lambda a: type(a).__name__,
            "jail_sentence": lambda a: getattr(a, "jail_sentence", None),
            "condition": lambda a: getattr(a, "condition", None),
            "arrest_probability": lambda a: getattr(a, "arrest_probability", None),
        }
        self.datacollector = mesa.DataCollector(
            model_reporters=model_reporters, agent_reporters=agent_reporters
        )
        if self.cop_density + self.citizen_density > 1:
            raise ValueError("Cop density + citizen density must be less than 1")

        for cell in self.grid.all_cells:
            if self.random.random() < self.cop_density:
                cop = Cop(self, vision=self.cop_vision)
                cop.move_to(cell)

            elif self.random.random() < (self.cop_density + self.citizen_density):
                citizen = Citizen(
                    self,
                    hardship=self.random.random(),
                    regime_legitimacy=self.legitimacy,
                    risk_aversion=self.random.random(),
                    threshold=self.active_threshold,
                    vision=self.citizen_vision,
                )
                citizen.move_to(cell)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step and collect data.
        """
        self.agents.shuffle_do("step")
        # collect data
        self.datacollector.collect(self)
        self.iteration += 1
        if self.iteration > self.max_iters:
            self.running = False

    @staticmethod
    def count_type_citizens(model, condition, exclude_jailed=True):
        """
        Helper method to count agents by Quiescent/Active.
        """
        citizens = model.agents_by_type[Citizen]

        if exclude_jailed:
            return len(
                [
                    c
                    for c in citizens
                    if (c.condition == condition) and (c.jail_sentence == 0)
                ]
            )
        else:
            return len([c for c in citizens if c.condition == condition])

    @staticmethod
    def count_jailed(model):
        """
        Helper method to count jailed agents.
        """
        return len([a for a in model.agents_by_type[Citizen] if a.jail_sentence > 0])

    @staticmethod
    def count_cops(model):
        """
        Helper method to count jailed agents.
        """
        return len(model.agents_by_type[Cop])
