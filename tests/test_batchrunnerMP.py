"""
Test the BatchRunner
"""
import unittest
from functools import reduce
from multiprocessing import cpu_count, freeze_support
from operator import mul

from mesa import Agent, Model
from mesa.batchrunner import BatchRunnerMP, ParameterProduct, ParameterSampler
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler

NUM_AGENTS = 7


class MockAgent(Agent):
    """
    Minimalistic agent implementation for testing purposes
    """

    def __init__(self, unique_id, model, val):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.val = val
        self.local = 0

    def step(self):
        self.val += 1
        self.local += 0.25


class MockModel(Model):
    """
    Minimalistic model for testing purposes
    """

    def __init__(
        self,
        variable_model_param,
        variable_agent_param,
        fixed_model_param=None,
        schedule=None,
        **kwargs
    ):
        super().__init__()
        self.schedule = BaseScheduler(None) if schedule is None else schedule
        self.variable_model_param = variable_model_param
        self.variable_agent_param = variable_agent_param
        self.fixed_model_param = fixed_model_param
        self.n_agents = kwargs.get("n_agents", NUM_AGENTS)
        self.datacollector = DataCollector(
            model_reporters={"reported_model_param": self.get_local_model_param},
            agent_reporters={"agent_id": "unique_id", "agent_local": "local"},
        )
        self.running = True
        self.init_agents()

    def get_local_model_param(self):
        return 42

    def init_agents(self):
        for i in range(self.n_agents):
            self.schedule.add(MockAgent(i, self, self.variable_agent_param))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


class MockMixedModel(Model):
    def __init__(self, **other_params):
        super().__init__()
        self.variable_name = other_params.get("variable_name", 42)
        self.fixed_name = other_params.get("fixed_name")
        self.running = True
        self.schedule = BaseScheduler(None)
        self.schedule.add(MockAgent(1, self, 0))

    def step(self):
        self.schedule.step()


