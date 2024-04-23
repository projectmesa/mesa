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

import warnings
from collections import defaultdict
from collections.abc import Iterable

# mypy
from typing import Union

from mesa.agent import Agent, AgentSet
from mesa.model import Model

# BaseScheduler has a self.time of int, while
# StagedActivation has a self.time of float
TimeT = Union[float, int]


class BaseScheduler:
    """
    A simple scheduler that activates agents one at a time, in the order they were added.

    This scheduler is designed to replicate the behavior of the scheduler in MASON, a multi-agent simulation toolkit.
    It assumes that each agent added has a `step` method which takes no arguments and executes the agent's actions.

    Attributes:
        - model (Model): The model instance associated with the scheduler.
        - steps (int): The number of steps the scheduler has taken.
        - time (TimeT): The current time in the simulation. Can be an integer or a float.

    Methods:
        - add: Adds an agent to the scheduler.
        - remove: Removes an agent from the scheduler.
        - step: Executes a step, which involves activating each agent once.
        - get_agent_count: Returns the number of agents in the scheduler.
        - agents (property): Returns a list of all agent instances.
    """

    def __init__(self, model: Model, agents: Iterable[Agent] | None = None) -> None:
        """Create a new BaseScheduler.

        Args:
            model (Model): The model to which the schedule belongs
            agents (Iterable[Agent], None, optional): An iterable of agents who are controlled by the schedule

        """
        self.model = model
        self.steps = 0
        self.time: TimeT = 0
        self._original_step = self.step
        self.step = self._wrapped_step

        if agents is None:
            agents = []

        self._agents: AgentSet = AgentSet(agents, model)

        self._remove_warning_given = False
        self._agents_key_warning_given = False

    def add(self, agent: Agent) -> None:
        """Add an Agent object to the schedule.

        Args:
            agent: An Agent to be added to the schedule. NOTE: The agent must
            have a step() method.
        """

        if agent not in self._agents:
            self._agents.add(agent)
        else:
            raise ValueError("agent already added to scheduler")

    def remove(self, agent: Agent) -> None:
        """Remove all instances of a given agent from the schedule.

        Note:
            It is only necessary to explicitly remove agents from the schedule if
            the agent is not removed from the model.

        Args:
            agent: An agent object.
        """
        self._agents.remove(agent)

    def step(self) -> None:
        """Execute the step of all the agents, one at a time."""
        # To be able to remove and/or add agents during stepping
        # it's necessary for the keys view to be a list.
        self.do_each("step")
        self.steps += 1
        self.time += 1

    def _wrapped_step(self):
        """Wrapper for the step method to include time and step updating."""
        self._original_step()
        self.model._advance_time()

    def get_agent_count(self) -> int:
        """Returns the current number of agents in the queue."""
        return len(self._agents)

    @property
    def agents(self) -> AgentSet:
        # a bit dirty, but returns a copy of the internal agent set
        return self._agents.select()

    def get_agent_keys(self, shuffle: bool = False) -> list[int]:
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.

        if not self._agents_key_warning_given:
            self._agents_key_warning_given = True
            warnings.warn(
                "Because of the shift to using weakrefs, this method will be removed in a future version",
                DeprecationWarning,
                stacklevel=2,
            )

        agent_keys = [agent.unique_id for agent in self._agents]
        if shuffle:
            self.model.random.shuffle(agent_keys)
        return agent_keys

    def do_each(self, method, shuffle=False):
        if shuffle:
            self._agents.shuffle(inplace=True)
        self._agents.do(method)


class RandomActivation(BaseScheduler):
    """
    A scheduler that activates each agent once per step, in a random order, with the order reshuffled each step.

    This scheduler is equivalent to the NetLogo 'ask agents...' behavior and is a common default for ABMs.
    It assumes that all agents have a `step` method.

    The random activation ensures that no single agent or sequence of agents consistently influences the model due
    to ordering effects, which is crucial for certain types of simulations.

    Inherits all attributes and methods from BaseScheduler.

    Methods:
        - step: Executes a step, activating each agent in a random order.
    """

    def step(self) -> None:
        """Executes the step of all agents, one at a time, in
        random order.

        """
        self.do_each("step", shuffle=True)
        self.steps += 1
        self.time += 1


class SimultaneousActivation(BaseScheduler):
    """
    A scheduler that simulates the simultaneous activation of all agents.

    This scheduler is unique in that it requires agents to have both `step` and `advance` methods.
    - The `step` method is for activating the agent and staging any changes without applying them immediately.
    - The `advance` method then applies these changes, simulating simultaneous action.

    This scheduler is useful in scenarios where the interactions between agents are sensitive to the order
    of execution, and a quasi-simultaneous execution is more realistic.

    Inherits all attributes and methods from BaseScheduler.

    Methods:
        - step: Executes a step for all agents, first calling `step` then `advance` on each.
    """

    def step(self) -> None:
        """Step all agents, then advance them."""
        self.do_each("step")
        # do_each recomputes the agent_keys from scratch whenever it is called.
        # It can handle the case when some agents might have been removed in
        # the previous loop.
        self.do_each("advance")
        self.steps += 1
        self.time += 1


