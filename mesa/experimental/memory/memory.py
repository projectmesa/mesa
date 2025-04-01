"""An entry-recording functionality designed to be used as the memory of an agent.

This module provides the foundational class needed for storing information in the memory of an agent.
Then objective is to implement a very simple and efficient system that can be used for any agent and
for any kind of information (an entry). The user defines the capacity of the memory chooses the format
of the entries, which allows for a greater flexibility.

Features:

- Capacity-based short-term memory, with a FIFO system.
- Efficient storage and retrieval of entries.
- Support for different entry types of entries.
- Possibility to send entries to other agents.

For now, the module contains only one main component:
- Memory: A class representing the memory of an agent.
"""

import copy
from collections import deque
from typing import Any


class MemoryEntry:
    """Base class for all memory entries."""

    def __init__(
        self,
        entry_content: str,
        entry_step: int,
        entry_type: str,
        entry_metadata: dict | None = None,
    ):
        """Initialize a MemoryEntry with given content, step, type, and optional metadata."""
        self.entry_content = entry_content
        self.entry_step = entry_step
        self.entry_type = entry_type
        self.entry_metadata = entry_metadata or {}

    def to_dict(self) -> dict:
        """Convert memory entry to dictionary for serialization."""
        return {
            "entry_content": self.entry_content,
            "entry_step": self.entry_step,
            "entry_type": self.entry_type,
            "entry_metadata": self.entry_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """Create memory entry from dictionary."""
        entry = cls(
            entry_content=data["entry_content"],
            entry_step=data["entry_step"],
            entry_type=data["entry_type"],
            entry_metadata=data["entry_metadata"],
        )
        return entry


class ShortTermMemory:
    """Short-term memory with limited capacity that follows recency principles.

    Implemented as a double-ended queue with O(1) add/remove operations.
    """

    def __init__(self, model, capacity: int = 10):
        """Initialize ShortTermMemory with a model and capacity."""
        self.model = model
        self.capacity = capacity
        self.entries = deque(maxlen=capacity)

    def add(
        self,
        model,
        entry_content: str | None = None,
        entry_type: str = "general",
        entry_metadata: dict | None = None,
        entry=None,
    ) -> MemoryEntry:
        """Add a new entry to short-term memory."""
        if entry is not None:
            self.entries.append(entry)
            return entry

        entry_metadata = entry_metadata or {}
        entry = MemoryEntry(
            entry_step=model.step,
            entry_content=entry_content,
            entry_type=entry_type,
            entry_metadata=entry_metadata,
        )
        self.entries.append(entry)
        return entry

    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """Get n most recent entries."""
        return list(self.entries)[-n:]

    def get_by_id(self, entry_id) -> MemoryEntry | None:
        """Retrieve an entry by its ID."""
        entry_list = [entry for entry in self.entries if id(entry) == entry_id]
        if entry_list:
            return entry_list[0]
        else:
            return None

    def get_by_type(self, entry_type: str) -> list[MemoryEntry]:
        """Get entries from a specific entry type."""
        entry_list = [entry for entry in self.entries if entry.entry_type == entry_type]
        return entry_list

    def forget_last(self) -> bool:
        """Remove the most recent entry from memory. Returns True if successful."""
        if self.entries:
            self.entries.pop()
            return True
        else:
            return False

    def forget_first(self) -> bool:
        """Remove the oldest entry from memory. Returns True if successful."""
        if self.entries:
            self.entries.popleft()
            return True
        else:
            return False

    def forget(self, entry_id=None, entry: MemoryEntry = None) -> bool:
        """Remove an entry from short-term memory."""
        if entry_id is not None:
            entry_list = [entry for entry in self.entries if id(entry) == entry_id]
            if entry_list:
                entry = entry_list[0]
        if isinstance(entry, MemoryEntry):
            try:
                self.entries.remove(entry)
                return True
            except ValueError:
                return False
        return False

    def clear(self):
        """Remove all entries from memory."""
        self.entries.clear()


class LongTermMemory:
    """Long-term memory with categorization and importance-based retrieval.

    Implemented using dictionaries for O(1) entry type access.
    """

    def __init__(self, model):
        """Initialize LongTermMemory with a model."""
        self.model = model
        self.entries: dict[int, MemoryEntry] = {}

    def add(
        self,
        model,
        entry_content: str | None = None,
        entry_type: str = "general",
        entry_metadata: dict | None = None,
        entry=None,
    ) -> MemoryEntry:
        """Add a new entry to long-term memory."""
        if entry is not None:
            entry_id = id(entry)
            self.entries[entry_id] = entry
            return entry

        entry_metadata = entry_metadata or {}
        entry = MemoryEntry(
            entry_step=model.step,
            entry_content=entry_content,
            entry_type=entry_type,
            entry_metadata=entry_metadata,
        )
        entry_id = id(entry)
        self.entries[entry_id] = entry
        return entry

    def get_by_id(self, entry_id) -> MemoryEntry | None:
        """Retrieve an entry by its ID."""
        if entry_id in self.entries:
            return self.entries[entry_id]
        return None

    def get_by_type(self, entry_type: str) -> list[MemoryEntry]:
        """Get entries from a specific entry type."""
        entry_list = [
            entry for entry in self.entries.values() if entry.entry_type == entry_type
        ]
        return entry_list

    def forget(self, entry_id=None, entry: MemoryEntry = None) -> bool:
        """Remove an entry from long-term memory."""
        if entry:
            entry_id = id(entry)
        if entry_id is None or entry_id not in self.entries:
            return False
        del self.entries[entry_id]
        return True


class Memory:
    """Main memory manager combining short-term and long-term memory.

    Provides consolidation, search (by type for now) and memory transfer (communicate) functionality.
    """

    def __init__(self, agent, model, stm_capacity: int = 10):
        """Initialize Memory with an agent, model, and short-term memory capacity."""
        self.model = model
        self.agent = agent
        self.short_term = ShortTermMemory(model=self.model, capacity=stm_capacity)
        self.long_term = LongTermMemory(model=self.model)

    def remember_short_term(
        self,
        model,
        entry_content: Any,
        entry_type: str = "general",
        entry_metadata: dict | None = None,
    ) -> MemoryEntry:
        """Add an entry to short-term memory. Returns the MemoryEntry object created."""
        return self.short_term.add(model, entry_content, entry_type, entry_metadata)

    def remember_long_term(
        self,
        model,
        entry_content: Any,
        entry_type: str = "general",
        entry_metadata: dict | None = None,
    ) -> MemoryEntry:
        """Add an entry directly to long-term memory."""
        return self.long_term.add(model, entry_content, entry_type, entry_metadata)

    def consolidate(self, entry: MemoryEntry) -> MemoryEntry:
        """Transfer an entry from short-term to long-term memory.

        Returns the MemoryEntry object transferred.
        """
        entry = self.long_term.add(entry=entry, model=self.model)
        self.short_term.forget(entry_id=id(entry))
        return entry

    def get_by_type(
        self,
        entry_type: str,
        include_short_term: bool = True,
        include_long_term: bool = True,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Get a list of entries of the same entry type."""
        results: list[MemoryEntry] = []
        if include_short_term:
            short_results = self.short_term.get_by_type(entry_type)
            if short_results is not None:
                if isinstance(short_results, list):
                    results.extend(short_results)
                else:
                    results.append(short_results)
        if include_long_term:
            long_results = self.long_term.get_by_type(entry_type)
            if long_results is not None:
                if isinstance(long_results, list):
                    results.extend(long_results)
                else:
                    results.append(long_results)
        if not results:
            return []
        return results[:limit] if limit is not None else results

    def communicate(self, entry, external_agent):
        """Send a memory entry to another agent by making a deep copy of the entry."""
        entry_copy = copy.deepcopy(entry)
        entry_copy.entry_metadata["external_id"] = self.agent.unique_id
        new_entry = external_agent.memory.remember_short_term(
            model=self.model,
            entry_content=entry_copy.entry_content,
            entry_type=entry_copy.entry_type,
            entry_metadata=entry_copy.entry_metadata,
        )
        return new_entry
