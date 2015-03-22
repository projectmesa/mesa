'''
Mesa Time Module
=================================

Objects for handling the time component of a model. In particular, this module
contains Schedulers, which handle agent activation. A Scheduler is an object
which controls when agents are called upon to act, and when.

The activation order can have a serious impact on model behavior, so it's
important to specify it explicity. Example simple activation regimes include
activating all agents in the same order every step, shuffling the activation
order every time, activating each agent *on average* once per step, and more.

Key concepts:
    Step: Many models advance in 'steps'. A step may involve the activation of
    all agents, or a random (or selected) subset of them. Each agent in turn
    may have their own step() method.

    Time: Some models may simulate a continuous 'clock' instead of discrete
    steps. However, by default, the Time is equal to the number of steps the
    model has taken.


TODO: Have the schedulers use the model's randomizer, to keep random number
seeds consistent and allow for replication.

'''

import random


class BaseScheduler(object):
    '''
    Simplest scheduler; activates agents one at a time, in the order they were
    added.

    Assumes that each agent added has a *step* method, which accepts a model
    object as its single argument.

    (This is explicitly meant to replicate the scheduler in MASON).
    '''

    model = None
    steps = 0
    time = 0
    agents = []

    def __init__(self, model):
        '''
        Create a new, empty BaseScheduler.
        '''

        self.model = model
        self.steps = 0
        self.time = 0
        self.agents = []

    def add(self, agent):
        '''
        Add an Agent object to the schedule.

        Args:
            agent: An Agent to be added to the schedule. NOTE: The agent must
            have a step(model) method.
        '''
        self.agents.append(agent)

    def remove(self, agent):
        '''
        Remove all instances of a given agent from the schedule.

        Args:
            agent: An agent object.
        '''
        while agent in self.agents:
            self.agents.remove(agent)

    def step(self):
        '''
        Execute the step of all the agents, one at a time.
        '''
        for agent in self.agents:
            agent.step(self.model)
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        '''
        Returns the current number of agents in the queue.
        '''

        return len(self.agents)


class RandomActivation(BaseScheduler):
    '''
    A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask agents...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step(model) method.
    '''

    def step(self):
        '''
        Executes the step of all agents, one at a time, in random order.
        '''
        random.shuffle(self.agents)

        for agent in self.agents:
            agent.step(self.model)
        self.steps += 1
        self.time += 1
