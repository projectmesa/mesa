"""Test the DataCollector."""

import unittest

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler


class MockAgent(Agent):
    """Minimalistic agent for testing purposes."""

    def __init__(self, model, val=0):  # noqa: D107
        super().__init__(model)
        self.val = val
        self.val2 = val

    def step(self):  # D103
        """Increment vals by 1."""
        self.val += 1
        self.val2 += 1

    def double_val(self):  # noqa: D102
        return self.val * 2

    def write_final_values(self):  # D103
        """Write the final value to the appropriate table."""
        row = {"agent_id": self.unique_id, "final_value": self.val}
        self.model.datacollector.add_table_row("Final_Values", row)


class MockAgentA(MockAgent):
    """Agent subclass A for testing agent-type-specific reporters."""

    def __init__(self, model, val=0):  # noqa: D107
        super().__init__(model, val)
        self.type_a_val = val * 2

    def step(self):  # noqa: D102
        super().step()
        self.type_a_val = self.val * 2


class MockAgentB(MockAgent):
    """Agent subclass B for testing agent-type-specific reporters."""

    def __init__(self, model, val=0):  # noqa: D107
        super().__init__(model, val)
        self.type_b_val = val * 3

    def step(self):  # noqa: D102
        super().step()
        self.type_b_val = self.val * 3


def agent_function_with_params(agent, multiplier, offset):  # noqa: D103
    return (agent.val * multiplier) + offset


class MockModel(Model):
    """Minimalistic model for testing purposes."""

    schedule = BaseScheduler(None)

    def __init__(self):  # noqa: D107
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.model_val = 100

        self.n = 10
        for i in range(1, self.n + 1):
            self.schedule.add(MockAgent(self, val=i))
        self.initialize_data_collector(
            model_reporters={
                "total_agents": lambda m: m.schedule.get_agent_count(),
                "model_value": "model_val",
                "model_calc": self.schedule.get_agent_count,
                "model_calc_comp": [self.test_model_calc_comp, [3, 4]],
                "model_calc_fail": [self.test_model_calc_comp, [12, 0]],
            },
            agent_reporters={
                "value": lambda a: a.val,
                "value2": "val2",
                "double_value": MockAgent.double_val,
                "value_with_params": [agent_function_with_params, [2, 3]],
            },
            tables={"Final_Values": ["agent_id", "final_value"]},
        )

    def test_model_calc_comp(self, input1, input2):  # noqa: D102
        if input2 > 0:
            return (self.model_val * input1) / input2
        else:
            assert ValueError
            return None

    def step(self):  # noqa: D102
        self.schedule.step()
        self.datacollector.collect(self)


class MockModelWithAgentTypes(Model):
    """Model for testing agent-type-specific reporters."""

    def __init__(self):  # noqa: D107
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.model_val = 100

        for i in range(10):
            if i % 2 == 0:
                self.schedule.add(MockAgentA(self, val=i))
            else:
                self.schedule.add(MockAgentB(self, val=i))

        self.datacollector = DataCollector(
            model_reporters={
                "total_agents": lambda m: m.schedule.get_agent_count(),
            },
            agent_reporters={
                "value": lambda a: a.val,
            },
            agenttype_reporters={
                MockAgentA: {"type_a_val": lambda a: a.type_a_val},
                MockAgentB: {"type_b_val": lambda a: a.type_b_val},
            },
        )

    def step(self):  # noqa: D102
        self.schedule.step()
        self.datacollector.collect(self)


