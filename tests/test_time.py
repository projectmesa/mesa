"""
Test the advanced schedulers.
"""

# import unittest
# from unittest import TestCase, mock

from mesa import Agent, Model
from mesa.time import (
    BaseScheduler,
    RandomActivation,
    RandomActivationByType,
    SimultaneousActivation,
    StagedActivation,
)

RANDOM = "random"
STAGED = "staged"
SIMULTANEOUS = "simultaneous"
RANDOM_BY_TYPE = "random_by_type"


class MockAgent(Agent):
    """
    Minimalistic agent for testing purposes.
    """

    def __init__(self, model):
        super().__init__(model)
        self.steps = 0
        self.advances = 0

    def kill_other_agent(self):
        for agent in self.model.schedule.agents:
            if agent is not self:
                agent.remove()

    def stage_one(self):
        if self.model.enable_kill_other_agent:
            self.kill_other_agent()
        self.model.log.append(f"{self.unique_id}_1")

    def stage_two(self):
        self.model.log.append(f"{self.unique_id}_2")

    def advance(self):
        self.advances += 1

    def step(self):
        if self.model.enable_kill_other_agent:
            self.kill_other_agent()
        self.steps += 1
        self.model.log.append(self.unique_id)


class Model:
    import random

    def __init__(self, *args, seed=None, **kwargs):
        """Create a new model. Overload this method with the actual code to
        start the model. Always start with super().__init__() to initialize the
        model object properly.
        """
        super().__init__(*args, **kwargs)
        self.running = True
        self.schedule = None
        self.steps: int = 0

        self._setup_agent_registration()

        self._seed = seed
        if self._seed is None:
            # We explicitly specify the seed here so that we know its value in
            # advance.
            self._seed = random.random()
            self.random = random.Random(self._seed)

        # Wrap the user-defined step method
        self._user_step = self.step
        self.step = self._wrapped_step

    def _wrapped_step(self, *args: Any, **kwargs: Any) -> None:
        """Automatically increments time and steps after calling the user's step method."""
        # Automatically increment time and step counters
        self.steps += 1
        # Call the original user-defined step method
        self._user_step(*args, **kwargs)

    def next_id(self) -> int:
        warnings.warn(
            "using model.next_id() is deprecated. Agents track their unique ID automatically",
            DeprecationWarning,
            stacklevel=2,
        )
        return 0

    @property
    def agents(self) -> AgentSet:
        """Provides an AgentSet of all agents in the model, combining agents from all types."""
        return self._all_agents

    @agents.setter
    def agents(self, agents: Any) -> None:
        raise AttributeError(
            "You are trying to set model.agents. In Mesa 3.0 and higher, this attribute is "
            "used by Mesa itself, so you cannot use it directly anymore."
            "Please adjust your code to use a different attribute name for custom agent storage."
        )

    @property
    def agent_types(self) -> list[type]:
        """Return a list of all unique agent types registered with the model."""
        return list(self._agents_by_type.keys())

    @property
    def agents_by_type(self) -> dict[type[Agent], AgentSet]:
        """A dictionary where the keys are agent types and the values are the corresponding AgentSets."""
        return self._agents_by_type

    def get_agents_of_type(self, agenttype: type[Agent]) -> AgentSet:
        """Deprecated: Retrieves an AgentSet containing all agents of the specified type."""
        warnings.warn(
            f"Model.get_agents_of_type() is deprecated, please replace get_agents_of_type({agenttype})"
            f"with the property agents_by_type[{agenttype}].",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.agents_by_type[agenttype]

    def _setup_agent_registration(self):
        """helper method to initialize the agent registration datastructures"""
        self._agents = {}  # the hard references to all agents in the model
        self._agents_by_type: dict[
            type[Agent], AgentSet
        ] = {}  # a dict with an agentset for each class of agents
        self._all_agents = AgentSet([], self)  # an agenset with all agents

    def register_agent(self, agent):
        """Register the agent with the model

        Args:
            agent: The agent to register.

        Notes:
            This method is called automatically by ``Agent.__init__``, so there is no need to use this
            if you are subclassing Agent and calling its super in the ``__init__`` method.

        """
        if not hasattr(self, "_agents"):
            self._setup_agent_registration()

            warnings.warn(
                "The Mesa Model class was not initialized. In the future, you need to explicitly initialize "
                "the Model by calling super().__init__() on initialization.",
                FutureWarning,
                stacklevel=2,
            )

        self._agents[agent] = None

        # because AgentSet requires model, we cannot use defaultdict
        # tricks with a function won't work because model then cannot be pickled
        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet(
                [
                    agent,
                ],
                self,
            )

        self._all_agents.add(agent)

    def deregister_agent(self, agent):
        """Deregister the agent with the model

        Notes::
        This method is called automatically by ``Agent.remove``

        """
        del self._agents[agent]
        self._agents_by_type[type(agent)].remove(agent)
        self._all_agents.remove(agent)

    def run_model(self) -> None:
        """Run the model until the end condition is reached. Overload as
        needed.
        """
        while self.running:
            self.step()

    def step(self) -> None:
        """A single step. Fill in here."""

    def reset_randomizer(self, seed: int | None = None) -> None:
        """Reset the model random number generator.

        Args:
            seed: A new seed for the RNG; if None, reset using the current seed
        """

        if seed is None:
            seed = self._seed
        self.random.seed(seed)
        self._seed = seed

    def initialize_data_collector(
        self,
        model_reporters=None,
        agent_reporters=None,
        tables=None,
    ) -> None:
        if not hasattr(self, "schedule") or self.schedule is None:
            raise RuntimeError(
                "You must initialize the scheduler (self.schedule) before initializing the data collector."
            )
        if self.schedule.get_agent_count() == 0:
            raise RuntimeError(
                "You must add agents to the scheduler before initializing the data collector."
            )
        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters,
            tables=tables,
        )
        # Collect data for the first time during initialization.
        self.datacollector.collect(self)


