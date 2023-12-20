import pytest

from mesa.agent import Agent, AgentSet
from mesa.model import Model


class TestAgent(Agent):

    def get_unique_identifier(self):
        return self.unique_id


def test_agent_removal():
    model = Model()
    agent = TestAgent(model.next_id(), model)
    # Check if the agent is added
    assert agent in model.agents

    agent.remove()
    # Check if the agent is removed
    assert agent not in model.agents


def test_agentset():
    # create agentset
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(10)]

    agentset = AgentSet(agents, model)

    assert agents[0] in agentset
    assert len(agentset) == len(agents)
    assert all(a1 == a2 for a1, a2 in zip(agentset[0:5], agents[0:5]))

    for a1, a2 in zip(agentset, agents):
        assert a1 == a2

    def test_function(agent):
        return agent.unique_id > 5

    assert len(agentset.select(test_function)) == 5
    assert len(agentset.select(test_function, inplace=True)) == 5
    assert agentset.select(inplace=True) == agentset
    assert all(a1 == a2 for a1, a2 in zip(agentset.select(), agentset))

    def test_function(agent):
        return agent.unique_id

    assert all(a1 == a2 for a1, a2 in zip(agentset.sort(test_function, reverse=True), agentset[::-1]))

    assert all(a1 == a2.unique_id for a1, a2 in zip(agentset.get_each("unique_id"), agentset))
    assert all(a1 == a2.unique_id for a1, a2 in zip(agentset.do_each("get_unique_identifier"), agentset))

    agentset.discard(agents[0])
    assert agents[0] not in agentset
    agentset.discard(agents[0])  # check if no error is raised on discard

    with pytest.raises(KeyError):
        agentset.remove(agents[0])

    agentset.add(agents[0])
    assert agents[0] in agentset
