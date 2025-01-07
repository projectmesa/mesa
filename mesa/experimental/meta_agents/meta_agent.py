"""Implementation of Mesa's meta agent capability.

This contains two helper functions and a MetaAgent class that can be used to create agents that contain other agents as components.

Helper functions:
1 - find_combinations: Find combinations of agents to create a meta-agent subset.
2- evaluate_combination: Evaluate combinations of agents by some user based criteria to determine if it should be a subset.

Meta-Agent class (MetaAgent): An agent that contains other agents as components.
"""

import itertools
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from mesa.agent import Agent, AgentSet


def evaluate_combination(
    candidate_group: tuple[Agent, ...],
    model,
    evaluation_func: Callable[[AgentSet], float] | None,
) -> tuple[AgentSet, float] | None:
    """Evaluate a combination of agents.

    Args:
        candidate_group (Tuple[Agent, ...]): The group of agents to evaluate.
        model: The model instance.
        evaluation_func (Optional[Callable[[AgentSet], float]]): The function to evaluate the group.

    Returns:
        Optional[Tuple[AgentSet, float]]: The evaluated group and its value, or None.
    """
    group_set = AgentSet(candidate_group, random=model.random)
    if evaluation_func:
        value = evaluation_func(group_set)
        return group_set, value
    return None


def find_combinations(
    model,
    group: AgentSet,
    size: int | tuple[int, int] = (2, 5),
    evaluation_func: Callable[[AgentSet], float] | None = None,
    filter_func: Callable[[list[tuple[AgentSet, float]]], list[tuple[AgentSet, float]]]
    | None = None,
) -> list[tuple[AgentSet, float]]:
    """Find valuable combinations of agents in this set.

    Args:
        model: The model instance.
        group (AgentSet): The set of agents to find combinations in.
        size (Union[int, Tuple[int, int]], optional): The size or range of sizes for combinations. Defaults to (2, 5).
        evaluation_func (Optional[Callable[[AgentSet], float]], optional): The function to evaluate combinations. Defaults to None.
        filter_func (Optional[Callable[[List[Tuple[AgentSet, float]]], List[Tuple[AgentSet, float]]]], optional): The function to filter combinations. Defaults to None.

    Returns:
        List[Tuple[AgentSet, float]]: The list of valuable combinations.
    """
    combinations = []
    with ThreadPoolExecutor() as executor:
        futures = []
        # Allow one size or range of sizes to be passed
        size_range = (size, size + 1) if isinstance(size, int) else size

        candidate_groups = itertools.chain.from_iterable(
            itertools.combinations(group, size) for size in range(*size_range)
        )
        for candidate_group in candidate_groups:
            futures.append(
                executor.submit(
                    evaluate_combination, candidate_group, model, evaluation_func
                )
            )

        for future in futures:
            group_set, result = future.result()
            if result:
                combinations.append((group_set, result))

    if len(combinations) > 0 and filter_func:
        filtered_combinations = filter_func(combinations)
        return filtered_combinations

    return combinations


class MetaAgent(Agent):
    """A MetaAgent is an agent that contains other agents as components."""

    def __init__(self, model, agents: set[Agent] | None = None):
        """Create a new MetaAgent.

        Args:
            model: The model instance.
            agents (Optional[set[Agent]], optional): The set of agents to include in the MetaAgent. Defaults to None.
        """
        super().__init__(model)
        self._subset = AgentSet(agents or [], random=model.random)

        # Add ref to meta_agent in subagents
        for agent in self._subset:
            agent.meta_agent = self  # TODO: Make a set for meta_agents

    def __len__(self) -> int:
        """Return the number of components."""
        return len(self._subset)

    def __iter__(self):
        """Iterate over components."""
        return iter(self._subset)

    def __contains__(self, agent: Agent) -> bool:
        """Check if an agent is a component."""
        return agent in self._subset

    @property
    def subset(self) -> AgentSet:
        """Read-only access to components as an AgentSet."""
        return self._subset

    def add_subagents(self, new_agents: set[Agent]):
        """Add agents as components.

        Args:
            new_agents (set[Agent]): The agents to add to MetaAgent subset.
        """
        for agent in new_agents:
            self._subset.add(agent)
            agent.meta_agent = self  # TODO: Make a set for meta_agents

    def remove_subagents(self, remove_agents: set[Agent]):
        """Remove agents as components.

        Args:
            remove_agents (set[Agent]): The agents to remove from MetaAgent.
        """
        for agent in remove_agents:
            self._subset.discard(agent)
            agent.meta_agent = None  # TODO: Remove meta_agent from set

    def step(self):
        """Perform the agent's step.

        Override this method to define the meta agent's behavior.
        By default, does nothing.
        """
