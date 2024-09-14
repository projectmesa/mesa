"""
Test the advanced schedulers.
"""

# import unittest
# from unittest import TestCase, mock

from unittest import mock

import pytest

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


class SomeModel(Model):
    def __init__(
        self, seed=None, shuffle=False, activation=STAGED, enable_kill_other_agent=False
    ):
        super().__init__(seed=seed)
        self.log = []
        self.enable_kill_other_agent = enable_kill_other_agent

        match activation:
            case "random":
                self.schedule = RandomActivation(self)
            case "staged":
                model_stages = ["stage_one", "model.model_stage", "stage_two"]
                self.schedule = StagedActivation(
                    self, stage_list=model_stages, shuffle=shuffle
                )
            case "simultaneous":
                self.schedule = SimultaneousActivation(self)
            case "random_by_type":
                self.schedule = RandomActivationByType(self)
            case _:
                self.schedule = BaseScheduler(self)

        for _ in range(2):
            agent = MockAgent(self)
            self.schedule.add(agent)


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


def test_StagedActivation_no_shuffle():
    """
    Testing the staged activation without shuffling.
    """
    model = MockModel(shuffle=False)
    model.step()
    model.step()
    assert all(i == j for i, j in zip(model.log[:5], model.log[5:]))


def test_StagedActivation_shuffle():
    """
    Test the staged activation with shuffling
    """
    expected_output = ["1_1", "1_1", "model_stage", "1_2", "1_2"]

    model = MockModel(shuffle=True)
    model.step()
    for output in expected_output[:2]:
        assert output in model.log[:2]
    for output in expected_output[3:]:
        assert output in model.log[3:]
    assert expected_output[2] == model.log[2]


def test_StagedActivation_shuffle_shuffles_agents():
    model = MockModel(shuffle=True)
    model.random = mock.Mock()
    assert model.random.shuffle.call_count == 0
    model.step()
    assert model.random.shuffle.call_count == 1


def test_StagedActivation_remove():
    """
    Test the staged activation can remove an agent
    """
    model = MockModel(shuffle=True)
    agents = list(model.schedule._agents)
    agent = agents[0]
    model.schedule.remove(agents[0])
    assert agent not in model.schedule.agents


def test_StagedActivation_intrastep_remove():
    """
    Test the staged activation can remove an agent in a
    step of another agent so that the one removed doesn't step.
    """
    model = MockModel(shuffle=True, enable_kill_other_agent=True)
    model.step()
    assert len(model.log) == 3


def test_StagedActivation_add_existing_agent():
    model = MockModel()
    agent = model.schedule.agents[0]

    with pytest.raises(ValueError):
        model.schedule.add(agent)


def test_RandomActivation_init():
    model = Model()
    agents = [MockAgent(model) for _ in range(10)]

    scheduler = RandomActivation(model, agents)
    assert all(agent in scheduler.agents for agent in agents)

def test_RandomActivation_step_shuffles():
    """
    Test the random activation step
    """
    model = MockModel(activation=RANDOM)
    model.random = mock.Mock()
    model.schedule.step()
    assert model.random.shuffle.call_count == 1

def test_RandomActivation_step_increments_step_and_time_counts():
    """
    Test the random activation step increments step and time counts
    """
    model = MockModel(activation=RANDOM)
    assert model.schedule.steps == 0
    assert model.schedule.time == 0
    model.schedule.step()
    assert model.schedule.steps == 1
    assert model.schedule.time == 1

def test_RandomActivation_step_steps_each_agent():
    """
    Test the random activation step causes each agent to step
    """
    model = MockModel(activation=RANDOM)
    model.step()
    agent_steps = [i.steps for i in model.schedule.agents]
    # one step for each of 2 agents
    assert all(x == 1 for x in agent_steps)

def test_RandomActivation_intrastep_remove():
    """
    Test the random activation can remove an agent in a
    step of another agent so that the one removed doesn't step.
    """
    model = MockModel(activation=RANDOM, enable_kill_other_agent=True)
    model.step()
    assert len(model.log) == 1