class TestDataCollector(unittest.TestCase):
    """Tests for DataCollector."""

    def setUp(self):
        """Create the model and run it a set number of steps."""
        self.model = MockModel()
        for i in range(7):
            if i == 4:
                self.model.schedule.remove(self.model.schedule._agents[3])
            self.model.step()

        # Write to table:
        for agent in self.model.schedule.agents:
            agent.write_final_values()

    def step_assertion(self, model_var):  # noqa: D102
        for element in model_var:
            if model_var.index(element) < 4:
                assert element == 10
            else:
                assert element == 9

    def test_model_vars(self):
        """Test model-level variable collection."""
        data_collector = self.model.datacollector
        assert "total_agents" in data_collector.model_vars
        assert "model_value" in data_collector.model_vars
        assert "model_calc" in data_collector.model_vars
        assert "model_calc_comp" in data_collector.model_vars
        assert "model_calc_fail" in data_collector.model_vars
        length = 8
        assert len(data_collector.model_vars["total_agents"]) == length
        assert len(data_collector.model_vars["model_value"]) == length
        assert len(data_collector.model_vars["model_calc"]) == length
        assert len(data_collector.model_vars["model_calc_comp"]) == length
        self.step_assertion(data_collector.model_vars["total_agents"])
        for element in data_collector.model_vars["model_value"]:
            assert element == 100
        self.step_assertion(data_collector.model_vars["model_calc"])
        for element in data_collector.model_vars["model_calc_comp"]:
            assert element == 75
        for element in data_collector.model_vars["model_calc_fail"]:
            assert element is None

    def test_agent_records(self):
        """Test agent-level variable collection."""
        data_collector = self.model.datacollector
        agent_table = data_collector.get_agent_vars_dataframe()

        assert "double_value" in list(agent_table.columns)
        assert "value_with_params" in list(agent_table.columns)

        # Check the double_value column
        for (step, agent_id), value in agent_table["double_value"].items():
            expected_value = (step + agent_id) * 2
            self.assertEqual(value, expected_value)

        # Check the value_with_params column
        for (step, agent_id), value in agent_table["value_with_params"].items():
            expected_value = ((step + agent_id) * 2) + 3
            self.assertEqual(value, expected_value)

        assert len(data_collector._agent_records) == 8
        for step, records in data_collector._agent_records.items():
            if step < 5:
                assert len(records) == 10
            else:
                assert len(records) == 9

            for values in records:
                assert len(values) == 6

        assert "value" in list(agent_table.columns)
        assert "value2" in list(agent_table.columns)
        assert "value3" not in list(agent_table.columns)

        with self.assertRaises(KeyError):
            data_collector._agent_records[8]

    def test_table_rows(self):
        """Test table collection."""
        data_collector = self.model.datacollector
        assert len(data_collector.tables["Final_Values"]) == 2
        assert "agent_id" in data_collector.tables["Final_Values"]
        assert "final_value" in data_collector.tables["Final_Values"]
        for _key, data in data_collector.tables["Final_Values"].items():
            assert len(data) == 9

        with self.assertRaises(Exception):
            data_collector.add_table_row("error_table", {})

        with self.assertRaises(Exception):
            data_collector.add_table_row("Final_Values", {"final_value": 10})

    def test_exports(self):
        """Test DataFrame exports."""
        data_collector = self.model.datacollector
        model_vars = data_collector.get_model_vars_dataframe()
        agent_vars = data_collector.get_agent_vars_dataframe()
        table_df = data_collector.get_table_dataframe("Final_Values")
        assert model_vars.shape == (8, 5)
        assert agent_vars.shape == (77, 4)
        assert table_df.shape == (9, 2)

        with self.assertRaises(Exception):
            table_df = data_collector.get_table_dataframe("not a real table")


class TestDataCollectorInitialization(unittest.TestCase):
    """Tests for DataCollector initialization."""

    def setUp(self):  # noqa: D102
        self.model = Model()

    def test_initialize_before_scheduler(self):  # noqa: D102
        with self.assertRaises(RuntimeError) as cm:
            self.model.initialize_data_collector()
        self.assertEqual(
            str(cm.exception),
            "You must initialize the scheduler (self.schedule) before initializing the data collector.",
        )

    def test_initialize_before_agents_added_to_scheduler(self):  # noqa: D102
        with self.assertRaises(RuntimeError) as cm:
            self.model.schedule = BaseScheduler(self)
            self.model.initialize_data_collector()
        self.assertEqual(
            str(cm.exception),
            "You must add agents to the scheduler before initializing the data collector.",
        )


