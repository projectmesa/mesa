"""A Boid (bird-oid) agent for implementing Craig Reynolds's Boids flocking model.

This implementation uses numpy arrays to represent vectors for efficient computation
of flocking behavior.
"""

import numpy as np

from mesa.experimental.continuous_space import ContinuousSpaceAgent


class Boid(ContinuousSpaceAgent):
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
        space,
        position=(0,0),
        speed=1,
        direction=(1,1),
        vision=1,
        separation=1,
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
        super().__init__(space, model)
        self.position = position
        self.speed = speed
        self.direction = direction
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match
        self.neighbors = []

    @property
    def pos(self):
        return self.position

    @pos.setter
    def pos(self, value):
        pass


    def step(self):
        """Get the Boid's neighbors, compute the new vector, and move accordingly."""
        neighbors, distances = self.get_neighbors_in_radius(radius=self.vision, include_distance=True)
        self.neighbors = neighbors.tolist()

        # If no neighbors, maintain current direction
        if neighbors.size==0:
            self.position += self.direction * self.speed
            return

        delta = self.space.calculate_difference_vector(self.position, [n._mesa_index for n in neighbors])

        cohere = np.sum(delta, axis=0) * self.cohere_factor
        separation_vector = -1 * np.sum(delta[distances < self.separation], axis=0) * self.separate_factor
        match_vector = np.sum(np.asarray([n.direction for n in neighbors]), axis=0) * self.match_factor

        # Update direction based on the three behaviors
        self.direction += (cohere + separation_vector + match_vector) / len(neighbors)

        # Normalize direction vector
        self.direction /= np.linalg.norm(self.direction)

        # Move boid
        self.position += self.direction * self.speed