class TestBatchRunnerMP(unittest.TestCase):
    """
    Test that BatchRunner is running batches
    """

    def setUp(self):
        self.skipTest("Disabled due to consistent hangs")
        self.mock_model = MockModel
        self.model_reporters = {
            "reported_variable_value": lambda m: m.variable_model_param,
            "reported_fixed_value": lambda m: m.fixed_model_param,
        }
        self.agent_reporters = {"agent_id": "unique_id", "agent_val": "val"}
        self.variable_params = {
            "variable_model_param": range(3),
            "variable_agent_param": [1, 8],
        }
        self.fixed_params = None
        self.iterations = 17
        self.max_steps = 3

    def launch_batch_processing(self):
        batch = BatchRunnerMP(
            self.mock_model,
            nr_processes=None,
            variable_parameters=self.variable_params,
            fixed_parameters=self.fixed_params,
            iterations=self.iterations,
            max_steps=self.max_steps,
            model_reporters=self.model_reporters,
            agent_reporters=self.agent_reporters,
        )

        batch.run_all()
        return batch

    def launch_batch_processing_debug(self):
        """
        Tests with one processor for debugging purposes
        """

        batch = BatchRunnerMP(
            self.mock_model,
            nr_processes=1,
            variable_parameters=self.variable_params,
            fixed_parameters=self.fixed_params,
            iterations=self.iterations,
            max_steps=self.max_steps,
            model_reporters=self.model_reporters,
            agent_reporters=self.agent_reporters,
        )

        batch.run_all()
        return batch

    @property
    def model_runs(self):
        """
        Returns total number of batch runner's iterations.
        """
        return reduce(mul, map(len, self.variable_params.values())) * self.iterations

    def batch_model_vars(self, results):
        model_vars = results.get_model_vars_dataframe()
        model_collector = results.get_collector_model()
        expected_cols = (
            len(self.variable_params) + len(self.model_reporters) + 1
        )  # extra column with run index
        self.assertEqual(model_vars.shape, (self.model_runs, expected_cols))
        self.assertEqual(len(model_collector.keys()), self.model_runs)

    def test_model_level_vars(self):
        """
        Test that model-level variable collection is of the correct size
        """
        batch = self.launch_batch_processing()
        assert batch.processes == cpu_count()
        assert batch.processes != 1
        self.batch_model_vars(batch)

        batch2 = self.launch_batch_processing_debug()
        self.batch_model_vars(batch2)

    def batch_agent_vars(self, result):
        agent_vars = result.get_agent_vars_dataframe()
        agent_collector = result.get_collector_agents()
        # extra columns with run index and agentId
        expected_cols = len(self.variable_params) + len(self.agent_reporters) + 2
        assert "agent_val" in list(agent_vars.columns)
        assert "val_non_existent" not in list(agent_vars.columns)
        assert "agent_id" in list(agent_collector[(0, 1, 1)].columns)
        assert "Step" in list(agent_collector[(0, 1, 5)].index.names)
        assert "nose" not in list(agent_collector[(0, 1, 1)].columns)

        self.assertEqual(
            agent_vars.shape, (self.model_runs * NUM_AGENTS, expected_cols)
        )

        self.assertEqual(
            agent_collector[(0, 1, 0)].shape, (NUM_AGENTS * self.max_steps, 2)
        )

    def test_agent_level_vars(self):
        """
        Test that agent-level variable collection is of the correct size
        """
        batch = self.launch_batch_processing()
        self.batch_agent_vars(batch)

        batch2 = self.launch_batch_processing_debug()
        self.batch_agent_vars(batch2)

    def test_model_with_fixed_parameters_as_kwargs(self):
        """
        Test that model with fixed parameters passed like kwargs is
        properly handled
        """
        self.fixed_params = {"fixed_model_param": "Fixed", "n_agents": 1}
        batch = self.launch_batch_processing()
        model_vars = batch.get_model_vars_dataframe()
        agent_vars = batch.get_agent_vars_dataframe()

        self.assertEqual(len(model_vars), len(agent_vars))
        self.assertEqual(len(model_vars), self.model_runs)
        self.assertEqual(model_vars["reported_fixed_value"].unique(), ["Fixed"])

    def test_model_with_variable_and_fixed_kwargs(self):
        self.mock_model = MockMixedModel
        self.model_reporters = {
            "reported_fixed_param": lambda m: m.fixed_name,
            "reported_variable_param": lambda m: m.variable_name,
        }
        self.fixed_params = {"fixed_name": "Fixed"}
        self.variable_params = {"variable_name": [1, 2, 3]}
        batch = self.launch_batch_processing()
        model_vars = batch.get_model_vars_dataframe()
        expected_cols = (
            len(self.variable_params)
            + len(self.fixed_params)
            + len(self.model_reporters)
            + 1
        )
        self.assertEqual(model_vars.shape, (self.model_runs, expected_cols))
        self.assertEqual(
            model_vars["reported_fixed_param"].iloc[0], self.fixed_params["fixed_name"]
        )


class TestParameters(unittest.TestCase):
    def test_product(self):
        params = ParameterProduct({"var_alpha": ["a", "b", "c"], "var_num": [10, 20]})

        lp = list(params)
        self.assertCountEqual(
            lp,
            [
                {"var_alpha": "a", "var_num": 10},
                {"var_alpha": "a", "var_num": 20},
                {"var_alpha": "b", "var_num": 10},
                {"var_alpha": "b", "var_num": 20},
                {"var_alpha": "c", "var_num": 10},
                {"var_alpha": "c", "var_num": 20},
            ],
        )

    def test_sampler(self):
        params1 = ParameterSampler(
            {
                "var_alpha": ["a", "b", "c", "d", "e"],
                "var_num": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            },
            n=10,
            random_state=1,
        )
        params2 = ParameterSampler(
            {"var_alpha": ["a", "b", "c", "d", "e"], "var_num": range(16)},
            n=10,
            random_state=1,
        )

        lp = list(params1)
        self.assertEqual(10, len(lp))
        self.assertEqual(lp, list(params2))


if __name__ == "__main__":
    freeze_support()
    unittest.main()
