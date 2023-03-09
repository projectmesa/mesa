"""
Test the advanced schedulers.
"""

import unittest
from unittest import TestCase, mock

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

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.steps = 0
        self.advances = 0

    def kill_other_agent(self):
        for agent in self.model.schedule.agents:
            if agent is not self:
                self.model.schedule.remove(agent)
                break

    def stage_one(self):
        if self.model.enable_kill_other_agent:
            self.kill_other_agent()
        self.model.log.append(self.unique_id + "_1")

    def stage_two(self):
        self.model.log.append(self.unique_id + "_2")

    def advance(self):
        self.advances += 1

    def step(self):
        if self.model.enable_kill_other_agent:
            self.kill_other_agent()
        self.steps += 1
        self.model.log.append(self.unique_id)


class MockModel(Model):
    def __init__(self, shuffle=False, activation=STAGED, enable_kill_other_agent=False):
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
        self.log = []
        self.enable_kill_other_agent = enable_kill_other_agent

        # Make scheduler
        if activation == STAGED:
            model_stages = ["stage_one", "stage_two"]
            self.schedule = StagedActivation(self, model_stages, shuffle=shuffle)
        elif activation == RANDOM:
            self.schedule = RandomActivation(self)
        elif activation == SIMULTANEOUS:
            self.schedule = SimultaneousActivation(self)
        elif activation == RANDOM_BY_TYPE:
            self.schedule = RandomActivationByType(self)
        else:
            self.schedule = BaseScheduler(self)

        # Make agents
        for name in ["A", "B"]:
            agent = MockAgent(name, self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()


class TestStagedActivation(TestCase):
    """
    Test the staged activation.
    """

    expected_output = ["A_1", "B_1", "A_2", "B_2"]

    def test_no_shuffle(self):
        """
        Testing the staged activation without shuffling.
        """
        model = MockModel(shuffle=False)
        model.step()
        model.step()
        assert all(i == j for i, j in zip(model.log[:4], model.log[4:]))

    def test_shuffle(self):
        """
        Test the staged activation with shuffling
        """
        model = MockModel(shuffle=True)
        model.step()
        for output in self.expected_output[:2]:
            assert output in model.log[:2]
        for output in self.expected_output[2:]:
            assert output in model.log[2:]

    def test_shuffle_shuffles_agents(self):
        model = MockModel(shuffle=True)
        model.random = mock.Mock()
        assert model.random.shuffle.call_count == 0
        model.step()
        assert model.random.shuffle.call_count == 1

    def test_remove(self):
        """
        Test the staged activation can remove an agent
        """
        model = MockModel(shuffle=True)
        agent_keys = list(model.schedule._agents.keys())
        agent = model.schedule._agents[agent_keys[0]]
        model.schedule.remove(agent)
        assert agent not in model.schedule.agents

    def test_intrastep_remove(self):
        """
        Test the staged activation can remove an agent in a
        step of another agent so that the one removed doesn't step.
        """
        model = MockModel(shuffle=True, enable_kill_other_agent=True)
        model.step()
        assert len(model.log) == 2

    def test_add_existing_agent(self):
        model = MockModel()
        agent = model.schedule.agents[0]
        with self.assertRaises(Exception):
            model.schedule.add(agent)


class TestRandomActivation(TestCase):
    """
    Test the random activation.
    """

    def test_random_activation_step_shuffles(self):
        """
        Test the random activation step
        """
        model = MockModel(activation=RANDOM)
        model.random = mock.Mock()
        model.schedule.step()
        assert model.random.shuffle.call_count == 1

    def test_random_activation_step_increments_step_and_time_counts(self):
        """
        Test the random activation step increments step and time counts
        """
        model = MockModel(activation=RANDOM)
        assert model.schedule.steps == 0
        assert model.schedule.time == 0
        model.schedule.step()
        assert model.schedule.steps == 1
        assert model.schedule.time == 1

    def test_random_activation_step_steps_each_agent(self):
        """
        Test the random activation step causes each agent to step
        """
        model = MockModel(activation=RANDOM)
        model.step()
        agent_steps = [i.steps for i in model.schedule.agents]
        # one step for each of 2 agents
        assert all(x == 1 for x in agent_steps)

    def test_intrastep_remove(self):
        """
        Test the random activation can remove an agent in a
        step of another agent so that the one removed doesn't step.
        """
        model = MockModel(activation=RANDOM, enable_kill_other_agent=True)
        model.step()
        assert len(model.log) == 1


class TestSimultaneousActivation(TestCase):
    """
    Test the simultaneous activation.
    """

    def test_simultaneous_activation_step_steps_and_advances_each_agent(self):
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


class TestRandomActivationByType(TestCase):
    """
    Test the random activation by type.
    TODO implement at least 2 types of agents, and test that step_type only
    does step for one type of agents, not the entire agents.
    """

    def test_random_activation_step_shuffles(self):
        """
        Test the random activation by type step
        """
        model = MockModel(activation=RANDOM_BY_TYPE)
        model.random = mock.Mock()
        model.schedule.step()
        assert model.random.shuffle.call_count == 2

    def test_random_activation_step_increments_step_and_time_counts(self):
        """
        Test the random activation by type step increments step and time counts
        """
        model = MockModel(activation=RANDOM_BY_TYPE)
        assert model.schedule.steps == 0
        assert model.schedule.time == 0
        model.schedule.step()
        assert model.schedule.steps == 1
        assert model.schedule.time == 1

    def test_random_activation_step_steps_each_agent(self):
        """
        Test the random activation by type step causes each agent to step
        """

        model = MockModel(activation=RANDOM_BY_TYPE)
        model.step()
        agent_steps = [i.steps for i in model.schedule.agents]
        # one step for each of 2 agents
        assert all(x == 1 for x in agent_steps)

    def test_add_non_unique_ids(self):
        """
        Test that adding agent with duplicate ids result in an error.
        TODO: we need to run this test on all schedulers, not just
        RandomActivationByType.
        """
        model = MockModel(activation=RANDOM_BY_TYPE)
        a = MockAgent(0, model)
        b = MockAgent(0, model)
        model.schedule.add(a)
        with self.assertRaises(Exception):
            model.schedule.add(b)


if __name__ == "__main__":
    unittest.main()