class SomeModel(Model):
    def __init__(self, some_number, seed=None, some_other_argument=5):
        super().__init__(seed=seed)
        self.some_number = some_number
        self.some_other_argument = some_other_argument


class MockModel(Model):
    def __init__(
        self, seed=None, shuffle=False, activation=STAGED, enable_kill_other_agent=False
    ):
        """
        Creates a Model instance with a schedule

        Args:
            shuffle (Bool): whether or not to instantiate a scheduler
                            with shuffling.
                            This option is only used for
                            StagedActivation schedulers.

            activation (str): which kind of scheduler to use.
                              'random' creates a RandomActivation scheduler.
                              'staged' creates a StagedActivation scheduler.
                              The default scheduler is a BaseScheduler.
        """
        super().__init__(seed=seed)
        self.log = []
        self.enable_kill_other_agent = enable_kill_other_agent

        # Make scheduler
        if activation == STAGED:
            model_stages = ["stage_one", "model.model_stage", "stage_two"]
            self.schedule = StagedActivation(
                self, stage_list=model_stages, shuffle=shuffle
            )
        elif activation == RANDOM:
            self.schedule = RandomActivation(self)
        elif activation == SIMULTANEOUS:
            self.schedule = SimultaneousActivation(self)
        elif activation == RANDOM_BY_TYPE:
            self.schedule = RandomActivationByType(self)
        else:
            self.schedule = BaseScheduler(self)

        # Make agents
        for _ in range(2):
            agent = MockAgent(self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()

    def model_stage(self):
        self.log.append("model_stage")


def test_some_model():
    some_model = SomeModel(5)
    some_model = SomeModel(5, seed=10)
    some_model = SomeModel(5, some_other_argument=10)
    some_model.some_number = 6


# def test_StagedActivation_no_shuffle():
#     """
#     Testing the staged activation without shuffling.
#     """
#     try:
#         model = SomeModel(shuffle=False)
#     except TypeError as e:
#         print_tb(e.__traceback__)
#         raise e
#
#     model.step()
#     model.step()
#     assert all(i == j for i, j in zip(model.log[:5], model.log[5:]))
#
#
# def test_StagedActivation_shuffle():
#     """
#     Test the staged activation with shuffling
#     """
#     expected_output = ["1_1", "1_1", "model_stage", "1_2", "1_2"]
#
#     model = MockModel(shuffle=True)
#     model.step()
#     for output in expected_output[:2]:
#         assert output in model.log[:2]
#     for output in expected_output[3:]:
#         assert output in model.log[3:]
#     assert expected_output[2] == model.log[2]
#
#
# def test_StagedActivation_shuffle_shuffles_agents():
#     model = MockModel(shuffle=True)
#     model.random = mock.Mock()
#     assert model.random.shuffle.call_count == 0
#     model.step()
#     assert model.random.shuffle.call_count == 1
#
#
# def test_StagedActivation_remove():
#     """
#     Test the staged activation can remove an agent
#     """
#     model = MockModel(shuffle=True)
#     agents = list(model.schedule._agents)
#     agent = agents[0]
#     model.schedule.remove(agents[0])
#     assert agent not in model.schedule.agents
#
#
# def test_StagedActivation_intrastep_remove():
#     """
#     Test the staged activation can remove an agent in a
#     step of another agent so that the one removed doesn't step.
#     """
#     model = MockModel(shuffle=True, enable_kill_other_agent=True)
#     model.step()
#     assert len(model.log) == 3
#
#
# def test_StagedActivation_add_existing_agent():
#     model = MockModel()
#     agent = model.schedule.agents[0]
#
#     with pytest.raises(ValueError):
#         model.schedule.add(agent)
#
#
# def test_RandomActivation_init():
#     model = Model()
#     agents = [MockAgent(model) for _ in range(10)]
#
#     scheduler = RandomActivation(model, agents)
#     assert all(agent in scheduler.agents for agent in agents)
#
#
# def test_RandomActivation_step_shuffles():
#     """
#     Test the random activation step
#     """
#     model = MockModel(activation=RANDOM)
#     model.random = mock.Mock()
#     model.schedule.step()
#     assert model.random.shuffle.call_count == 1
#
#
# def test_RandomActivation_step_increments_step_and_time_counts():
#     """
#     Test the random activation step increments step and time counts
#     """
#     model = MockModel(activation=RANDOM)
#     assert model.schedule.steps == 0
#     assert model.schedule.time == 0
#     model.schedule.step()
#     assert model.schedule.steps == 1
#     assert model.schedule.time == 1
#
#
# def test_RandomActivation_step_steps_each_agent():
#     """
#     Test the random activation step causes each agent to step
#     """
#     model = MockModel(activation=RANDOM)
#     model.step()
#     agent_steps = [i.steps for i in model.schedule.agents]
#     # one step for each of 2 agents
#     assert all(x == 1 for x in agent_steps)
#
#
# def test_RandomActivation_intrastep_remove():
#     """
#     Test the random activation can remove an agent in a
#     step of another agent so that the one removed doesn't step.
#     """
#     model = MockModel(activation=RANDOM, enable_kill_other_agent=True)
#     model.step()
#     assert len(model.log) == 1
#
#
# def test_RandomActivation_get_agent_keys():
#     model = MockModel(activation=RANDOM)
#
#     keys = model.schedule.get_agent_keys()
#     agent_ids = [agent.unique_id for agent in model.agents]
#     assert all(entry_i == entry_j for entry_i, entry_j in zip(keys, agent_ids))
#
#     keys = model.schedule.get_agent_keys(shuffle=True)
#     agent_ids = {agent.unique_id for agent in model.agents}
#     assert all(entry in agent_ids for entry in keys)
#
#
# def test_RandomActivation_not_sequential():
#     model = MockModel(activation=RANDOM)
#     # Create 10 agents
#     for _ in range(10):
#         model.schedule.add(MockAgent(model))
#     # Run 3 steps
#     for _ in range(3):
#         model.step()
#     # Filter out non-integer elements from the log
#     filtered_log = [item for item in model.log if isinstance(item, int)]
#
#     # Check that there are no 18 consecutive agents id's in the filtered log
#     total_agents = 10
#     assert not any(
#         all(
#             (filtered_log[(i + j) % total_agents] - filtered_log[i]) % total_agents
#             == j % total_agents
#             for j in range(18)
#         )
#         for i in range(len(filtered_log))
#     ), f"Agents are activated sequentially:\n{filtered_log}"
#
#
# def test_SimultaneousActivation_step_steps_and_advances_each_agent():
#     """
#     Test the simultaneous activation step causes each agent to step
#     """
#     model = MockModel(activation=SIMULTANEOUS)
#     model.step()
#     # one step for each of 2 agents
#     agent_steps = [i.steps for i in model.schedule.agents]
#     agent_advances = [i.advances for i in model.schedule.agents]
#     assert all(x == 1 for x in agent_steps)
#     assert all(x == 1 for x in agent_advances)
#
#
# def test_RandomActivationByType_init():
#     model = Model()
#     agents = [MockAgent(model) for _ in range(10)]
#     agents += [Agent(model) for _ in range(10)]
#
#     scheduler = RandomActivationByType(model, agents)
#     assert all(agent in scheduler.agents for agent in agents)
#
#
# def test_RandomActivationByType_step_shuffles():
#     """
#     Test the random activation by type step
#     """
#     model = MockModel(activation=RANDOM_BY_TYPE)
#     model.random = mock.Mock()
#     model.schedule.step()
#     assert model.random.shuffle.call_count == 2
#
#
# def test_RandomActivationByType_step_increments_step_and_time_counts():
#     """
#     Test the random activation by type step increments step and time counts
#     """
#     model = MockModel(activation=RANDOM_BY_TYPE)
#     assert model.schedule.steps == 0
#     assert model.schedule.time == 0
#     model.schedule.step()
#     assert model.schedule.steps == 1
#     assert model.schedule.time == 1
#
#
# def test_RandomActivationByType_step_steps_each_agent():
#     """
#     Test the random activation by type step causes each agent to step
#     """
#
#     model = MockModel(activation=RANDOM_BY_TYPE)
#     model.step()
#     agent_steps = [i.steps for i in model.schedule.agents]
#     # one step for each of 2 agents
#     assert all(x == 1 for x in agent_steps)
#
#
# def test_RandomActivationByType_counts():
#     """
#     Test the random activation by type step causes each agent to step
#     """
#
#     model = MockModel(activation=RANDOM_BY_TYPE)
#
#     agent_types = model.agent_types
#     for agent_type in agent_types:
#         assert model.schedule.get_type_count(agent_type) == len(
#             model.agents_by_type[agent_type]
#         )
#
#     # def test_add_non_unique_ids(self):
#     #     """
#     #     Test that adding agent with duplicate ids result in an error.
#     #     TODO: we need to run this test on all schedulers, not just
#     #     TODO:: identical IDs is something for the agent, not the scheduler and should be tested there
#     #     RandomActivationByType.
#     #     """
#     #     model = MockModel(activation=RANDOM_BY_TYPE)
#     #     a = MockAgent(0, model)
#     #     b = MockAgent(0, model)
#     #     model.schedule.add(a)
#     #     with self.assertRaises(Exception):
#     #         model.schedule.add(b)
