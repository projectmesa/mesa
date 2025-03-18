"""Implementation of Mesa's meta agent capability.

This contains two helper methods and a MetaAgent class that can be used to
create agents that contain other agents as components.

Helper methods:
1 - find_combinations: Find combinations of agents to create a meta-agent
subset.
2- evaluate_combination: Evaluate combinations of agents by some user based
criteria to determine if it should be a subset.

Meta-Agent class (MetaAgent): An agent that contains other agents
as components.

See basic examples >> meta_agents for dynamic creation and explicit creation
"""

import itertools
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from types import MethodType
from typing import Any

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
        evaluation_func (Optional[Callable[[AgentSet], float]]): The function
        to evaluate the group.

    Returns:
        Optional[Tuple[AgentSet, float]]: The evaluated group and its value,
        or None.
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
        size (Union[int, Tuple[int, int]], optional): The size or range of
        sizes for combinations. Defaults to (2, 5).
        evaluation_func (Optional[Callable[[AgentSet], float]], optional): The
          function to evaluate combinations. Defaults to None.
        filter_func (Optional[Callable[[List[Tuple[AgentSet, float]]]): Allows
          the user to specify how agents are filtered to form groups.
          Defaults to None.
        List[Tuple[AgentSet, float]]]], optional): The function to filter
        combinations. Defaults to None.

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


def extract_class(agents_by_type: dict, new_agent_class: str):
    """Helper function for create_meta_agents extracts the type of agent
    being created to create a new instance of that agent type.

    Args:
        agents_by_type (dict): The dictionary of agents by type.
        new_agent_class (str): The name of the agent class to be created

    Returns:
        type(Agent) if it agent type exists
        None otherwise
    """

    if new_agent_class in agents_by_type:
        return type(agents_by_type[new_agent_class][0])
    return None


def create_meta_agent(
    model: Any,
    new_agent_class: str,
    agents: Iterable[Any],
    mesa_agent_type=Agent,
    meta_attributes: dict[str, Any] = dict(),  # noqa B006
    meta_methods: dict[str, Callable] = dict(),  # noqa B006
    assume_subagent_methods: bool = False,
    assume_subagent_attributes: bool = False,
) -> Any | None:
    
    """Dynamically create a new meta-agent class and instantiate agents
    in that class.

    Parameters:
    model (Any): The model instance.
    new_agent_class (str): The name of the new meta-agent class.
    agents (Iterable[Any]): The agents to be included in the meta-agent.
    meta_attributes (Dict[str, Any]): Attributes to be added to the meta-agent.
    meta_methods (Dict[str, Callable]): Methods to be added to the meta-agent.
    assume_subagent_methods (bool): Whether to assume methods from
    sub-agents as meta_agent methods.
    assume_subagent_attributes (bool): Whether to retain attributes
    from sub-agents.

    Returns:
        Optional[Any]:
            - None if adding agent(s) to existing class
            - New class instance if created a new instance of a dynamically
            created agent type
            - New class instance if created a new dynamically created agent type
    """
    
    # Convert agents to set to ensure uniqueness
    agents = set(agents)

    def add_methods(
        meta_agent_instance: Any,
        agents: Iterable[Any],
        meta_methods: dict[str, Callable],
    ) -> None:
        """Add methods to the meta-agent instance.

        Parameters:
        meta_agent_instance (Any): The meta-agent instance.
        agents (Iterable[Any]): The agents to derive methods from.
        meta_methods (Dict[str, Callable]): methods to be added to the meta-agent.
        """
        if assume_subagent_methods:
            agent_classes = {type(agent) for agent in agents}
            for agent_class in agent_classes:
                for name in agent_class.__dict__:
                    if callable(getattr(agent_class, name)) and not name.startswith(
                        "__"
                    ):
                        original_method = getattr(agent_class, name)
                        meta_methods[name] = original_method

        for name, meth in meta_methods.items():
            bound_method = MethodType(meth, meta_agent_instance)
            setattr(meta_agent_instance, name, bound_method)

    def add_attributes(
        meta_agent_instance: Any, agents: Iterable[Any], meta_attributes: dict[str, Any]
    ) -> None:
        """Add attributes to the meta-agent instance.

        Parameters:
        meta_agent_instance (Any): The meta-agent instance.
        agents (Iterable[Any]): The agents to derive attributes from.
        meta_attributes (Dict[str, Any]): Attributes to be added to the
        meta-agent.
        """
        if assume_subagent_attributes:
            for agent in agents:
                for name, value in agent.__dict__.items():
                    if not callable(value):
                        meta_attributes[name] = value

        for key, value in meta_attributes.items():
            setattr(meta_agent_instance, key, value)

    # Path 1 - Add agents to existing meta-agent
    subagents = [a for a in agents if hasattr(a, "meta_agent")]
    if len(subagents) > 0:
        if len(subagents) == 1:
            add_attributes(subagents[0].meta_agent, agents, meta_attributes)
            add_methods(subagents[0].meta_agent, agents, meta_methods)
            subagents[0].meta_agent.add_subagents(agents)

        else:
            subagent = model.random.choice(subagents)
            agents = set(agents) - set(subagents)
            add_attributes(subagent.meta_agent, agents, meta_attributes)
            add_methods(subagent.meta_agent, agents, meta_methods)
            subagent.meta_agent.add_subagents(agents)
            # TODO: Add way for user to specify how agents join meta-agent
            # instead of random choice
    else:
        # Path 2 - Create a new instance of an existing meta-agent class
        agent_class = extract_class(model.agents_by_type, new_agent_class)
        if agent_class:
            meta_agent_instance = agent_class(model, agents)
            add_attributes(meta_agent_instance, agents, meta_attributes)
            add_methods(meta_agent_instance, agents, meta_methods)
            return meta_agent_instance
        else:
            # Path 3 - Create a new meta-agent class
            meta_agent_class = type(
                new_agent_class,
                (MetaAgent, mesa_agent_type),  # Use the meta_agent_type parameter here
                {
                    "unique_id": None,
                    "_subset": None,
                },
            )
            meta_agent_instance = meta_agent_class(model, agents)
            add_attributes(meta_agent_instance, agents, meta_attributes)
            add_methods(meta_agent_instance, agents, meta_methods)
            return meta_agent_instance


