from mesa import Agent


class SchellingAgent(Agent):
    """Schelling segregation agent."""

    def __init__(self, model, agent_type: int) -> None:
        """Create a new Schelling agent.
        Args:
            model: The model instance the agent belongs to
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(model)
        self.type = agent_type

    def step(self) -> None:
        """Determine if agent is happy and move if necessary."""
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )

        # Count similar neighbors
        similar_neighbors = len([n for n in neighbors if n.type == self.type])

        # Calculate the fraction of similar neighbors
        if (valid_neighbors := len(neighbors) )> 0:
            similarity_fraction = similar_neighbors / valid_neighbors

            # If unhappy, move to a random empty cell
            if similarity_fraction < self.model.homophily:
                self.model.grid.move_to_empty(self)
            else:
                self.model.happy += 1
