"""
Boids Flocking Model
===================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import numpy as np

from mesa import Model
from mesa.examples.basic.boid_flockers.agents import Boid
from mesa.space import ContinuousSpace


class BoidFlockers(Model):
    """Flocker model class. Handles agent creation, placement and scheduling."""

    def __init__(
        self,
        population=100,
        width=100,
        height=100,
        speed=1,
        vision=10,
        separation=2,
        cohere=0.03,
        separate=0.015,
        match=0.05,
        seed=None,
    ):
        """Create a new Boids Flocking model.

        Args:
            population: Number of Boids in the simulation (default: 100)
            width: Width of the space (default: 100)
            height: Height of the space (default: 100)
            speed: How fast the Boids move (default: 1)
            vision: How far each Boid can see (default: 10)
            separation: Minimum distance between Boids (default: 2)
            cohere: Weight of cohesion behavior (default: 0.03)
            separate: Weight of separation behavior (default: 0.015)
            match: Weight of alignment behavior (default: 0.05)
            seed: Random seed for reproducibility (default: None)
        """
        super().__init__(seed=seed)

        # Model Parameters
        self.population = population
        self.vision = vision
        self.speed = speed
        self.separation = separation

        # Set up the space
        self.space = ContinuousSpace(width, height, torus=True)

        # Store flocking weights
        self.factors = {"cohere": cohere, "separate": separate, "match": match}

        # Create and place the Boid agents
        self.make_agents()

        # For tracking statistics
        self.average_heading = None
        self.update_average_heading()

    def make_agents(self):
        """Create and place all Boid agents randomly in the space."""
        for _ in range(self.population):
            # Random position
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))

            # Random initial direction
            direction = np.random.random(2) * 2 - 1  # Random vector between -1 and 1
            direction /= np.linalg.norm(direction)  # Normalize

            # Create and place the Boid
            boid = Boid(
                model=self,
                speed=self.speed,
                direction=direction,
                vision=self.vision,
                separation=self.separation,
                **self.factors,
            )
            self.space.place_agent(boid, pos)

    def update_average_heading(self):
        """Calculate the average heading (direction) of all Boids."""
        if not self.agents:
            self.average_heading = 0
            return

        headings = np.array([agent.direction for agent in self.agents])
        mean_heading = np.mean(headings, axis=0)
        self.average_heading = np.arctan2(mean_heading[1], mean_heading[0])

    def step(self):
        """Run one step of the model.

        All agents are activated in random order using the AgentSet shuffle_do method.
        """
        self.agents.shuffle_do("step")
        self.update_average_heading()
