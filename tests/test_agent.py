from mesa.agent import Agent
from mesa.model import Model


def test_agent_removal():
    class TestAgent(Agent):
        pass

    model = Model()
    agent = TestAgent(model.next_id(), model)
    # Check if the agent is added
    assert agent in model.agents

    agent.remove()
    # Check if the agent is removed
    assert agent not in model.agents
