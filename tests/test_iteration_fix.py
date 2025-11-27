"""Test AgentSet iteration with garbage collection (Python 3.14 fix)."""

import gc

from mesa.agent import Agent, AgentSet
from mesa.model import Model


class TestAgent(Agent):
    """Simple agent for testing."""


def test_agentset_iteration_with_gc():
    """Test that AgentSet iteration doesn't fail when GC runs during iteration."""
    model = Model()
    agents = [TestAgent(model) for _ in range(100)]
    agentset = AgentSet(agents, random=model.random)

    # Test iteration with forced GC
    collected_ids = []
    for i, agent in enumerate(agentset):
        collected_ids.append(agent.unique_id)
        if i % 10 == 0:
            gc.collect()  # Force GC during iteration

    assert len(collected_ids) == 100
    print("Test passed: Iteration with GC works!")


if __name__ == "__main__":
    test_agentset_iteration_with_gc()
    print("\nAll tests passed!")
