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

import heapq
import warnings
import weakref
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
            self.agents.shuffle(inplace=True)
        self.agents.do(method)


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

    def __init__(self, model: Model, agents: Iterable[Agent] | None = None) -> None:
        super().__init__(model, agents)
        """

        Args:
            model (Model): The model to which the schedule belongs
            agents (Iterable[Agent], None, optional): An iterable of agents who are controlled by the schedule
        """

        # can't be a defaultdict because we need to pass model to AgentSet
        self.agents_by_type: [type, AgentSet] = {}

        if agents is not None:
            for agent in agents:
                try:
                    self.agents_by_type[type(agent)].add(agent)
                except KeyError:
                    self.agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def add(self, agent: Agent) -> None:
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """
        super().add(agent)

        try:
            self.agents_by_type[type(agent)].add(agent)
        except KeyError:
            self.agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def remove(self, agent: Agent) -> None:
        """
        Remove all instances of a given agent from the schedule.
        """
        super().remove(agent)
        self.agents_by_type[type(agent)].remove(agent)

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

    def step_type(self, agenttype: type[Agent], shuffle_agents: bool = True) -> None:
        """
        Shuffle order and run all agents of a given type.
        This method is equivalent to the NetLogo 'ask [breed]...'.

        Args:
            agenttype: Class object of the type to run.
        """
        agents = self.agents_by_type[agenttype]

        if shuffle_agents:
            agents.shuffle(inplace=True)
        agents.do("step")

    def get_type_count(self, agenttype: type[Agent]) -> int:
        """
        Returns the current number of agents of certain type in the queue.
        """
        return len(self.agents_by_type[agenttype])


class DiscreteEventScheduler(BaseScheduler):
    """
    A scheduler for discrete event simulation in Mesa.

    This scheduler manages events where each event is associated with a
    specific time and agent. The scheduler advances time not in fixed
    increments, but to the moment the next event is scheduled to occur.

    This implementation uses a priority queue (heapq) to manage events. Each
    event is a tuple of the form (time, random_value, agent), where:
        - time (float): The scheduled time for the event.
        - random_value (float): A secondary sorting criterion to randomize
          the order of events that are scheduled for the same time.
        - agent (Agent): The agent associated with the event.

    The random value for secondary sorting ensures that when two events are
    scheduled for the same time, their execution order is randomized, thus
    preventing direct comparison issues between different types of agents and
    maintaining the integrity of the simulation's randomness.

    Attributes:
        model (Model): The model instance associated with the scheduler.
        event_queue (list): A priority queue of scheduled events.
        time_step (int or float): The fixed time period by which the model advances
                                  on each step. Defaults to 1.

    Methods:
        schedule_event(time, agent): Schedule an event for a specific time.
        schedule_in(delay, agent): Schedule an event after a specified delay.
        step(): Execute all events within the next time_step period.
        get_next_event_time(): Returns the time of the next scheduled event.

    Usage:
        1. Instantiate the DiscreteEventScheduler with a model instance and a time_step period.
        2. Add agents to the scheduler using schedule.add(). With schedule_now=True (default),
              the first event for the agent will be scheduled immediately.
        3. In the Agent step() method, schedule the next event for the agent
              (using schedule_in or schedule_event).
        3. Add self.schedule.step() to the model's step() method, as usual.

    Now, with each model step, the scheduler will execute all events within the
    next time_step period, and advance time one time_step forward.
    """

    def __init__(self, model: Model, time_step: TimeT = 1) -> None:
        """

        Args:
            model (Model): The model to which the schedule belongs
            time_step (TimeT): The fixed time step between steps

        """
        super().__init__(model)
        self.event_queue: list[tuple[TimeT, float, weakref.ref]] = []
        self.time_step: TimeT = time_step  # Fixed time period for each step

        warnings.warn(
            "The DiscreteEventScheduler is experimental. It may be changed or removed in any and all future releases, including patch releases.\n"
            "We would love to hear what you think about this new feature. If you have any thoughts, share them with us here: https://github.com/projectmesa/mesa/discussions/1923",
            FutureWarning,
            stacklevel=2,
        )

    def schedule_event(self, time: TimeT, agent: Agent) -> None:
        """Schedule an event for an agent at a specific time."""
        if time < self.time:
            raise ValueError(
                f"Scheduled time ({time}) must be >= the current time ({self.time})"
            )
        if agent not in self._agents:
            raise ValueError(
                "trying to schedule an event for agent which is not known to the scheduler"
            )

        # Create an event, sorted first on time, secondary on a random value
        event = (time, self.model.random.random(), weakref.ref(agent))
        heapq.heappush(self.event_queue, event)

    def schedule_in(self, delay: TimeT, agent: Agent) -> None:
        """Schedule an event for an agent after a specified delay."""
        if delay < 0:
            raise ValueError("Delay must be non-negative")
        event_time = self.time + delay
        self.schedule_event(event_time, agent)

    def step(self) -> None:
        """Execute the next event and advance the time."""
        end_time = self.time + self.time_step

        while self.event_queue and self.event_queue[0][0] <= end_time:
            # Get the next event (ignore the random value during unpacking)
            time, _, agent = heapq.heappop(self.event_queue)
            agent = agent()  # unpack weakref

            if agent:
                # Advance time to the event's time
                self.time = time
                # Execute the event
                agent.step()

        # After processing events, advance time by the time_step
        self.time = end_time
        self.steps += 1

    def get_next_event_time(self) -> TimeT | None:
        """Returns the time of the next scheduled event."""
        if not self.event_queue:
            return None
        return self.event_queue[0][0]

    def add(self, agent: Agent, schedule_now: bool = True) -> None:
        """Add an Agent object to the schedule and optionally schedule its first event.

        Args:
            agent: An Agent to be added to the schedule. Must have a step() method.
            schedule_now: If True, schedules the first event for the agent immediately.
        """
        super().add(agent)  # Call the add method from BaseScheduler

        if schedule_now:
            # Schedule the first event immediately
            self.schedule_event(self.time, agent)
