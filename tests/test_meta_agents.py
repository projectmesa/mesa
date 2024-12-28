"""Tests for the meta_agents module."""

import pytest

from mesa import Agent, Model
from mesa.experimental.meta_agents.meta_agents import create_meta_agent


@pytest.fixture
def setup_agents():
    """Set up the model and agents for testing.

    Returns:
        tuple: A tuple containing the model and a list of agents.
    """
    model = Model()
    agent1 = Agent(model)
    agent2 = Agent(model)
    agent3 = Agent(model)
    agent4 = Agent(model)
    agent4.custom_attribute = "custom_value"
    agents = [agent1, agent2, agent3, agent4]
    return model, agents


def test_create_meta_agent_new_class(setup_agents):
    """Test creating a new meta-agent class and test inclusion of attributes and functions.

    Args:
        setup_agents (tuple): The model and agents fixture.
    """
    model, agents = setup_agents
    meta_agent = create_meta_agent(
        model,
        "MetaAgentClass",
        agents,
        meta_attributes={"attribute1": "value1"},
        meta_functions={"function1": lambda self: "function1"},
        retain_subagent_attributes=True,
    )
    assert meta_agent is not None
    assert meta_agent.attribute1 == "value1"
    assert meta_agent.function1() == "function1"
    assert meta_agent.agents == set(agents)
    assert hasattr(meta_agent, "custom_attribute")
    assert meta_agent.custom_attribute == "custom_value"


def test_create_meta_agent_existing_class(setup_agents):
    """Test creating new meta-agent instance with an existing meta-agent class.

    Args:
        setup_agents (tuple): The model and agents fixture.
    """
    model, agents = setup_agents

    # Create Met Agent Class
    meta_agent = create_meta_agent(
        model,
        "MetaAgentClass",
        [agents[0], agents[2]],
        meta_attributes={"attribute1": "value1"},
        meta_functions={"function1": lambda self: "function1"},
    )

    # Create new meta-agent instance with existing class
    meta_agent2 = create_meta_agent(
        model,
        "MetaAgentClass",
        [agents[1], agents[3]],
        meta_attributes={"attribute2": "value2"},
        meta_functions={"function2": lambda self: "function2"},
        retain_subagent_attributes=True,
    )
    assert meta_agent is not None
    assert meta_agent2.attribute2 == "value2"
    assert meta_agent.function1() == "function1"
    assert meta_agent.agents == {agents[2], agents[0]}
    assert meta_agent2.function2() == "function2"
    assert meta_agent2.agents == {agents[1], agents[3]}
    assert hasattr(meta_agent2, "custom_attribute")
    assert meta_agent2.custom_attribute == "custom_value"


def test_add_agents_to_existing_meta_agent(setup_agents):
    """Test adding agents to an existing meta-agent instance.

    Args:
        setup_agents (tuple): The model and agents fixture.
    """
    model, agents = setup_agents

    meta_agent1 = create_meta_agent(
        model,
        "MetaAgentClass",
        [agents[0], agents[3]],
        meta_attributes={"attribute1": "value1"},
        meta_functions={"function1": lambda self: "function1"},
        retain_subagent_attributes=True,
    )

    create_meta_agent(
        model,
        "MetaAgentClass",
        [agents[1], agents[0], agents[2]],
        retain_subagent_attributes=True,
    )
    assert meta_agent1.agents == {agents[0], agents[1], agents[2], agents[3]}
    assert meta_agent1.function1() == "function1"
    assert meta_agent1.attribute1 == "value1"
    assert hasattr(meta_agent1, "custom_attribute")
    assert meta_agent1.custom_attribute == "custom_value"
