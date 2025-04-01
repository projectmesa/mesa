"""Core event management functionality for Mesa's memory system.

This module provides the foundational data structures and classes needed for memory
entries recording in mesa. The Memory class is a manager between the ShortTermMemory
(dque data structure) and LongTermMemory (hash map).

Key features:

- Priority-based event ordering
- Weak references to prevent memory leaks from canceled events
- Efficient event insertion and removal using a heap queue
- Support for event cancellation without breaking the heap structure

The module contains three main components:
- Priority: An enumeration defining event priority levels (HIGH, DEFAULT, LOW)
- SimulationEvent: A class representing individual events with timing and execution details
- EventList: A heap-based priority queue managing the chronological ordering of events

The implementation supports both pure discrete event simulation and hybrid approaches
combining agent-based modeling with event scheduling.
"""

from .memory import LongTermMemory, Memory, MemoryEntry, ShortTermMemory

__all__ = [
    "LongTermMemory",
    "Memory",
    "MemoryEntry",
    "ShortTermMemory",
]
