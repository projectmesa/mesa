from mesa import Agent, Model


class SchellingAgent(Agent):
    """
    Schelling segregation agent
    """

    def __init__(self, model: Model, agent_type: int) -> None:
        """
        Create a new Schelling agent.

        Args:
           agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(model)
        self.type = agent_type

    def step(self) -> None:
        neighbors = self.model.grid.iter_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )
        similar = sum(1 for neighbor in neighbors if neighbor.type == self.type)

        # If unhappy, move:
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1
