# -*- coding: utf-8 -*-
"""
Mesa Time Module
================

Objects for handling the time component of a model. In particular, this module
contains Schedulers, which handle agent activation. A Scheduler is an object
which controls when agents are called upon to act, and when.

The activation order can have a serious impact on model behavior, so it's
important to specify it explicitly. Example simple activation regimes include
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

"""
import random


class BaseScheduler:
    """ Simplest scheduler; activates agents one at a time, in the order
    they were added.

    Assumes that each agent added has a *step* method which takes no arguments.

    (This is explicitly meant to replicate the scheduler in MASON).

    """
    def __init__(self, model):
        """ Create a new, empty BaseScheduler. """
        self.model = model
        self.steps = 0
        self.time = 0
        self.agents = []

    def add(self, agent):
        """ Add an Agent object to the schedule.

        Args:
            agent: An Agent to be added to the schedule. NOTE: The agent must
            have a step() method.

        """
        self.agents.append(agent)

    def remove(self, agent):
        """ Remove all instances of a given agent from the schedule.

        Args:
            agent: An agent object.

        """
        while agent in self.agents:
            self.agents.remove(agent)

    def step(self):
        """ Execute the step of all the agents, one at a time. """
        for agent in self.agents[:]:
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        """ Returns the current number of agents in the queue. """
        return len(self.agents)


class RandomActivation(BaseScheduler):
    """ A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask agents...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step(model) method.

    """
    def step(self):
        """ Executes the step of all agents, one at a time, in
        random order.

        """
        random.shuffle(self.agents)
        for agent in self.agents[:]:
            agent.step()
        self.steps += 1
        self.time += 1


class SimultaneousActivation(BaseScheduler):
    """ A scheduler to simulate the simultaneous activation of all the agents.

    This scheduler requires that each agent have two methods: step and advance.
    step() activates the agent and stages any necessary changes, but does not
    apply them yet. advance() then applies the changes.

    """
    def step(self):
        """ Step all agents, then advance them. """
        for agent in self.agents[:]:
            agent.step()
        for agent in self.agents[:]:
            agent.advance()
        self.steps += 1
        self.time += 1


class StagedActivation(BaseScheduler):
    """ A scheduler which allows agent activation to be divided into several
    stages instead of a single `step` method. All agents execute one stage
    before moving on to the next.

    Agents must have all the stage methods implemented. Stage methods take a
    model object as their only argument.

    This schedule tracks steps and time separately. Time advances in fractional
    increments of 1 / (# of stages), meaning that 1 step = 1 unit of time.

    """
    def __init__(self, model, stage_list=None, shuffle=False,
                 shuffle_between_stages=False):
        """ Create an empty Staged Activation schedule.

        Args:
            model: Model object associated with the schedule.
            stage_list: List of strings of names of stages to run, in the
                         order to run them in.
            shuffle: If True, shuffle the order of agents each step.
            shuffle_between_stages: If True, shuffle the agents after each
                                    stage; otherwise, only shuffle at the start
                                    of each step.

        """
        super().__init__(model)
        self.stage_list = ["step"] if not stage_list else stage_list
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages
        self.stage_time = 1 / len(self.stage_list)

    def step(self):
        """ Executes all the stages for all agents. """
        if self.shuffle:
            random.shuffle(self.agents)
        for stage in self.stage_list:
            for agent in self.agents[:]:
                getattr(agent, stage)()  # Run stage
            if self.shuffle_between_stages:
                random.shuffle(self.agents)
            self.time += self.stage_time

        self.steps += 1