class MetaAgent(Agent):
    """A MetaAgent is an agent that contains other agents as components."""

    def __init__(
        self, model, agents: set[Agent] | None = None, name: str = "MetaAgent"
    ):
        """Create a new MetaAgent.

        Args:
            model: The model instance.
            agents (Optional[set[Agent]], optional): The set of agents to
            include in the MetaAgent. Defaults to None.
            name (str, optional): The name of the MetaAgent. Defaults to "MetaAgent".
        """
        super().__init__(model, key_by_name=True)
        self._subset = AgentSet(agents or [], random=model.random)
        self.name = name

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
    def agents(self) -> AgentSet:
        """Get list of Meta-Agent subagents."""
        return set(self._subset)

    @property
    def subagents_by_type(self) -> dict[type, list[Agent]]:
        """Get the subagents grouped by type.

        Returns:
            dict[type, list[Agent]]: A dictionary of subagents grouped by type.
        """
        subagents_by_type = {}
        for agent in self._subset:
            agent_type = type(agent)
            if agent_type not in subagents_by_type:
                subagents_by_type[agent_type] = []
            subagents_by_type[agent_type].append(agent)
        return subagents_by_type

    @property
    def subagent_types(self) -> set[type]:
        """Get the types of all subagents.

        Returns:
            set[type]: A set of unique types of the subagents.
        """
        return {type(agent) for agent in self._subset}

    def get_subagent_instance(self, agent_type) -> set[type]:
        """Get the instance of a subagent of the specified type.

        Args:
            agent_type: The type of the subagent to retrieve.

        Returns:
            The first instance of the specified subagent type.

        Raises:
            ValueError: If no subagent of the specified type is found.
        """
        try:
            return self.subagents_by_type[agent_type][0]
        except KeyError:
            raise ValueError(f"No subagent of type {agent_type} found.")

    def add_subagents(
        self,
        new_agents: set[Agent],
    ):
        """Add agents as components.

        Args:
            new_agents (set[Agent]): The agents to add to MetaAgent subset.
        """
        for agent in new_agents:
            self._subset.add(agent)
            agent.meta_agent = self  # TODO: Make a set for meta_agents
            self.model.register_agent(agent)

    def remove_subagents(self, remove_agents: set[Agent]):
        """Remove agents as components.

        Args:
            remove_agents (set[Agent]): The agents to remove from MetaAgent.
        """
        for agent in remove_agents:
            self._subset.discard(agent)
            agent.meta_agent = None  # TODO: Remove meta_agent from set
            self.model.deregister_agent(agent)

    def get_subagent_type(self) -> set[type]:
        """Get the types of all subagents.

        Returns:
            set[type]: A set of unique types of the subagents.
        """
        return {type(agent) for agent in self._subset}

    def step(self):
        """Perform the agent's step.

        Override this method to define the meta agent's behavior.
        By default, does nothing.
        """
