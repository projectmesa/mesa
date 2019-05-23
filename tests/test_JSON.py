from mesa import Agent, Model
from mesa.time import BaseScheduler
import unittest
import json


class MockAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.alive = True

    @property
    def is_alive(self):
        return self.alive


class MockModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule = BaseScheduler(self)
        for _ in range(10):
            agent = MockAgent(self.next_id(), self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()

    @property
    def is_running(self):
        return self.running


class TestAgentJSON(unittest.TestCase):
    def setUp(self):
        self.model = MockModel()
        self.agent = self.model.schedule.agents[0]

    def test_with_filter(self):
        agent_json = self.agent.as_json(filter=True)
        # test if json is deserializable
        agent_dict = json.loads(agent_json)

        assert "model" not in agent_dict
        assert "random" not in agent_dict

        assert agent_dict["alive"] is True
        assert agent_dict["unique_id"] == 1
        assert agent_dict["is_alive"] is True

    def test_without_filter(self):
        agent_json = self.agent.as_json(filter=False)
        # test if json is deserializable
        agent_dict = json.loads(agent_json)

        assert agent_dict["alive"] is True
        assert agent_dict["unique_id"] == 1
        assert agent_dict["is_alive"] is True
        assert "MockModel" in agent_dict["model"]
        assert "random" in agent_dict


class TestModelJSON(unittest.TestCase):
    def setUp(self):
        self.model = MockModel()
        self.agent = self.model.schedule.agents[0]

    def test_with_filter(self):
        model_json = self.model.as_json(filter=True)
        # test if json is deserializable
        model_dict = json.loads(model_json)

        assert "random" not in model_dict

        assert model_dict["running"] is True
        assert model_dict["current_id"] == 10
        assert model_dict["is_running"] is True
        assert isinstance(model_dict["agents"], list)

    def test_without_filter(self):
        model_json = self.model.as_json(filter=False)
        # test if json is deserializable
        model_dict = json.loads(model_json)

        assert model_dict["running"] is True
        assert model_dict["current_id"] == 10
        assert model_dict["is_running"] is True
        assert isinstance(model_dict["agents"], list)
        assert "random" in model_dict

    def test_without_agents(self):
        model_json = self.model.as_json(filter=True, include_agents=False)
        # test if json is deserializable
        model_dict = json.loads(model_json)

        assert "agents" not in model_dict