class StagedActivation(BaseScheduler):
    """
    A scheduler allowing agent activation to be divided into several stages, with all agents executing one stage
    before moving on to the next. This class is a generalization of SimultaneousActivation.

    This scheduler is useful for complex models where actions need to be broken down into distinct phases
    for each agent in each time step. Agents must implement methods for each defined stage.

    The scheduler also tracks steps and time separately, allowing fractional time increments based on the number
    of stages. Time advances in fractional increments of 1 / (# of stages), meaning that 1 step = 1 unit of time.

    Inherits all attributes and methods from BaseScheduler.

    Attributes:
        - stage_list (list[str]): A list of stage names that define the order of execution.
        - shuffle (bool): Determines whether to shuffle the order of agents each step.
        - shuffle_between_stages (bool): Determines whether to shuffle agents between each stage.

    Methods:
        - step: Executes all the stages for all agents in the defined order.
    """

    def __init__(
        self,
        model: Model,
        agents: Iterable[Agent] | None = None,
        stage_list: list[str] | None = None,
        shuffle: bool = False,
        shuffle_between_stages: bool = False,
    ) -> None:
        """Create an empty Staged Activation schedule.

        Args:
            model (Model): The model to which the schedule belongs
            agents (Iterable[Agent], None, optional): An iterable of agents who are controlled by the schedule
            stage_list (:obj:`list` of :obj:`str`): List of strings of names of stages to run, in the
                         order to run them in.
            shuffle (bool, optional): If True, shuffle the order of agents each step.
            shuffle_between_stages (bool, optional): If True, shuffle the agents after each
                                    stage; otherwise, only shuffle at the start
                                    of each step.
        """
        super().__init__(model, agents)
        self.stage_list = stage_list if stage_list else ["step"]
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages
        self.stage_time = 1 / len(self.stage_list)

    def step(self) -> None:
        """Executes all the stages for all agents."""
        shuffle = self.shuffle
        for stage in self.stage_list:
            if stage.startswith("model."):
                getattr(self.model, stage[6:])()
            else:
                self.do_each(stage, shuffle=shuffle)

            shuffle = self.shuffle_between_stages
            self.time += self.stage_time

        self.steps += 1


class RandomActivationByType(BaseScheduler):
    """
    A scheduler that activates each type of agent once per step, in random order, with the order reshuffled every step.

    This scheduler is useful for models with multiple types of agents, ensuring that each type is treated
    equitably in terms of activation order. The randomness in activation order helps in reducing biases
    due to ordering effects.

    Inherits all attributes and methods from BaseScheduler.

    If you want to do some computations / data collections specific to an agent
    type, you can either:
    - loop through all agents, and filter by their type
    - access via `your_model.scheduler.agents_by_type[your_type_class]`

    Attributes:
        - agents_by_type (defaultdict): A dictionary mapping agent types to dictionaries of agents.

    Methods:
        - step: Executes the step of each agent type in a random order.
        - step_type: Activates all agents of a given type.
        - get_type_count: Returns the count of agents of a specific type.
    """

    @property
    def agents_by_type(self):
        warnings.warn(
            "Because of the shift to using AgentSet, in the future this attribute will return a dict with"
            "type as key as AgentSet as value. Future behavior is available via RandomActivationByType._agents_by_type",
            DeprecationWarning,
            stacklevel=2,
        )

        agentsbytype = defaultdict(dict)
        for k, v in self._agents_by_type.items():
            agentsbytype[k] = {agent.unique_id: agent for agent in v}

        return agentsbytype

    def __init__(self, model: Model, agents: Iterable[Agent] | None = None) -> None:
        super().__init__(model, agents)
        """

        Args:
            model (Model): The model to which the schedule belongs
            agents (Iterable[Agent], None, optional): An iterable of agents who are controlled by the schedule
        """

        # can't be a defaultdict because we need to pass model to AgentSet
        self._agents_by_type: [type, AgentSet] = {}

        if agents is not None:
            for agent in agents:
                try:
                    self._agents_by_type[type(agent)].add(agent)
                except KeyError:
                    self._agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def add(self, agent: Agent) -> None:
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """
        super().add(agent)

        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def remove(self, agent: Agent) -> None:
        """
        Remove all instances of a given agent from the schedule.
        """
        super().remove(agent)
        self._agents_by_type[type(agent)].remove(agent)

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
        type_keys: list[type[Agent]] = list(self._agents_by_type.keys())
        if shuffle_types:
            self.model.random.shuffle(type_keys)
        for agent_class in type_keys:
            self.step_type(agent_class, shuffle_agents=shuffle_agents)
        self.steps += 1
        self.time += 1

    def step_type(self, agenttype: type[Agent], shuffle_agents: bool = True) -> None:
        """
        Shuffle order and run all agents of a given type.
        This method is equivalent to the NetLogo 'ask [breed]...'.

        Args:
            agenttype: Class object of the type to run.
        """
        agents = self._agents_by_type[agenttype]

        if shuffle_agents:
            agents.shuffle(inplace=True)
        agents.do("step")

    def get_type_count(self, agenttype: type[Agent]) -> int:
        """
        Returns the current number of agents of certain type in the queue.
        """
        return len(self._agents_by_type[agenttype])


class DiscreteEventScheduler(BaseScheduler):
    """
    This class has been deprecated and replaced by the functionality provided by experimental.devs
    """

    def __init__(self, model: Model, time_step: TimeT = 1) -> None:
        """

        Args:
            model (Model): The model to which the schedule belongs
            time_step (TimeT): The fixed time step between steps

        """
        super().__init__(model)
        raise Exception(
            "DiscreteEventScheduler is deprecated in favor of the functionality provided by experimental.devs"
        )
