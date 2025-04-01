"""Core event management functionality for Mesa's memory system.

This module provides the foundational data structures and classes needed for memory
entries recording in mesa. The Memory class is a manager between the ShortTermMemory
(dque data structure) and LongTermMemory (hash map).


The module now contains four main component:
- Memory: The operating class for managing ShortTermMemory and LongTermMemory
- ShortTermMemory more memory-efficient and reactive (efficient store and pop functionality)
- LongTermMemory : more computational-efficient (efficient navigation)
"""

from .memory import LongTermMemory, Memory, MemoryEntry, ShortTermMemory

__all__ = [
    "LongTermMemory",
    "Memory",
    "MemoryEntry",
    "ShortTermMemory",
]
