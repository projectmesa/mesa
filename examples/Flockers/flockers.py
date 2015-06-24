'''
Flockers
===============
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
'''


import numpy as np
import random

from mesa import Model, Agent
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation


class Boid(Agent):
    '''
    A Boid-style flocker agent.

    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents
        - Separation:
    '''
    def __init__(self, unique_id, pos, speed=5, heading=None,
            vision=5, separation=1):
        '''
        Create a new Boid flocker agent.
        '''
        self.unique_id = unique_id
        self.pos = pos
        self.speed = speed
        if heading is not None:
            self.heading = heading
        else:
            self.heading = np.random.random(2)
            self.heading /= np.linalg.norm(self.heading)
        self.vision = vision
        self.separation = separation

    def cohere(self, neighbors):
        '''
        Return the vector toward the center of mass of the local neighbors.
        '''
        center = np.array([0.0, 0.0])
        for neighbor in neighbors:
            center += np.array(neighbor.pos)
        return center / len(neighbors)

    def separate(self, neighbors):
        my_pos = np.array(self.pos)
        sep_vector = np.array([0, 0])
        for neighbor in neighbors:
            their_pos = np.array(neighbor.pos)
            dist = np.linalg.norm(my_pos - their_pos)
            if dist < self.separation:
                sep_vector -= their_pos - my_pos
        return sep_vector

    def match_heading(self, neighbors):
        mean_heading = np.array([0, 0])
        for neighbor in neighbors:
            mean_heading += neighbor.heading
        return mean_heading / len(neighbors)

    def step(self, model):
        x, y = self.pos
        neighbors = model.space.get_neighbors(x, y, self.vision, False)
        if len(neighbors) > 0:
            cohere_vector = self.cohere(neighbors)
            separate_vector = self.separate(neighbors)
            match_heading_vector = self.match_heading(neighbors)
            self.heading += (cohere_vector + separate_vector
                + match_heading_vector)
            self.heading /= np.linalg.norm(self.heading)
        new_pos = np.array(self.pos) + self.heading * self.speed
        new_x, new_y = new_pos
        model.space.move_agent(self, (new_x, new_y))


class BoidModel(Model):
    N = 100
    width = 100
    height = 100

    def __init__(self, N, width, height, speed, vision, separation):
        self.N = N
        self.vision = vision
        self.speed = speed
        self.separation = separation
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True,
            grid_width=10, grid_height=10)
        self.make_agents()
        self.running = True

    def make_agents(self):
        for i in range(self.N):
            x = random.random() * self.space.x_max
            y = random.random() * self.space.y_max
            pos = (x, y)
            heading = np.random.random(2) * 2 - np.array((1, 1))
            heading /= np.linalg.norm(heading)
            boid = Boid(i, pos, self.speed, heading, self.vision, self.separation)
            self.space.place_agent(boid, pos)
            self.schedule.add(boid)

    def step(self):
        self.schedule.step()
