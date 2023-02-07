"""
Test the DataCollector
"""
import unittest

from mesa import Agent, Model
from mesa.time import BaseScheduler


class MockAgent(Agent):
    """
    Minimalistic agent for testing purposes.
    """

    def __init__(self, unique_id, model, val=0):
        super().__init__(unique_id, model)
        self.val = val
        self.val2 = val

    def step(self):
        """
        Increment vals by 1.
        """
        self.val += 1
        self.val2 += 1

    def write_final_values(self):
        """
        Write the final value to the appropriate table.
        """
        row = {"agent_id": self.unique_id, "final_value": self.val}
        self.model.datacollector.add_table_row("Final_Values", row)


class MockModel(Model):
    """
    Minimalistic model for testing purposes.
    """

    schedule = BaseScheduler(None)

    def __init__(self):
        self.schedule = BaseScheduler(self)
        self.model_val = 100

        for i in range(10):
            a = MockAgent(i, self, val=i)
            self.schedule.add(a)
        self.initialize_data_collector(
            {
                "total_agents": lambda m: m.schedule.get_agent_count(),
                "model_value": "model_val",
                "model_calc": self.schedule.get_agent_count,
                "model_calc_comp": [self.test_model_calc_comp, [3, 4]],
                "model_calc_fail": [self.test_model_calc_comp, [12, 0]],
            },
            {"value": lambda a: a.val, "value2": "val2"},
            {"Final_Values": ["agent_id", "final_value"]},
        )

    def test_model_calc_comp(self, input1, input2):
        if input2 > 0:
            return (self.model_val * input1) / input2
        else:
            assert ValueError
            return None

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)


class TestDataCollector(unittest.TestCase):
    def setUp(self):
        """
        Create the model and run it a set number of steps.
        """
        self.model = MockModel()
        for i in range(7):
            if i == 4:
                self.model.schedule.remove(self.model.schedule._agents[3])
            self.model.step()

        # Write to table:
        for agent in self.model.schedule.agents:
            agent.write_final_values()

    def step_assertion(self, model_var):
        for element in model_var:
            if model_var.index(element) < 4:
                assert element == 10
            else:
                assert element == 9

    def test_model_vars(self):
        """
        Test model-level variable collection.
        """
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
        """
        Test agent-level variable collection.
        """
        data_collector = self.model.datacollector
        agent_table = data_collector.get_agent_vars_dataframe()

        assert len(data_collector._agent_records) == 8
        for step, records in data_collector._agent_records.items():
            if step < 5:
                assert len(records) == 10
            else:
                assert len(records) == 9

            for values in records:
                assert len(values) == 4

        assert "value" in list(agent_table.columns)
        assert "value2" in list(agent_table.columns)
        assert "value3" not in list(agent_table.columns)

        with self.assertRaises(KeyError):
            data_collector._agent_records[8]

    def test_table_rows(self):
        """
        Test table collection
        """
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
        """
        Test DataFrame exports
        """
        data_collector = self.model.datacollector
        model_vars = data_collector.get_model_vars_dataframe()
        agent_vars = data_collector.get_agent_vars_dataframe()
        table_df = data_collector.get_table_dataframe("Final_Values")
        assert model_vars.shape == (8, 5)
        assert agent_vars.shape == (77, 2)
        assert table_df.shape == (9, 2)

        with self.assertRaises(Exception):
            table_df = data_collector.get_table_dataframe("not a real table")


class TestDataCollectorInitialization(unittest.TestCase):
    def setUp(self):
        self.model = Model()

    def test_initialize_before_scheduler(self):
        with self.assertRaises(RuntimeError) as cm:
            self.model.initialize_data_collector()
        self.assertEqual(
            str(cm.exception),
            "You must initialize the scheduler (self.schedule) before initializing the data collector.",
        )

    def test_initialize_before_agents_added_to_scheduler(self):
        with self.assertRaises(RuntimeError) as cm:
            self.model.schedule = BaseScheduler(self)
            self.model.initialize_data_collector()
        self.assertEqual(
            str(cm.exception),
            "You must add agents to the scheduler before initializing the data collector.",
        )


if __name__ == "__main__":
    unittest.main()
