"""
Flockers
=============================================================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import mesa
import numpy as np
from agents import Boid


class BoidFlockers(mesa.Model):
    """
    Flocker model class. Handles agent creation, placement and scheduling.
    """

    def __init__(
        self,
        seed=None,
        population=100,
        width=100,
        height=100,
        vision=10,
        speed=1,
        separation=1,
        cohere=0.03,
        separate=0.015,
        match=0.05,
    ):
        """
        Create a new Flockers model.

        Args:
            population: Number of Boids
            width, height: Size of the space.
            speed: How fast should the Boids move.
            vision: How far around should each Boid look for its neighbors
            separation: What's the minimum distance each Boid will attempt to
                    keep from any other
            cohere, separate, match: factors for the relative importance of
                    the three drives.
        """
        super().__init__(seed=seed)
        self.population = population
        self.vision = vision
        self.speed = speed
        self.separation = separation

        self.space = mesa.space.ContinuousSpace(width, height, True)
        self.factors = {"cohere": cohere, "separate": separate, "match": match}
        self.make_agents()

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for _ in range(self.population):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            direction = np.random.random(2) * 2 - 1
            boid = Boid(
                model=self,
                speed=self.speed,
                direction=direction,
                vision=self.vision,
                separation=self.separation,
                **self.factors,
            )
            self.space.place_agent(boid, pos)

    def step(self):
        self.agents.shuffle_do("step")
