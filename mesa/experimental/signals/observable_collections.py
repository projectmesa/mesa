"""This module defines observable collections classes.

Observable collections behave like Observable but then for collections.


"""

from .signal import Observable, HasObservables

from collections.abc import MutableSequence

from typing import Any, Iterable

__all__ = ["ObservableList", ]


class ObservableList(Observable):
    """An ObservableList that emits signals on changes to the underlying list."""
    def __init__(self):
        """Initialize the ObservableList."""
        super().__init__()
        self.signal_types: set = {"added", "removed", "cleared", "replaced", "on_change"}
        self.fallback_value = []

    def __get__(self, instance: HasObservables, owner):
        """Get the value of the descriptor attribute.

        Args:
            instance: The instance from which to retrieve the attribute.
            owner: the class

        Returns:
            The value of the descriptor attribute.

        """
        return getattr(instance, self.private_name, self.fallback_value)

    def __set__(self, instance: "HasObservables", value: Iterable):
        """Set the value of the descriptor attribute.

        Args:
            instance: The instance on which to set the attribute.
            value: The value to set the attribute to.

        """
        instance.notify(self.public_name, self.__get__(instance, None), value, "on_change")
        setattr(instance, self.private_name, SignalingList(value, instance, self.public_name))


class SignalingList(MutableSequence[Any]):
    """A basic lists that emits signals on changes."""

    __slots__ = ["owner", "name", "data"]

    def __init__(self, iterable: Iterable, owner: HasObservables, name: str):
        """initialize a SignalingList.

        Args:
            iterable: initial values in the list
            owner: the HasObservables instance on which this list is defined
            name: the attribute name to which  this list is assigned

        """
        self.owner: HasObservables = owner
        self.name: str = name
        self.data = [entry for entry in iterable]

    def __setitem__(self, index: int, value: Any) -> None:
        """set item to index.

        Args:
            index: the index to set item to
            value: the item to set

        """
        old_value = self.data[index]
        self.data[index] = value
        self.owner.notify(self.name, old_value, value, "replaced")

    def __delitem__(self, index: int) -> None:
        """delete item at index.

        Args:
            index: The index of the item to remove

        """
        old_value = self.data
        del self.data[index]
        self.owner.notify(self.name, old_value, None, "removed")

    def __getitem__(self, index) -> Any:
        """get item at index.

        Args:
            index: The index of the item to retrieve

        Returns:
            the item at index
        """

        return self.data[index]

    def __len__(self) -> int:
        """Return the length of the list."""
        return len(self.data)

    def insert(self, index, value):
        """Insert value at index.

        Args:
            index: the index to insert value into
            value: the value to insert

        """
        old_value = self.data[index]
        self.data.insert(index, value)
        self.owner.notify(self.name, old_value, value, "added")
