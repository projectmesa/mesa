from mesa.agent import Agent, AgentSet
from mesa.model import Model


def test_model_set_up():
    model = Model()
    assert model.running is True
    assert model.schedule is None
    assert model.steps == 0
    model.step()
    assert model.steps == 1


def test_running():
    class TestModel(Model):
        steps = 0

        def step(self):
            """Increase steps until 10."""
            if self.steps == 10:
                self.running = False

    model = TestModel()
    model.run_model()
    assert model.steps == 10


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
    test_agent = TestAgent( model)
    assert test_agent in model.agents
    assert type(test_agent) in model.agent_types


def test_agents_by_type():
    class Wolf(Agent):
        pass

    class Sheep(Agent):
        pass

    model = Model()
    wolf = Wolf(1, model)
    sheep = Sheep(2, model)

    assert model.agents_by_type[Wolf] == AgentSet([wolf], model)
    assert model.agents_by_type[Sheep] == AgentSet([sheep], model)
    assert len(model.agents_by_type) == 2
