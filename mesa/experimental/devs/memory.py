"""An entry-recording functionality designed to be used as the memory of an agent.

This module provides the foundational class needed for storing information in the memory of an agent.
Then objective is to implement a very simple and efficient system that can be used for any agent and
for any kind of information (an entry). The user defines the capacity of the memory chooses the format
of the entries, which allows for a greater flexibility. Key features:

- Capacity-based memory, with a FIFO system
- Efficient storage and retrieval of entries
- Support for different entry_types of entries
- Possibility to send entries to other agents

For now, the module contains only one main component:
- Memory: A class representing the memory of an agent

"""

# from experimental.devs.eventlist import EventList, SimulationEvent
import copy
import itertools
from collections import OrderedDict
from typing import Any

from mesa.model import Model


class Memory:
    """The memory of an Agent : it can store any kind of information based on a unique id of the form (agent_id, entry_id) to ensure the uniqueness of the entry.

    Attributes:
        model (Model): The used model
        agent_id (int): The id of the agent
        capacity (int): The capacity of the memory

    Structure of one entry (example):
        "entry_id" : {
            "external_agent_id" : external_agent_id, # Not mandatory : represents the agent that sent the entry (if memory was received)
            "entry_step" : 1,
            "entry_type" : "position",
            "entry_content" : [1,2]
        },

    """

    def __init__(self, model: Model, agent_id: int, capacity: int):
        """Initializes the agent memory."""
        self.model = model
        self.capacity = capacity
        self.agent_id = agent_id
        self._ids = itertools.count()

        self.memory_storage = OrderedDict()

    def remember(
        self, entry_content: Any, entry_type: Any, external_agent_id=None
    ) -> tuple:
        """Store an entry in the memory."""
        entry_id = (self.agent_id, next(self._ids))

        # creation of a new entry in the memory
        if entry_id not in self.memory_storage:
            self.memory_storage[entry_id] = OrderedDict()

        self.memory_storage[entry_id]["entry_content"] = entry_content
        self.memory_storage[entry_id]["entry_type"] = entry_type
        self.memory_storage[entry_id]["entry_step"] = self.model.steps

        if external_agent_id is not None:
            self.memory_storage[entry_id]["external_agent_id"] = external_agent_id

        # if the memory is longer than the capacity, we remove the oldest entry
        if len(self.memory_storage) > self.capacity:
            self.memory_storage.popitem(last=False)

        return entry_id

    def recall(self, entry_id):
        """Recall a specific entry."""
        # Verification of the existence of the entry
        if entry_id not in self.memory_storage:
            return None
        return self.memory_storage[entry_id]

    def get_by_type(self, entry_type: str) -> list:
        """Returns all the ids of the entries of a specific entry_type."""
        entry_list = [
            entry_id
            for entry_id, entry in self.memory_storage.items()
            if entry["entry_type"] == entry_type
        ]
        return entry_list

    def forget(self, entry_id):
        """Forget a specific entry."""
        if entry_id in self.memory_storage:
            self.memory_storage.pop(entry_id)

    def tell_to(self, entry_id, external_agent):
        """Send a precise memory to another agent by making a deep copy of the entry."""
        entry_copy = copy.deepcopy(self.memory_storage[entry_id])
        new_entry_id = external_agent.memory.remember(
            entry_copy["entry_content"],
            entry_copy["entry_type"],
            external_agent_id=self.agent_id,
        )

        return new_entry_id
