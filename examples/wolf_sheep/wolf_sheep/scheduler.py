from typing import Type, Callable
from mesa.agent import Agent
from mesa.time import RandomActivationByType


class RandomActivationByTypeFiltered(RandomActivationByType):
    """
    A scheduler that overrides the get_type_count method to allow for filtering
    of agents by a function before counting.

    Example:
    >>> scheduler = RandomActivationByTypeFiltered(model)
    >>> scheduler.get_type_count(AgentA, lambda agent: agent.some_attribute > 10)
    """

    def get_type_count(
        self, type_class: Type[Agent], filter_func: Callable[[Agent], bool] = None
    ) -> int:
        """
        Returns the current number of agents of certain type in the queue that satisfy the filter function.
        """
        count = 0
        for agent in self.agents_by_type[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count
