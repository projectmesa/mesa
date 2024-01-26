"""
Test the advanced schedulers.
"""

import unittest
from unittest import TestCase, mock

from mesa import Agent, Model
from mesa.time import (
    BaseScheduler,
    DiscreteEventScheduler,
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
                agent.remove()

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
        super().__init__()
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
        for name in ["A", "B"]:
            agent = MockAgent(name, self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()

    def model_stage(self):
        self.log.append("model_stage")


class TestStagedActivation(TestCase):
    """
    Test the staged activation.
    """

    expected_output = ["A_1", "B_1", "model_stage", "A_2", "B_2"]

    def test_no_shuffle(self):
        """
        Testing the staged activation without shuffling.
        """
        model = MockModel(shuffle=False)
        model.step()
        model.step()
        assert all(i == j for i, j in zip(model.log[:5], model.log[5:]))

    def test_shuffle(self):
        """
        Test the staged activation with shuffling
        """
        model = MockModel(shuffle=True)
        model.step()
        for output in self.expected_output[:2]:
            assert output in model.log[:2]
        for output in self.expected_output[3:]:
            assert output in model.log[3:]
        assert self.expected_output[2] == model.log[2]

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
        agents = list(model.schedule._agents)
        agent = agents[0]
        model.schedule.remove(agents[0])
        assert agent not in model.schedule.agents

    def test_intrastep_remove(self):
        """
        Test the staged activation can remove an agent in a
        step of another agent so that the one removed doesn't step.
        """
        model = MockModel(shuffle=True, enable_kill_other_agent=True)
        model.step()
        assert len(model.log) == 3

    def test_add_existing_agent(self):
        model = MockModel()
        agent = model.schedule.agents[0]
        with self.assertRaises(Exception):
            model.schedule.add(agent)


class TestRandomActivation(TestCase):
    """
    Test the random activation.
    """

    def test_init(self):
        model = Model()
        agents = [MockAgent(model.next_id(), model) for _ in range(10)]

        scheduler = RandomActivation(model, agents)
        assert all(agent in scheduler.agents for agent in agents)

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

    def test_get_agent_keys(self):
        model = MockModel(activation=RANDOM)

        keys = model.schedule.get_agent_keys()
        agent_ids = [agent.unique_id for agent in model.agents]
        assert all(entry_i == entry_j for entry_i, entry_j in zip(keys, agent_ids))

        keys = model.schedule.get_agent_keys(shuffle=True)
        agent_ids = {agent.unique_id for agent in model.agents}
        assert all(entry in agent_ids for entry in keys)


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

    def test_init(self):
        model = Model()
        agents = [MockAgent(model.next_id(), model) for _ in range(10)]
        agents += [Agent(model.next_id(), model) for _ in range(10)]

        scheduler = RandomActivationByType(model, agents)
        assert all(agent in scheduler.agents for agent in agents)

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

    def test_random_activation_counts(self):
        """
        Test the random activation by type step causes each agent to step
        """

        model = MockModel(activation=RANDOM_BY_TYPE)

        agent_types = model.agent_types
        for agent_type in agent_types:
            assert model.schedule.get_type_count(agent_type) == len(
                model.get_agents_of_type(agent_type)
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


class TestDiscreteEventScheduler(TestCase):
    def setUp(self):
        self.model = MockModel()
        self.scheduler = DiscreteEventScheduler(self.model, time_step=1)
        self.model.schedule = self.scheduler
        self.agent1 = MockAgent(1, self.model)
        self.agent2 = MockAgent(2, self.model)
        self.model.schedule.add(self.agent1, schedule_now=False)
        self.model.schedule.add(self.agent2, schedule_now=False)

    # Testing Initialization and Attributes
    def test_initialization(self):
        self.assertIsInstance(self.scheduler.event_queue, list)
        self.assertEqual(self.scheduler.time_step, 1)

    # Testing Event Scheduling
    def test_schedule_event(self):
        self.scheduler.schedule_event(5, self.agent1)
        self.assertEqual(len(self.scheduler.event_queue), 1)
        event_time, _, event_agent = self.scheduler.event_queue[0]
        self.assertEqual(event_time, 5)
        self.assertEqual(event_agent(), self.agent1)

    def test_schedule_event_with_float_time(self):
        self.scheduler.schedule_event(5.5, self.agent1)
        self.assertEqual(len(self.scheduler.event_queue), 1)
        event_time, _, event_agent = self.scheduler.event_queue[0]
        self.assertEqual(event_time, 5.5)
        self.assertEqual(event_agent(), self.agent1)

    def test_schedule_in(self):
        self.scheduler.schedule_in(3, self.agent2)
        _, _, event_agent = self.scheduler.event_queue[0]
        self.assertEqual(event_agent(), self.agent2)
        self.assertEqual(self.scheduler.get_next_event_time(), self.scheduler.time + 3)

    # Testing Event Execution and Time Advancement
    def test_step_function(self):
        self.scheduler.schedule_event(1, self.agent1)
        self.scheduler.schedule_event(2, self.agent2)
        self.scheduler.step()
        self.assertEqual(self.scheduler.time, 1)
        self.assertEqual(self.agent1.steps, 1)
        self.assertEqual(self.agent2.steps, 0)

    def test_time_advancement(self):
        self.scheduler.schedule_event(5, self.agent1)
        self.scheduler.step()
        self.assertEqual(self.scheduler.time, 1)
        self.scheduler.step()
        self.assertEqual(self.scheduler.time, 2)

    def test_no_events(self):
        self.scheduler.step()
        self.assertEqual(self.scheduler.time, 1)

    # Testing Edge Cases and Error Handling
    def test_invalid_event_time(self):
        with self.assertRaises(ValueError):
            self.scheduler.schedule_event(-1, self.agent1)

    def test_invalid_aget_time(self):
        with self.assertRaises(ValueError):
            agent3 = MockAgent(3, self.model)
            self.scheduler.schedule_event(2, agent3)

    def test_immediate_event_execution(self):
        # Current time of the scheduler
        current_time = self.scheduler.time

        # Schedule an event at the current time
        self.scheduler.schedule_event(current_time, self.agent1)

        # Step the scheduler and check if the event is executed immediately
        self.scheduler.step()
        self.assertEqual(self.agent1.steps, 1)

        # The time should advance to the next time step after execution
        self.assertEqual(self.scheduler.time, current_time + 1)

    # Testing Utility Functions
    def test_get_next_event_time(self):
        self.scheduler.schedule_event(10, self.agent1)
        self.assertEqual(self.scheduler.get_next_event_time(), 10)

    # Test add() method with and without immediate scheduling
    def test_add_with_immediate_scheduling(self):
        # Add an agent with schedule_now set to True (default behavior)
        new_agent = MockAgent(3, self.model)
        self.scheduler.add(new_agent)

        # Check if the agent's first event is scheduled immediately
        self.assertEqual(len(self.scheduler.event_queue), 1)
        event_time, _, event_agent = self.scheduler.event_queue[0]
        self.assertEqual(event_time, self.scheduler.time)
        self.assertEqual(event_agent(), new_agent)

        # Step the scheduler and check if the agent's step method is executed
        self.scheduler.step()
        self.assertEqual(new_agent.steps, 1)

    def test_add_without_immediate_scheduling(self):
        # Add an agent with schedule_now set to False
        new_agent = MockAgent(4, self.model)
        self.scheduler.add(new_agent, schedule_now=False)

        # Check if the event queue is not updated
        self.assertEqual(len(self.scheduler.event_queue), 0)

        # Step the scheduler and verify that the agent's step method is not executed
        self.scheduler.step()
        self.assertEqual(new_agent.steps, 0)


if __name__ == "__main__":
    unittest.main()
