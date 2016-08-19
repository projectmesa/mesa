"""
Test the BatchRunner
"""
import unittest

from mesa import Agent, Model
from mesa.batchrunner import BatchRunner
from mesa.time import BaseScheduler

NUM_AGENTS = 7


class MockAgent(Agent):
    """
    Minimalistic model for testing purposes
    """
    def __init__(self, unique_id, val):
        self.unique_id = unique_id
        self.val = val

    def step(self):
        """
        increment val by 1
        """
        self.val += 1


class MockModel(Model):
    """
    Minimalistic model for testing purposes
    """
    def __init__(self, model_param, agent_param):
        """
        Args:
            model_param (any): parameter specific to the model
            agent_param (int): parameter specific to the agent
        """
        self.schedule = BaseScheduler(None)
        self.model_param = model_param
        self.running = True
        for i in range(NUM_AGENTS):
            a = MockAgent(i, agent_param)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()


class DictionaryMockModel(MockModel):

    def __init__(self, dict_model_param, agent_param):
        super().__init__(dict_model_param, agent_param)


class TestBatchRunner(unittest.TestCase):
    """
    Test that BatchRunner is running batches
    """
    def setUp(self):
        """
        Create the model and run it for some steps
        """
        self.params = {
            'model_param': range(3),
            'agent_param': [1, 8],
        }
        self.batch = self.create_batch_runner(self.params, MockModel)
        self.batch.run_all()

    def create_batch_runner(self, runner_params, model):
        """
        Helper method to create runner with specific parameters.
        """
        self.model_reporter = {"model": lambda m: m.model_param}
        self.agent_reporter = {
            "agent_id": lambda a: a.unique_id,
            "agent_val": lambda a: a.val}
        self.iterations = 17
        batch = BatchRunner(
            model,
            runner_params,
            iterations=self.iterations,
            max_steps=3,
            model_reporters=self.model_reporter,
            agent_reporters=self.agent_reporter)
        return batch

    def test_model_level_vars(self):
        """
        Test that model-level variable collection is of the correct size
        """
        model_vars = self.batch.get_model_vars_dataframe()
        rows = len(self.params['model_param']) * \
            len(self.params['agent_param']) * \
            self.iterations
        assert model_vars.shape == (rows, 4)

    def test_agent_level_vars(self):
        """
        Test that agent-level variable collection is of the correct size
        """
        agent_vars = self.batch.get_agent_vars_dataframe()
        rows = NUM_AGENTS * \
            len(self.params['agent_param']) * \
            len(self.params['model_param']) * \
            self.iterations
        assert agent_vars.shape == (rows, 6)

    def test_passing_dictionary_argument_into_batch_runner(self):
        """
        Tests that batch runner properly processes arguments of
        dictionary type.
        """
        # This test is a little bit cumbersome b/c it ignores setUp() call
        # and creates runner from scratch.

        params = {'dict_model_param': {'width': 10, 'height': 10},
                  'agent_param': [10, 100, 1000]}
        batch = self.create_batch_runner(params, DictionaryMockModel)

        batch.run_all()
        model_vars = batch.get_model_vars_dataframe()
        agent_vars = batch.get_agent_vars_dataframe()

        assert "dict_model_param" in model_vars.columns
        assert len(model_vars.dict_model_param.unique()) == 1
        assert "dict_model_param" in agent_vars.columns
        assert len(agent_vars.dict_model_param.unique()) == 1
        expected = params['dict_model_param']
        actual = dict(model_vars.dict_model_param.unique()[0])
        assert actual == expected
