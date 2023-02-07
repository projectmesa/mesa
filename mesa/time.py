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
"""

# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

from collections import defaultdict

# mypy
from typing import Iterator, Union

from mesa.agent import Agent
from mesa.model import Model

# BaseScheduler has a self.time of int, while
# StagedActivation has a self.time of float
TimeT = Union[float, int]


class BaseScheduler:
    """Simplest scheduler; activates agents one at a time, in the order
    they were added.

    Assumes that each agent added has a *step* method which takes no arguments.

    (This is explicitly meant to replicate the scheduler in MASON).
    """

    def __init__(self, model: Model) -> None:
        """Create a new, empty BaseScheduler."""
        self.model = model
        self.steps = 0
        self.time: TimeT = 0
        self._agents: dict[int, Agent] = {}

    def add(self, agent: Agent) -> None:
        """Add an Agent object to the schedule.

        Args:
            agent: An Agent to be added to the schedule. NOTE: The agent must
            have a step() method.
        """
        if agent.unique_id in self._agents:
            raise Exception(
                f"Agent with unique id {repr(agent.unique_id)} already added to scheduler"
            )

        self._agents[agent.unique_id] = agent

    def remove(self, agent: Agent) -> None:
        """Remove all instances of a given agent from the schedule.

        Args:
            agent: An agent object.
        """
        del self._agents[agent.unique_id]

    def step(self) -> None:
        """Execute the step of all the agents, one at a time."""
        for agent in self.agent_buffer(shuffled=False):
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self) -> int:
        """Returns the current number of agents in the queue."""
        return len(self._agents)

    @property
    def agents(self) -> list[Agent]:
        return list(self._agents.values())

    def agent_buffer(self, shuffled: bool = False) -> Iterator[Agent]:
        """Simple generator that yields the agents while letting the user
        remove and/or add agents during stepping.
        """
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.
        agent_keys = list(self._agents.keys())
        if shuffled:
            self.model.random.shuffle(agent_keys)

        for agent_key in agent_keys:
            if agent_key in self._agents:
                yield self._agents[agent_key]


class RandomActivation(BaseScheduler):
    """A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask agents...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step(model) method.
    """

    def step(self) -> None:
        """Executes the step of all agents, one at a time, in
        random order.

        """
        for agent in self.agent_buffer(shuffled=True):
            agent.step()
        self.steps += 1
        self.time += 1


class SimultaneousActivation(BaseScheduler):
    """A scheduler to simulate the simultaneous activation of all the agents.

    This scheduler requires that each agent have two methods: step and advance.
    step() activates the agent and stages any necessary changes, but does not
    apply them yet. advance() then applies the changes.
    """

    def step(self) -> None:
        """Step all agents, then advance them."""
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.
        agent_keys = list(self._agents.keys())
        for agent_key in agent_keys:
            self._agents[agent_key].step()
        # We recompute the keys because some agents might have been removed in
        # the previous loop.
        agent_keys = list(self._agents.keys())
        for agent_key in agent_keys:
            self._agents[agent_key].advance()
        self.steps += 1
        self.time += 1


class StagedActivation(BaseScheduler):
    """A scheduler which allows agent activation to be divided into several
    stages instead of a single `step` method. All agents execute one stage
    before moving on to the next.

    Agents must have all the stage methods implemented. Stage methods take a
    model object as their only argument.

    This schedule tracks steps and time separately. Time advances in fractional
    increments of 1 / (# of stages), meaning that 1 step = 1 unit of time.
    """

    def __init__(
        self,
        model: Model,
        stage_list: list[str] | None = None,
        shuffle: bool = False,
        shuffle_between_stages: bool = False,
    ) -> None:
        """Create an empty Staged Activation schedule.

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
        self.stage_list = stage_list if stage_list else ["step"]
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages
        self.stage_time = 1 / len(self.stage_list)

    def step(self) -> None:
        """Executes all the stages for all agents."""
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.
        agent_keys = list(self._agents.keys())
        if self.shuffle:
            self.model.random.shuffle(agent_keys)
        for stage in self.stage_list:
            for agent_key in agent_keys:
                if agent_key in self._agents:
                    getattr(self._agents[agent_key], stage)()  # Run stage
            # We recompute the keys because some agents might have been removed
            # in the previous loop.
            agent_keys = list(self._agents.keys())
            if self.shuffle_between_stages:
                self.model.random.shuffle(agent_keys)
            self.time += self.stage_time

        self.steps += 1


class RandomActivationByType(BaseScheduler):
    """
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    The `step_type` method is equivalent to the NetLogo 'ask [breed]...' and is
    generally the default behavior for an ABM. The `step` method performs
    `step_type` for each of the agent types.

    Assumes that all agents have a step() method.

    This implementation assumes that the type of an agent doesn't change
    throughout the simulation.

    If you want to do some computations / data collections specific to an agent
    type, you can either:
    - loop through all agents, and filter by their type
    - access via `your_model.scheduler.agents_by_type[your_type_class]`
    """

    def __init__(self, model: Model) -> None:
        super().__init__(model)
        self.agents_by_type = defaultdict(dict)

    def add(self, agent: Agent) -> None:
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """
        super().add(agent)
        agent_class: type[Agent] = type(agent)
        self.agents_by_type[agent_class][agent.unique_id] = agent

    def remove(self, agent: Agent) -> None:
        """
        Remove all instances of a given agent from the schedule.
        """
        del self._agents[agent.unique_id]

        agent_class: type[Agent] = type(agent)
        del self.agents_by_type[agent_class][agent.unique_id]

    def step(self, shuffle_types: bool = True, shuffle_agents: bool = True) -> None:
        """
        Executes the step of each agent type, one at a time, in random order.

        Args:
            shuffle_types: If True, the order of execution of each types is
                           shuffled.
            shuffle_agents: If True, the order of execution of each agents in a
                            type group is shuffled.
        """
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.
        type_keys: list[type[Agent]] = list(self.agents_by_type.keys())
        if shuffle_types:
            self.model.random.shuffle(type_keys)
        for agent_class in type_keys:
            self.step_type(agent_class, shuffle_agents=shuffle_agents)
        self.steps += 1
        self.time += 1

    def step_type(self, type_class: type[Agent], shuffle_agents: bool = True) -> None:
        """
        Shuffle order and run all agents of a given type.
        This method is equivalent to the NetLogo 'ask [breed]...'.

        Args:
            type_class: Class object of the type to run.
        """
        agent_keys: list[int] = list(self.agents_by_type[type_class].keys())
        if shuffle_agents:
            self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            if agent_key in self.agents_by_type[type_class]:
                self.agents_by_type[type_class][agent_key].step()

    def get_type_count(self, type_class: type[Agent]) -> int:
        """
        Returns the current number of agents of certain type in the queue.
        """
        return len(self.agents_by_type[type_class])
