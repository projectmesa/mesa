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
        
        # Filter out empty cells
        similar_neighbors = [
            neighbor for neighbor in neighbors 
            if hasattr(neighbor, 'type') and neighbor.type == self.type
        ]
        total_neighbors = [
            neighbor for neighbor in neighbors 
            if hasattr(neighbor, 'type')
        ]
        
        # Calculate fraction of similar neighbors
        if len(total_neighbors) > 0:
            similarity_fraction = len(similar_neighbors) / len(total_neighbors)
            
            # If unhappy, move to a random empty cell
            if similarity_fraction < self.model.homophily / 8.0:
                self.model.grid.move_to_empty(self)
            else:
                self.model.happy += 1