def test_RandomActivation_get_agent_keys():
    model = MockModel(activation=RANDOM)

    keys = model.schedule.get_agent_keys()
    agent_ids = [agent.unique_id for agent in model.agents]
    assert all(entry_i == entry_j for entry_i, entry_j in zip(keys, agent_ids))

    keys = model.schedule.get_agent_keys(shuffle=True)
    agent_ids = {agent.unique_id for agent in model.agents}
    assert all(entry in agent_ids for entry in keys)

def test_RandomActivation_not_sequential():
    model = MockModel(activation=RANDOM)
    # Create 10 agents
    for _ in range(10):
        model.schedule.add(MockAgent(model))
    # Run 3 steps
    for _ in range(3):
        model.step()
    # Filter out non-integer elements from the log
    filtered_log = [item for item in model.log if isinstance(item, int)]

    # Check that there are no 18 consecutive agents id's in the filtered log
    total_agents = 10
    assert not any(
        all(
            (filtered_log[(i + j) % total_agents] - filtered_log[i]) % total_agents
            == j % total_agents
            for j in range(18)
        )
        for i in range(len(filtered_log))
    ), f"Agents are activated sequentially:\n{filtered_log}"


def test_SimultaneousActivation_step_steps_and_advances_each_agent():
    """
    Test the simultaneous activation step causes each agent to step
    """
    model = MockModel(activation=SIMULTANEOUS)
    model.step()
    # one step for each of 2 agents
    agent_steps = [i.steps for i in model.schedule.agents]
    agent_advances = [i.advances for i in model.schedule.agents]
    assert all(x == 1 for x in agent_steps)
    assert all(x == 1 for x in agent_advances)


def test_RandomActivationByType_init():
    model = Model()
    agents = [MockAgent(model) for _ in range(10)]
    agents += [Agent(model) for _ in range(10)]

    scheduler = RandomActivationByType(model, agents)
    assert all(agent in scheduler.agents for agent in agents)

def test_RandomActivationByType_step_shuffles():
    """
    Test the random activation by type step
    """
    model = MockModel(activation=RANDOM_BY_TYPE)
    model.random = mock.Mock()
    model.schedule.step()
    assert model.random.shuffle.call_count == 2

def test_RandomActivationByType_step_increments_step_and_time_counts():
    """
    Test the random activation by type step increments step and time counts
    """
    model = MockModel(activation=RANDOM_BY_TYPE)
    assert model.schedule.steps == 0
    assert model.schedule.time == 0
    model.schedule.step()
    assert model.schedule.steps == 1
    assert model.schedule.time == 1

def test_RandomActivationByType_step_steps_each_agent():
    """
    Test the random activation by type step causes each agent to step
    """

    model = MockModel(activation=RANDOM_BY_TYPE)
    model.step()
    agent_steps = [i.steps for i in model.schedule.agents]
    # one step for each of 2 agents
    assert all(x == 1 for x in agent_steps)

def test_RandomActivationByType_counts():
    """
    Test the random activation by type step causes each agent to step
    """

    model = MockModel(activation=RANDOM_BY_TYPE)

    agent_types = model.agent_types
    for agent_type in agent_types:
        assert model.schedule.get_type_count(agent_type) == len(
            model.agents_by_type[agent_type]
        )

    # def test_add_non_unique_ids(self):
    #     """
    #     Test that adding agent with duplicate ids result in an error.
    #     TODO: we need to run this test on all schedulers, not just
    #     TODO:: identical IDs is something for the agent, not the scheduler and should be tested there
    #     RandomActivationByType.
    #     """
    #     model = MockModel(activation=RANDOM_BY_TYPE)
    #     a = MockAgent(0, model)
    #     b = MockAgent(0, model)
    #     model.schedule.add(a)
    #     with self.assertRaises(Exception):
    #         model.schedule.add(b)