class TestDataCollectorWithAgentTypes(unittest.TestCase):
    """Tests for DataCollector with agent-type-specific reporters."""

    def setUp(self):
        """Create the model and run it a set number of steps."""
        self.model = MockModelWithAgentTypes()
        for _ in range(5):
            self.model.step()

    def test_agenttype_vars(self):
        """Test agent-type-specific variable collection."""
        data_collector = self.model.datacollector

        # Test MockAgentA data
        agent_a_data = data_collector.get_agenttype_vars_dataframe(MockAgentA)
        self.assertIn("type_a_val", agent_a_data.columns)
        self.assertEqual(len(agent_a_data), 25)  # 5 agents * 5 steps
        for (step, agent_id), value in agent_a_data["type_a_val"].items():
            expected_value = (agent_id - 1) * 2 + step * 2
            self.assertEqual(value, expected_value)

        # Test MockAgentB data
        agent_b_data = data_collector.get_agenttype_vars_dataframe(MockAgentB)
        self.assertIn("type_b_val", agent_b_data.columns)
        self.assertEqual(len(agent_b_data), 25)  # 5 agents * 5 steps
        for (step, agent_id), value in agent_b_data["type_b_val"].items():
            expected_value = (agent_id - 1) * 3 + step * 3
            self.assertEqual(value, expected_value)

    def test_agenttype_and_agent_vars(self):
        """Test that agent-type-specific and general agent variables are collected correctly."""
        data_collector = self.model.datacollector

        agent_vars = data_collector.get_agent_vars_dataframe()
        agent_a_vars = data_collector.get_agenttype_vars_dataframe(MockAgentA)
        agent_b_vars = data_collector.get_agenttype_vars_dataframe(MockAgentB)

        # Check that general agent variables are present for all agents
        self.assertIn("value", agent_vars.columns)

        # Check that agent-type-specific variables are only present in their respective dataframes
        self.assertIn("type_a_val", agent_a_vars.columns)
        self.assertNotIn("type_a_val", agent_b_vars.columns)
        self.assertIn("type_b_val", agent_b_vars.columns)
        self.assertNotIn("type_b_val", agent_a_vars.columns)

    def test_nonexistent_agenttype(self):
        """Test that requesting data for a non-existent agent type raises a warning."""
        data_collector = self.model.datacollector

        class NonExistentAgent(Agent):
            pass

        with self.assertWarns(UserWarning):
            non_existent_data = data_collector.get_agenttype_vars_dataframe(
                NonExistentAgent
            )
            self.assertTrue(non_existent_data.empty)

    def test_agenttype_reporter_string_attribute(self):
        """Test agent-type-specific reporter with string attribute."""
        model = MockModel()
        model.datacollector._new_agenttype_reporter(MockAgentA, "string_attr", "val")
        model.step()

        agent_a_data = model.datacollector.get_agenttype_vars_dataframe(MockAgentA)
        self.assertIn("string_attr", agent_a_data.columns)
        for (step, agent_id), value in agent_a_data["string_attr"].items():
            expected_value = agent_id + 1  # Initial value + 1 step
            self.assertEqual(value, expected_value)

    def test_agenttype_reporter_function_with_params(self):
        """Test agent-type-specific reporter with function and parameters."""

        def test_func(agent, multiplier):
            return agent.val * multiplier

        model = MockModel()
        model.datacollector._new_agenttype_reporter(
            MockAgentB, "func_param", [test_func, [2]]
        )
        model.step()

        agent_b_data = model.datacollector.get_agenttype_vars_dataframe(MockAgentB)
        self.assertIn("func_param", agent_b_data.columns)
        for (step, agent_id), value in agent_b_data["func_param"].items():
            expected_value = (agent_id + 1) * 2  # (Initial value + 1 step) * 2
            self.assertEqual(value, expected_value)

    def test_agenttype_reporter_multiple_types(self):
        """Test adding reporters for multiple agent types."""
        model = MockModel()
        model.datacollector._new_agenttype_reporter(
            MockAgentA, "type_a_val", lambda a: a.type_a_val
        )
        model.datacollector._new_agenttype_reporter(
            MockAgentB, "type_b_val", lambda a: a.type_b_val
        )
        model.step()

        agent_a_data = model.datacollector.get_agenttype_vars_dataframe(MockAgentA)
        agent_b_data = model.datacollector.get_agenttype_vars_dataframe(MockAgentB)

        self.assertIn("type_a_val", agent_a_data.columns)
        self.assertIn("type_b_val", agent_b_data.columns)
        self.assertNotIn("type_b_val", agent_a_data.columns)
        self.assertNotIn("type_a_val", agent_b_data.columns)


if __name__ == "__main__":
    unittest.main()
