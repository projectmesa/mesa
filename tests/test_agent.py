import pickle

import numpy as np
import pytest

from mesa.agent import Agent, AgentSet
from mesa.model import Model


class TestAgent(Agent):
    def get_unique_identifier(self):
        return self.unique_id


class TestAgentDo(Agent):
    def __init__(
        self,
        model,
    ):
        super().__init__(model)
        self.agent_set = None

    def get_unique_identifier(self):
        return self.unique_id

    def do_add(self):
        agent = TestAgentDo(self.model)
        self.agent_set.add(agent)

    def do_remove(self):
        self.agent_set.remove(self)


def test_agent_removal():
    model = Model()
    agent = TestAgent(model)
    # Check if the agent is added
    assert agent in model.agents

    agent.remove()
    # Check if the agent is removed
    assert agent not in model.agents


def test_agentset():
    # create agentset
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]

    agentset = AgentSet(agents, model)

    assert agents[0] in agentset
    assert len(agentset) == len(agents)
    assert all(a1 == a2 for a1, a2 in zip(agentset[0:5], agents[0:5]))

    for a1, a2 in zip(agentset, agents):
        assert a1 == a2

    def test_function(agent):
        return agent.unique_id > 5

    assert len(agentset.select(at_most=0.2)) == 2  # Select 20% of agents
    assert len(agentset.select(at_most=0.549)) == 5  # Select 50% of agents
    assert len(agentset.select(at_most=0.09)) == 0  # Select 0% of agents
    assert len(agentset.select(at_most=1.0)) == 10  # Select 100% agents
    assert len(agentset.select(at_most=1)) == 1  # Select 1 agent

    assert len(agentset.select(test_function)) == 5
    assert len(agentset.select(test_function, n=2)) == 2
    assert len(agentset.select(test_function, inplace=True)) == 5
    assert agentset.select(inplace=True) == agentset
    assert all(a1 == a2 for a1, a2 in zip(agentset.select(), agentset))
    assert all(a1 == a2 for a1, a2 in zip(agentset.select(n=5), agentset[:5]))

    assert len(agentset.shuffle(inplace=False).select(n=5)) == 5

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

    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)
    assert len(agentset) == 10


def test_agentset_serialization():
    model = Model()
    agents = [TestAgent(model) for _ in range(5)]
    agentset = AgentSet(agents, model)

    serialized = pickle.dumps(agentset)
    deserialized = pickle.loads(serialized)  # noqa: S301

    original_ids = [agent.unique_id for agent in agents]
    deserialized_ids = [agent.unique_id for agent in deserialized]

    assert deserialized_ids == original_ids


def test_agent_membership():
    model = Model()
    agents = [TestAgent(model) for _ in range(5)]
    agentset = AgentSet(agents, model)

    assert agents[0] in agentset
    assert TestAgent(model) not in agentset


def test_agent_add_remove_discard():
    model = Model()
    agent = TestAgent(model)
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
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    assert agentset[0] == agents[0]
    assert agentset[-1] == agents[-1]
    assert agentset[1:3] == agents[1:3]

    with pytest.raises(IndexError):
        _ = agentset[20]


