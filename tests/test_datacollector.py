'''
Test the DataCollector
'''
import unittest

from mesa import Model, Agent
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector


class MockAgent(Agent):
    '''
    Minimalistic agent for testing purposes.
    '''
    def __init__(self, unique_id, model, val=0):
        super().__init__(unique_id, model)
        self.val = val
        self.val2 = val

    def step(self):
        '''
        Increment vals by 1.
        '''
        self.val += 1
        self.val2 += 1

    def write_final_values(self):
        '''
        Write the final value to the appropriate table.
        '''
        row = {"agent_id": self.unique_id, "final_value": self.val}
        self.model.datacollector.add_table_row("Final_Values", row)


class MockModel(Model):
    '''
    Minimalistic model for testing purposes.
    '''

    schedule = BaseScheduler(None)

    def __init__(self):
        self.schedule = BaseScheduler(self)
        self.model_val = 100

        for i in range(10):
            a = MockAgent(i, self, val=i)
            self.schedule.add(a)
        self.datacollector = DataCollector(
            {"total_agents": lambda m: m.schedule.get_agent_count(),
             "model_value": "model_val"},
            {"value": lambda a: a.val, "value2": "val2"},
            {"Final_Values": ["agent_id", "final_value"]})

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)


class TestDataCollector(unittest.TestCase):
    def setUp(self):
        '''
        Create the model and run it a set number of steps.
        '''
        self.model = MockModel()
        for i in range(7):
            self.model.step()
        # Write to table:
        for agent in self.model.schedule.agents:
            agent.write_final_values()

    def test_model_vars(self):
        '''
        Test model-level variable collection.
        '''
        data_collector = self.model.datacollector
        assert "total_agents" in data_collector.model_vars
        assert "model_value" in data_collector.model_vars
        assert len(data_collector.model_vars["total_agents"]) == 7
        assert len(data_collector.model_vars["model_value"]) == 7
        for element in data_collector.model_vars["total_agents"]:
            assert element == 10
        for element in data_collector.model_vars["model_value"]:
            assert element == 100

    def test_agent_records(self):
        '''
        Test agent-level variable collection.
        '''
        data_collector = self.model.datacollector
        assert len(data_collector._agent_records) == 7
        for step, records in data_collector._agent_records.items():
            assert len(records) == 10
            for values in records:
                assert len(values) == 4

    def test_table_rows(self):
        '''
        Test table collection
        '''
        data_collector = self.model.datacollector
        assert len(data_collector.tables["Final_Values"]) == 2
        assert "agent_id" in data_collector.tables["Final_Values"]
        assert "final_value" in data_collector.tables["Final_Values"]
        for key, data in data_collector.tables["Final_Values"].items():
            assert len(data) == 10

        with self.assertRaises(Exception):
            data_collector.add_table_row("error_table", {})

        with self.assertRaises(Exception):
            data_collector.add_table_row("Final_Values", {"final_value": 10})

    def test_exports(self):
        '''
        Test DataFrame exports
        '''
        data_collector = self.model.datacollector
        model_vars = data_collector.get_model_vars_dataframe()
        agent_vars = data_collector.get_agent_vars_dataframe()
        table_df = data_collector.get_table_dataframe("Final_Values")

        assert model_vars.shape == (7, 2)
        assert agent_vars.shape == (70, 2)
        assert table_df.shape == (10, 2)

        with self.assertRaises(Exception):
            table_df = data_collector.get_table_dataframe("not a real table")


if __name__ == '__main__':
    unittest.main()
