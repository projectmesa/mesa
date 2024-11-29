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
        neighbors = self.model.grid.iter_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )

        valid_neighbors = 0
        similar_neighbors = 0

        for neighbor in neighbors:
            if hasattr(neighbor, "type"):  # Exclude empty cells
                valid_neighbors += 1
                if neighbor.type == self.type:  # Count similar neighbors
                    similar_neighbors += 1

        # Calculate the fraction of similar neighbors
        if valid_neighbors > 0:
            similarity_fraction = similar_neighbors / valid_neighbors

            # If unhappy, move to a random empty cell
            if similarity_fraction < self.model.homophily:
                self.model.grid.move_to_empty(self)
            else:
                self.model.happy += 1
        else:
            self.model.happy += 1
