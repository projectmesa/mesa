"""Implementation of Mesa's meta agent capability."""

from mesa.agent import Agent, AgentSet


class MetaAgent(Agent):
    """A MetaAgent is an agent that contains other agents as components."""

    def __init__(self, model, agents):
        """Create a new MetaAgent."""
        super().__init__(model)
        self._subset = AgentSet(agents or [], random=model.random)

        # Add ref to meta_agent in subagents
        for agent in self._subset:
            agent.meta_agent = self  # TODO: Make a set for meta_agents

    @property
    def subset(self):
        """Read-only access to components as an AgentSet."""
        return self._subset

    def add_subagents(self, new_agents: set[Agent]):
        """Add an agent as a component.

        Args:
            new_agents (Agent): The agents to add to MetaAgent subset
        """
        for agent in new_agents:
            self._subset.add(agent)

        for agent in new_agents:
            agent.meta_agent = self  # TODO: Make a set for meta_agents

    def remove_subagents(self, remove_agents: set[Agent]):
        """Remove an agent component.

        Args:
            remove_agents (Agent): The agents to remove from MetAgents


        """
        for agent in remove_agents:
            self._subset.discard(agent)

        for agent in remove_agents:
            agent.meta_agent = None  # TODO: Remove meta_agent from set

    def step(self):
        """Perform the agent's step.

        Override this method to define the meta agent's behavior.
        By default, does nothing.
        """

    def __len__(self):
        """Return the number of components."""
        return len(self._subset)

    def __iter__(self):
        """Iterate over components."""
        return iter(self._subset)

    def __contains__(self, agent):
        """Check if an agent is a component."""
        return agent in self._subset
