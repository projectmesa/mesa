from mesa.agent import Agent
from mesa.batchrunner import _make_model_kwargs, batch_run
from mesa.datacollection import DataCollector
from mesa.model import Model
from mesa.time import BaseScheduler


def test_make_model_kwargs():
    assert _make_model_kwargs({"a": 3, "b": 5}) == [{"a": 3, "b": 5}]
    assert _make_model_kwargs({"a": 3, "b": range(3)}) == [
        {"a": 3, "b": 0},
        {"a": 3, "b": 1},
        {"a": 3, "b": 2},
    ]
    assert _make_model_kwargs({"a": range(2), "b": range(2)}) == [
        {"a": 0, "b": 0},
        {"a": 0, "b": 1},
        {"a": 1, "b": 0},
        {"a": 1, "b": 1},
    ]
    # If the value is a single string, do not iterate over it.
    assert _make_model_kwargs({"a": "value"}) == [{"a": "value"}]


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
        variable_model_param=None,
        variable_agent_param=None,
        fixed_model_param=None,
        schedule=None,
        enable_agent_reporters=True,
        n_agents=3,
        **kwargs
    ):
        super().__init__()
        self.schedule = BaseScheduler(self) if schedule is None else schedule
        self.variable_model_param = variable_model_param
        self.variable_agent_param = variable_agent_param
        self.fixed_model_param = fixed_model_param
        self.n_agents = n_agents
        if enable_agent_reporters:
            agent_reporters = {"agent_id": "unique_id", "agent_local": "local"}
        else:
            agent_reporters = None
        self.datacollector = DataCollector(
            model_reporters={"reported_model_param": self.get_local_model_param},
            agent_reporters=agent_reporters,
        )
        self.running = True
        self.init_agents()

    def init_agents(self):
        if self.variable_agent_param is None:
            agent_val = 1
        else:
            agent_val = self.variable_agent_param
        for i in range(self.n_agents):
            self.schedule.add(MockAgent(i, self, agent_val))

    def get_local_model_param(self):
        return 42

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


def test_batch_run():
    result = batch_run(MockModel, {}, number_processes=2)
    assert result == [
        {
            "RunId": 0,
            "iteration": 0,
            "Step": 1000,
            "reported_model_param": 42,
            "AgentID": 0,
            "agent_id": 0,
            "agent_local": 250.0,
        },
        {
            "RunId": 0,
            "iteration": 0,
            "Step": 1000,
            "reported_model_param": 42,
            "AgentID": 1,
            "agent_id": 1,
            "agent_local": 250.0,
        },
        {
            "RunId": 0,
            "iteration": 0,
            "Step": 1000,
            "reported_model_param": 42,
            "AgentID": 2,
            "agent_id": 2,
            "agent_local": 250.0,
        },
    ]


def test_batch_run_with_params():
    batch_run(
        MockModel,
        {
            "variable_model_params": range(5),
            "variable_agent_params": ["H", "E", "L", "L", "O"],
        },
        number_processes=2,
    )


def test_batch_run_no_agent_reporters():
    result = batch_run(MockModel, {"enable_agent_reporters": False}, number_processes=2)
    print(result)
    assert result == [
        {
            "RunId": 0,
            "iteration": 0,
            "Step": 1000,
            "enable_agent_reporters": False,
            "reported_model_param": 42,
        }
    ]


def test_batch_run_single_core():
    batch_run(MockModel, {}, number_processes=1, iterations=10)


def test_batch_run_unhashable_param():
    result = batch_run(
        MockModel,
        {
            "n_agents": 2,
            "variable_model_params": [{"key": "value"}],
        },
        iterations=2,
    )
    template = {
        "Step": 1000,
        "reported_model_param": 42,
        "agent_local": 250.0,
        "n_agents": 2,
        "variable_model_params": {"key": "value"},
    }

    assert result == [
        {
            "RunId": 0,
            "iteration": 0,
            "AgentID": 0,
            "agent_id": 0,
            **template,
        },
        {
            "RunId": 0,
            "iteration": 0,
            "AgentID": 1,
            "agent_id": 1,
            **template,
        },
        {
            "RunId": 1,
            "iteration": 1,
            "AgentID": 0,
            "agent_id": 0,
            **template,
        },
        {
            "RunId": 1,
            "iteration": 1,
            "AgentID": 1,
            "agent_id": 1,
            **template,
        },
    ]
