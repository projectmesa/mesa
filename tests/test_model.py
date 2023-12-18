import pytest

from mesa.agent import Agent
from mesa.model import Model


def test_model_set_up():
    model = Model()
    assert model.running is True
    assert model.schedule is None
    assert model.current_id == 0
    assert model.current_id + 1 == model.next_id()
    assert model.current_id == 1
    model.step()


def test_running():
    class TestModel(Model):
        steps = 0

        def step(self):
            """Increase steps until 10."""
            self.steps += 1
            if self.steps == 10:
                self.running = False

    model = TestModel()
    model.run_model()


def test_seed(seed=23):
    model = Model(seed=seed)
    assert model._seed == seed
    model2 = Model(seed=seed + 1)
    assert model2._seed == seed + 1
    assert model._seed == seed


def test_reset_randomizer(newseed=42):
    model = Model()
    oldseed = model._seed
    model.reset_randomizer()
    assert model._seed == oldseed
    model.reset_randomizer(seed=newseed)
    assert model._seed == newseed


def test_agent_types():
    class TestAgent(Agent):
        pass

    model = Model()
    test_agent = TestAgent(model.next_id(), model)
    assert test_agent in model.agents[type(test_agent)]
    assert type(test_agent) in model.agent_types


class TestSelectAgents:
    class MockAgent(Agent):
        def __init__(self, unique_id, model, type_id, age, wealth):
            super().__init__(unique_id, model)
            self.type_id = type_id
            self.age = age
            self.wealth = wealth

    @pytest.fixture
    def model_with_agents(self):
        model = Model()
        for i in range(20):
            self.MockAgent(i, model, type_id=i % 2, age=i + 20, wealth=100 - i * 2)
        return model

    def test_basic_selection(self, model_with_agents):
        selected_agents = model_with_agents.select_agents()
        assert len(selected_agents) == 20

    def test_selection_with_n(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(n=5)
        assert len(selected_agents) == 5

    def test_sorting_and_direction(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            n=3, sort=["wealth"], direction=["highest"]
        )
        assert [agent.wealth for agent in selected_agents] == [100, 98, 96]

    def test_functional_filtering(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            filter_func=lambda agent: agent.age > 30
        )
        assert all(agent.age > 30 for agent in selected_agents)

    def test_type_filtering(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(agent_type=self.MockAgent)
        assert all(isinstance(agent, self.MockAgent) for agent in selected_agents)

    def test_up_to_flag(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(n=50, up_to=True)
        assert len(selected_agents) == 20

    def test_edge_case_empty_model(self):
        empty_model = Model()
        selected_agents = empty_model.select_agents()
        assert len(selected_agents) == 0

    def test_error_handling_invalid_sort(self, model_with_agents):
        with pytest.raises(AttributeError):
            model_with_agents.select_agents(
                n=3, sort=["nonexistent_attribute"], direction=["highest"]
            )

    def test_sorting_with_multiple_criteria(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            n=3, sort=["type_id", "age"], direction=["lowest", "highest"]
        )
        assert [(agent.type_id, agent.age) for agent in selected_agents] == [
            (0, 38),
            (0, 36),
            (0, 34),
        ]

    def test_direction_with_multiple_criteria(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            n=3, sort=["type_id", "wealth"], direction=["highest", "lowest"]
        )
        assert [(agent.type_id, agent.wealth) for agent in selected_agents] == [
            (1, 62),
            (1, 66),
            (1, 70),
        ]

    def test_type_filtering_with_multiple_types(self, model_with_agents):
        class AnotherMockAgent(Agent):
            pass

        # Adding different type agents to the model
        for i in range(20, 25):
            AnotherMockAgent(i, model_with_agents)

        selected_agents = model_with_agents.select_agents(
            agent_type=[self.MockAgent, AnotherMockAgent]
        )
        assert len(selected_agents) == 25

    def test_selection_when_n_exceeds_agent_count(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(n=50)
        assert len(selected_agents) == 20

    def test_inverse_functional_filtering(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            filter_func=lambda agent: agent.age < 25
        )
        assert all(agent.age < 25 for agent in selected_agents)

    def test_complex_lambda_in_filter(self, model_with_agents):
        selected_agents = model_with_agents.select_agents(
            filter_func=lambda agent: agent.age > 25 and agent.wealth > 70
        )
        assert all(agent.age > 25 and agent.wealth > 70 for agent in selected_agents)
