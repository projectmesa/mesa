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
    def __init__(self, unique_id, pos, velocity=None, vision=5, separation=1):
        '''
        Create a new Boid flocker agent.
        '''
        self.unique_id = unique_id
        self.pos = pos
        if velocity is not None:
            self.velocity = velocity
        else:
            self.velocity
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
        sep_vector = np.array([0,0])
        for neighbor in neighbors:
            their_pos = np.array(neighbor.pos)
            dist = np.linalg.norm(my_pos - their_pos)
            if dist < self.separation:
                sep_vector -= their_pos - my_pos
        return sep_vector

    def match_velocity(self, neighbors):
        mean_velocity = np.array([0, 0])
        for neighbor in neighbors:
            mean_velocity += neighbor.velocity
        return mean_velocity / len(neighbors)

    def step(self, model):
        x, y = self.pos
        neighbors = model.space.get_neighbors(x, y, self.vision, False)
        if len(neighbors) > 0:
            cohere_vector = self.cohere(neighbors)
            separate_vector = self.separate(neighbors)
            match_vel_vector = self.match_velocity(neighbors)
            self.velocity += cohere_vector + separate_vector + 0.1 * match_vel_vector
        new_pos = np.array(self.pos) + self.velocity
        new_x, new_y = new_pos
        model.space.move_agent(self, (new_x, new_y))

class BoidModel(Model):
    N = 100
    width = 100
    height = 100

    def __init__(self, N, width, height, vision, separation):
        self.N = N
        self.vision = vision
        self.separation = separation
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True,
            grid_width=10, grid_height=10)
        self.make_agents()

    def make_agents(self):
        for i in range(self.N):
            x = random.random() * self.space.x_max
            y = random.random() * self.space.y_max
            pos = (x, y)
            velocity = np.random.random(2)
            velocity /= np.linalg.norm(velocity)
            boid = Boid(i, pos, velocity, self.vision, self.separation)
            self.space.place_agent(boid,  pos)
            self.schedule.add(boid)

    def step(self):
        self.schedule.step()


