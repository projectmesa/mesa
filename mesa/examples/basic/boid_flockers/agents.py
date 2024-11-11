"""A Boid (bird-oid) agent for implementing Craig Reynolds's Boids flocking model.

This implementation uses numpy arrays to represent vectors for efficient computation
of flocking behavior.
"""

import numpy as np

from mesa import Agent


class Boid(Agent):
    """A Boid-style flocker agent.

    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents
        - Separation: avoiding getting too close to any other agent
        - Alignment: trying to fly in the same direction as neighbors

    Boids have a vision that defines the radius in which they look for their
    neighbors to flock with. Their speed (a scalar) and direction (a vector)
    define their movement. Separation is their desired minimum distance from
    any other Boid.
    """

    def __init__(
        self,
        model,
        speed,
        direction,
        vision,
        separation,
        cohere=0.03,
        separate=0.015,
        match=0.05,
    ):
        """Create a new Boid flocker agent.

        Args:
            model: Model instance the agent belongs to
            speed: Distance to move per step
            direction: numpy vector for the Boid's direction of movement
            vision: Radius to look around for nearby Boids
            separation: Minimum distance to maintain from other Boids
            cohere: Relative importance of matching neighbors' positions (default: 0.03)
            separate: Relative importance of avoiding close neighbors (default: 0.015)
            match: Relative importance of matching neighbors' directions (default: 0.05)
        """
        super().__init__(model)
        self.speed = speed
        self.direction = direction
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match
        self.neighbors = []

    def step(self):
        """Get the Boid's neighbors, compute the new vector, and move accordingly."""
        self.neighbors = self.model.space.get_neighbors(self.pos, self.vision, False)

        # If no neighbors, maintain current direction
        if not self.neighbors:
            new_pos = self.pos + self.direction * self.speed
            self.model.space.move_agent(self, new_pos)
            return

        # Initialize vectors for the three flocking behaviors
        cohere = np.zeros(2)  # Cohesion vector
        match_vector = np.zeros(2)  # Alignment vector
        separation_vector = np.zeros(2)  # Separation vector

        # Calculate the contribution of each neighbor to the three behaviors
        for neighbor in self.neighbors:
            heading = self.model.space.get_heading(self.pos, neighbor.pos)
            distance = self.model.space.get_distance(self.pos, neighbor.pos)

            # Cohesion - steer towards the average position of neighbors
            cohere += heading

            # Separation - avoid getting too close
            if distance < self.separation:
                separation_vector -= heading

            # Alignment - match neighbors' flying direction
            match_vector += neighbor.direction

        # Weight each behavior by its factor and normalize by number of neighbors
        n = len(self.neighbors)
        cohere = cohere * self.cohere_factor
        separation_vector = separation_vector * self.separate_factor
        match_vector = match_vector * self.match_factor

        # Update direction based on the three behaviors
        self.direction += (cohere + separation_vector + match_vector) / n

        # Normalize direction vector
        self.direction /= np.linalg.norm(self.direction)

        # Move boid
        new_pos = self.pos + self.direction * self.speed
        self.model.space.move_agent(self, new_pos)
