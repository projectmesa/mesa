import pickle

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
    assert len(agentset.select(test_function, n=2)) == 2
    assert len(agentset.select(test_function, inplace=True)) == 5
    assert agentset.select(inplace=True) == agentset
    assert all(a1 == a2 for a1, a2 in zip(agentset.select(), agentset))
    assert all(a1 == a2 for a1, a2 in zip(agentset.select(n=5), agentset[:5]))

    assert len(agentset.shuffle().select(n=5)) == 5

    def test_function(agent):
        return agent.unique_id

    assert all(
        a1 == a2
        for a1, a2 in zip(agentset.sort(test_function, ascending=False), agentset[::-1])
    )
    assert all(
        a1 == a2
        for a1, a2 in zip(agentset.sort("unique_id", ascending=False), agentset[::-1])
    )

    assert all(
        a1 == a2.unique_id for a1, a2 in zip(agentset.get("unique_id"), agentset)
    )
    assert all(
        a1 == a2.unique_id
        for a1, a2 in zip(
            agentset.do("get_unique_identifier", return_results=True), agentset
        )
    )
    assert agentset == agentset.do("get_unique_identifier")

    agentset.discard(agents[0])
    assert agents[0] not in agentset
    agentset.discard(agents[0])  # check if no error is raised on discard

    with pytest.raises(KeyError):
        agentset.remove(agents[0])

    agentset.add(agents[0])
    assert agents[0] in agentset

    # because AgentSet uses weakrefs, we need hard refs as well....
    other_agents, another_set = pickle.loads(  # noqa: S301
        pickle.dumps([agents, AgentSet(agents, model)])
    )
    assert all(
        a1.unique_id == a2.unique_id for a1, a2 in zip(another_set, other_agents)
    )
    assert len(another_set) == len(other_agents)


def test_agentset_initialization():
    model = Model()
    empty_agentset = AgentSet([], model)
    assert len(empty_agentset) == 0

    agents = [TestAgent(model.next_id(), model) for _ in range(10)]
    agentset = AgentSet(agents, model)
    assert len(agentset) == 10


def test_agentset_serialization():
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(5)]
    agentset = AgentSet(agents, model)

    serialized = pickle.dumps(agentset)
    deserialized = pickle.loads(serialized)  # noqa: S301

    original_ids = [agent.unique_id for agent in agents]
    deserialized_ids = [agent.unique_id for agent in deserialized]

    assert deserialized_ids == original_ids


def test_agent_membership():
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(5)]
    agentset = AgentSet(agents, model)

    assert agents[0] in agentset
    assert TestAgent(model.next_id(), model) not in agentset


def test_agent_add_remove_discard():
    model = Model()
    agent = TestAgent(model.next_id(), model)
    agentset = AgentSet([], model)

    agentset.add(agent)
    assert agent in agentset

    agentset.remove(agent)
    assert agent not in agentset

    agentset.add(agent)
    agentset.discard(agent)
    assert agent not in agentset

    with pytest.raises(KeyError):
        agentset.remove(agent)


def test_agentset_get_item():
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    assert agentset[0] == agents[0]
    assert agentset[-1] == agents[-1]
    assert agentset[1:3] == agents[1:3]

    with pytest.raises(IndexError):
        _ = agentset[20]


def test_agentset_do_method():
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    with pytest.raises(AttributeError):
        agentset.do("non_existing_method")


def test_agentset_get_attribute():
    model = Model()
    agents = [TestAgent(model.next_id(), model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    unique_ids = agentset.get("unique_id")
    assert unique_ids == [agent.unique_id for agent in agents]

    with pytest.raises(AttributeError):
        agentset.get("non_existing_attribute")


class OtherAgentType(Agent):
    def get_unique_identifier(self):
        return self.unique_id


def test_agentset_select_by_type():
    model = Model()
    # Create a mix of agents of two different types
    test_agents = [TestAgent(model.next_id(), model) for _ in range(4)]
    other_agents = [OtherAgentType(model.next_id(), model) for _ in range(6)]

    # Combine the two types of agents
    mixed_agents = test_agents + other_agents
    agentset = AgentSet(mixed_agents, model)

    # Test selection by type
    selected_test_agents = agentset.select(agent_type=TestAgent)
    assert len(selected_test_agents) == len(test_agents)
    assert all(isinstance(agent, TestAgent) for agent in selected_test_agents)
    assert len(selected_test_agents) == 4

    selected_other_agents = agentset.select(agent_type=OtherAgentType)
    assert len(selected_other_agents) == len(other_agents)
    assert all(isinstance(agent, OtherAgentType) for agent in selected_other_agents)
    assert len(selected_other_agents) == 6

    # Test with no type specified (should select all agents)
    all_agents = agentset.select()
    assert len(all_agents) == len(mixed_agents)
