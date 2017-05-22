"""
Test the BatchRunner
"""
from functools import reduce
from operator import mul
import unittest

from mesa import Agent, Model
from mesa.time import BaseScheduler
from mesa.batchrunner import BatchRunner


NUM_AGENTS = 7


class MockAgent(Agent):
    """
    Minimalistic agent implementation for testing purposes
    """
    def __init__(self, unique_id, model, val):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.val = val

    def step(self):
        self.val += 1


class MockModel(Model):
    """
    Minimalistic model for testing purposes
    """
    def __init__(self, variable_model_param, variable_agent_param,
                 fixed_model_param=None, schedule=None, **kwargs):
        super().__init__()
        self.schedule = BaseScheduler(None) if schedule is None else schedule
        self.variable_model_param = variable_model_param
        self.variable_agent_param = variable_agent_param
        self.fixed_model_param = fixed_model_param
        self.n_agents = kwargs.get('n_agents', NUM_AGENTS)
        self.running = True
        self.init_agents()

    def init_agents(self):
        for i in range(self.n_agents):
            self.schedule.add(MockAgent(i, self, self.variable_agent_param))

    def step(self):
        self.schedule.step()


class MockDictionaryModel(Model):

    def __init__(self, variable_param, fixed_params):
        super().__init__()
        self.variable_param = variable_param
        self.fixed_name = fixed_params.get('fixed_name', None)
        self.running = True
        self.schedule = BaseScheduler(None)
        self.schedule.add(MockAgent(1, self, 0))

    def step(self):
        self.schedule.step()


class TestBatchRunner(unittest.TestCase):
    """
    Test that BatchRunner is running batches
    """
    def setUp(self):
        self.mock_model = MockModel
        self.model_reporters = {
            "reported_variable_value": lambda m: m.variable_model_param,
            "reported_fixed_value": lambda m: m.fixed_model_param
        }
        self.agent_reporters = {
            "agent_id": lambda a: a.unique_id,
            "agent_val": lambda a: a.val
        }
        self.variable_params = {
            "variable_model_param": range(3),
            "variable_agent_param": [1, 8]
        }
        self.fixed_params = None
        self.iterations = 17
        self.max_steps = 3

    def launch_batch_processing(self):
        batch = BatchRunner(
            self.mock_model,
            variable_parameters=self.variable_params,
            fixed_parameters=self.fixed_params,
            iterations=self.iterations,
            max_steps=self.max_steps,
            model_reporters=self.model_reporters,
            agent_reporters=self.agent_reporters)
        batch.run_all()
        return batch

    @property
    def model_runs(self):
        """
        Returns total number of batch runner's iterations.
        """
        return (reduce(mul, map(len, self.variable_params.values())) *
                self.iterations)

    def test_model_level_vars(self):
        """
        Test that model-level variable collection is of the correct size
        """
        batch = self.launch_batch_processing()
        model_vars = batch.get_model_vars_dataframe()
        expected_cols = (len(self.variable_params) +
                         len(self.model_reporters) +
                         1)  # extra column with run index

        assert model_vars.shape == (self.model_runs, expected_cols)

    def test_agent_level_vars(self):
        """
        Test that agent-level variable collection is of the correct size
        """
        batch = self.launch_batch_processing()
        agent_vars = batch.get_agent_vars_dataframe()
        expected_cols = (len(self.variable_params) +
                         len(self.agent_reporters) +
                         1)  # extra column with run index

        assert agent_vars.shape == (self.model_runs * NUM_AGENTS, expected_cols)

    def test_model_with_fixed_parameters_as_kwargs(self):
        """
        Test that model with fixed parameters passed like kwargs is
        properly handled
        """
        self.fixed_params = {'fixed_model_param': 'Fixed', 'n_agents': 1}
        batch = self.launch_batch_processing()
        model_vars = batch.get_model_vars_dataframe()
        agent_vars = batch.get_agent_vars_dataframe()

        assert len(model_vars) == len(agent_vars)
        assert len(model_vars) == self.model_runs
        assert model_vars['reported_fixed_value'].unique() == ['Fixed']

    def test_model_with_fixed_parameters_as_dict(self):
        self.mock_model = MockDictionaryModel
        self.model_reporters = {'reported_fixed_param': lambda m: m.fixed_name}
        self.agent_reporters = {}
        self.fixed_params = {'fixed_name': 'DictModel'}
        self.variable_params = {'variable_param': [1, 2, 3]}

        batch = self.launch_batch_processing()
        model_vars = batch.get_model_vars_dataframe()
        expected_cols = (len(self.variable_params) +
                         len(self.model_reporters) +
                         1)

        assert model_vars.shape == (self.model_runs, expected_cols)
        assert (model_vars['reported_fixed_param'].iloc[0] ==
                self.fixed_params['fixed_name'])