def test_agentset_do_str():
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    with pytest.raises(AttributeError):
        agentset.do("non_existing_method")

    # tests for addition and removal in do
    # do iterates, so no error should be raised to change size while iterating
    # related to issue #1595

    # setup
    n = 10
    model = Model()
    agents = [TestAgentDo(model) for _ in range(n)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    agentset.do("do_add")
    assert len(agentset) == 2 * n

    # setup
    model = Model()
    agents = [TestAgentDo(model) for _ in range(10)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    agentset.do("do_remove")
    assert len(agentset) == 0


def test_agentset_do_callable():
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    # Test callable with non-existent function
    with pytest.raises(AttributeError):
        agentset.do(lambda agent: agent.non_existing_method())

    # tests for addition and removal in do using callables
    # do iterates, so no error should be raised to change size while iterating
    # related to issue #1595

    # setup for lambda function tests
    n = 10
    model = Model()
    agents = [TestAgentDo(model) for _ in range(n)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    # Lambda for addition
    agentset.do(lambda agent: agent.do_add())
    assert len(agentset) == 2 * n

    # setup again for lambda function tests
    model = Model()
    agents = [TestAgentDo(model) for _ in range(10)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    # Lambda for removal
    agentset.do(lambda agent: agent.do_remove())
    assert len(agentset) == 0

    # setup for actual function tests
    def add_function(agent):
        agent.do_add()

    def remove_function(agent):
        agent.do_remove()

    # setup again for actual function tests
    model = Model()
    agents = [TestAgentDo(model) for _ in range(n)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    # Actual function for addition
    agentset.do(add_function)
    assert len(agentset) == 2 * n

    # setup again for actual function tests
    model = Model()
    agents = [TestAgentDo(model) for _ in range(10)]
    agentset = AgentSet(agents, model)
    for agent in agents:
        agent.agent_set = agentset

    # Actual function for removal
    agentset.do(remove_function)
    assert len(agentset) == 0


def test_agentset_get():
    model = Model()
    _ = [TestAgent(i, model) for i in range(10)]

    agentset = model.agents

    agentset.set("a", 5)
    agentset.set("b", 6)

    # Case 1: Normal retrieval of existing attributes
    values = agentset.get(["a", "b"])
    assert all((a == 5) & (b == 6) for a, b in values)

    # Case 2: Raise AttributeError when attribute doesn't exist
    with pytest.raises(AttributeError):
        agentset.get("unknown_attribute")

    # Case 3: Use default value when attribute is missing
    results = agentset.get(
        "unknown_attribute", handle_missing="default", default_value=True
    )
    assert all(results) is True

    # Case 4: Retrieve mixed attributes with default value for missing ones
    values = agentset.get(
        ["a", "unknown_attribute"], handle_missing="default", default_value=True
    )
    assert all((a == 5) & (unknown is True) for a, unknown in values)

    # Case 5: Skip agents missing the attribute
    results = agentset.get("unknown_attribute", handle_missing="skip")
    assert len(results) == 0

    # Case 6: Skip missing attributes in mixed attribute retrieval
    values = agentset.get(["a", "unknown_attribute"], handle_missing="skip")
    assert all((a == 5) for (a,) in values)

    # Case 7: Invalid handle_missing value raises ValueError
    with pytest.raises(ValueError):
        agentset.get("unknown_attribute", handle_missing="some nonsense value")

    # Case 8: Retrieve multiple attributes with mixed existence and 'default' handling
    values = agentset.get(
        ["a", "b", "unknown_attribute"], handle_missing="default", default_value=0
    )
    assert all((a == 5) & (b == 6) & (unknown == 0) for a, b, unknown in values)

    # Case 9: Retrieve multiple attributes with 'skip' handling for missing attributes
    values = agentset.get(["a", "b", "unknown_attribute"], handle_missing="skip")
    assert all((a == 5) & (b == 6) for a, b in values)  # No unknown_attribute included

    # Case 10: 'default' handling when one attribute is completely missing from some agents
    agentset.select(at_most=0.5).set("c", 8)  # Only some agents have attribute 'c'
    values = agentset.get(["a", "c"], handle_missing="default", default_value=-1)
    assert all((a == 5) & (c in [8, -1]) for a, c in values)

    # Case 11: Skip handling when one attribute is completely missing from some agents
    values = agentset.get(["a", "c"], handle_missing="skip")
    assert all(5 in a for a in values)  # Only agents with 'a' are returned


def test_agentset_agg():
    model = Model()
    agents = [TestAgent(model) for i in range(10)]

    # Assign some values to attributes
    for i, agent in enumerate(agents):
        agent.energy = i + 1
        agent.wealth = 10 * (i + 1)

    agentset = AgentSet(agents, model)

    # Test min aggregation
    min_energy = agentset.agg("energy", min)
    assert min_energy == 1

    # Test max aggregation
    max_energy = agentset.agg("energy", max)
    assert max_energy == 10

    # Test sum aggregation
    total_energy = agentset.agg("energy", sum)
    assert total_energy == sum(range(1, 11))

    # Test mean aggregation using numpy
    avg_wealth = agentset.agg("wealth", np.mean)
    assert avg_wealth == 55.0

    # Test aggregation with a custom function
    def custom_func(values):
        return sum(values) / len(values)

    custom_avg_energy = agentset.agg("energy", custom_func)
    assert custom_avg_energy == 5.5


def test_agentset_set_method():
    # Initialize the model and agents with and without existing attributes
    class TestAgentWithAttribute(Agent):
        def __init__(self, model, age=None):
            super().__init__(model)
            self.age = age

    model = Model()
    agents = [TestAgentWithAttribute(model, age=i) for i in range(5)]
    agentset = AgentSet(agents, model)

    # Set a new attribute "health" and an existing attribute "age" for all agents
    agentset.set("health", 100).set("age", 50).set("status", "active")

    # Check if all agents have the "health", "age", and "status" attributes correctly set
    for agent in agentset:
        assert hasattr(agent, "health")
        assert agent.health == 100
        assert hasattr(agent, "age")
        assert agent.age == 50
        assert hasattr(agent, "status")
        assert agent.status == "active"


def test_agentset_map_str():
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    with pytest.raises(AttributeError):
        agentset.do("non_existing_method")

    results = agentset.map("get_unique_identifier")
    assert all(i == entry for i, entry in zip(results, range(1, 11)))


def test_agentset_map_callable():
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    # Test callable with non-existent function
    with pytest.raises(AttributeError):
        agentset.map(lambda agent: agent.non_existing_method())

    # tests for addition and removal in do using callables
    # do iterates, so no error should be raised to change size while iterating
    # related to issue #1595

    results = agentset.map(lambda agent: agent.unique_id)
    assert all(i == entry for i, entry in zip(results, range(1, 11)))


def test_agentset_get_attribute():
    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    unique_ids = agentset.get("unique_id")
    assert unique_ids == [agent.unique_id for agent in agents]

    with pytest.raises(AttributeError):
        agentset.get("non_existing_attribute")

    model = Model()
    agents = []
    for i in range(10):
        agent = TestAgent(model)
        agent.i = i**2
        agents.append(agent)
    agentset = AgentSet(agents, model)

    values = agentset.get(["unique_id", "i"])

    for value, agent in zip(values, agents):
        (
            unique_id,
            i,
        ) = value
        assert agent.unique_id == unique_id
        assert agent.i == i


class OtherAgentType(Agent):
    def get_unique_identifier(self):
        return self.unique_id


def test_agentset_select_by_type():
    model = Model()
    # Create a mix of agents of two different types
    test_agents = [TestAgent(model) for _ in range(4)]
    other_agents = [OtherAgentType(model) for _ in range(6)]

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


def test_agentset_shuffle():
    model = Model()
    test_agents = [TestAgent(model) for _ in range(12)]

    agentset = AgentSet(test_agents, model=model)
    agentset = agentset.shuffle()
    assert not all(a1 == a2 for a1, a2 in zip(test_agents, agentset))

    agentset = AgentSet(test_agents, model=model)
    agentset.shuffle(inplace=True)
    assert not all(a1 == a2 for a1, a2 in zip(test_agents, agentset))


def test_agentset_groupby():
    class TestAgent(Agent):
        def __init__(self, model):
            super().__init__(model)
            self.even = self.unique_id % 2 == 0

        def get_unique_identifier(self):
            return self.unique_id

    model = Model()
    agents = [TestAgent(model) for _ in range(10)]
    agentset = AgentSet(agents, model)

    groups = agentset.groupby("even")
    assert len(groups.groups[True]) == 5
    assert len(groups.groups[False]) == 5

    groups = agentset.groupby(lambda a: a.unique_id % 2 == 0)
    assert len(groups.groups[True]) == 5
    assert len(groups.groups[False]) == 5
    assert len(groups) == 2

    for group_name, group in groups:
        assert len(group) == 5
        assert group_name in {True, False}

    sizes = agentset.groupby("even", result_type="list").map(len)
    assert sizes == {True: 5, False: 5}

    attributes = agentset.groupby("even", result_type="agentset").map("get", "even")
    for group_name, group in attributes.items():
        assert all(group_name == entry for entry in group)

    groups = agentset.groupby("even", result_type="agentset")
    another_ref_to_groups = groups.do("do", "step")
    assert groups == another_ref_to_groups

    groups = agentset.groupby("even", result_type="agentset")
    another_ref_to_groups = groups.do(lambda x: x.do("step"))
    assert groups == another_ref_to_groups


def test_oldstyle_agent_instantiation():
    """Old behavior of Agent creation with unique_id and model as positional arguments.
    Can be removed/updated in the future."""
    model = Model()
    agent = Agent("some weird unique id", model)
    assert isinstance(agent.unique_id, int)
    assert agent.model == model
    assert isinstance(agent.model, Model)
    assert agent.unique_id == 1  # test that we ignore unique ID that is passed
