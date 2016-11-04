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
    def __init__(self, unique_id, model, val):
        super().__init__(unique_id, model)
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
        super().__init__()
        self.schedule = BaseScheduler(None)
        self.model_param = model_param
        self.running = True
        for i in range(NUM_AGENTS):
            a = MockAgent(i, self, agent_param)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()


class DictionaryMockModel(MockModel):
    """
    A model that accepts additional parameters scalar and dictionary parameters.
    """

    def __init__(self, model_param, agent_param,
                 fixed_scalar, fixed_dictionary):
        super().__init__(model_param, agent_param)
        self.fixed_scalar = fixed_scalar
        self.fixed_dictionary = fixed_dictionary


class VarArgsMockModel(MockModel):
    """
    A model that accepts additional kwargs.
    """

    def __init__(self, model_param, agent_param, **kwargs):
        super().__init__(model_param, agent_param)
        self.fixed_value = kwargs.get('fixed_value')
        self.variable_value = kwargs.get('variable_value')


def launch_batch_processing(test_case):
    batch = BatchRunner(
        test_case.mock_model,
        variable_parameters=test_case.variable_params,
        fixed_parameters=test_case.fixed_params,
        iterations=test_case.iterations,
        max_steps=test_case.max_steps,
        model_reporters=test_case.model_reporter,
        agent_reporters=test_case.agent_reporter)
    batch.run_all()
    return batch


class TestBatchRunner(unittest.TestCase):
    """
    Test that BatchRunner is running batches
    """
    def setUp(self):
        """
        Create the model and run it for some steps
        """
        self.mock_model = MockModel
        self.model_reporter = {"model": lambda m: m.model_param}
        self.agent_reporter = {
            "agent_id": lambda a: a.unique_id,
            "agent_val": lambda a: a.val}
        self.variable_params = {
            'model_param': range(3),
            'agent_param': [1, 8],
        }
        self.fixed_params = None
        self.iterations = 17
        self.max_steps = 3

    def test_model_level_vars(self):
        """
        Test that model-level variable collection is of the correct size
        """
        self.batch = launch_batch_processing(self)

        model_vars = self.batch.get_model_vars_dataframe()
        rows = (len(self.variable_params['model_param']) *
                len(self.variable_params['agent_param']) *
                self.iterations)
        assert model_vars.shape == (rows, 4)

    def test_agent_level_vars(self):
        """
        Test that agent-level variable collection is of the correct size
        """
        self.batch = launch_batch_processing(self)

        agent_vars = self.batch.get_agent_vars_dataframe()
        rows = (NUM_AGENTS *
                len(self.variable_params['agent_param']) *
                len(self.variable_params['model_param']) *
                self.iterations)
        assert agent_vars.shape == (rows, 6)

    # TODO: going to add more extensive testing, just basic sanity checks now

    def test_dictionary_init_model(self):
        self.mock_model = DictionaryMockModel
        self.fixed_params = {'fixed_scalar': 1, 'fixed_dictionary': {'x': 42}}
        self.batch = launch_batch_processing(self)

        agent_vars = self.batch.get_agent_vars_dataframe()
        rows = (NUM_AGENTS *
                len(self.variable_params['agent_param']) *
                len(self.variable_params['model_param']) *
                self.iterations)
        assert agent_vars.shape == (rows, 6)

    def test_kwargs_init_model(self):
        self.mock_model = VarArgsMockModel
        old_params = self.variable_params.copy()
        old_params['variable_value'] = [1, 2, 3]
        self.variable_params = old_params
        self.fixed_params = {'fixed_value': 1}
        self.batch = launch_batch_processing(self)

        agent_vars = self.batch.get_agent_vars_dataframe()
        rows = (NUM_AGENTS *
                len(self.variable_params['agent_param']) *
                len(self.variable_params['model_param']) *
                len(self.variable_params['variable_value']) *
                self.iterations)
        assert agent_vars.shape == (rows, 7)
