"""Core classes for Observables."""

import contextlib
import functools
import itertools
import weakref
from collections import defaultdict, namedtuple
from collections.abc import Callable
from typing import Any

__all__ = ["Observable", "HasObservables"]


class Computable:
    """A Computable that is depended on one or more Observables.

    # fixme how to make this work with Descriptors?
    # we would need to now the owner (can also be in init)

    """

    def __init__(self, callable: Callable, *args, **kwargs):
        """Draft Computable.

        Args:
            callable: the callable that is computed
            args: arguments to pass to the callable
            **kwargs: keyword arguments to pass to the callable

        """
        # fixme: what if these are observable?
        #   basically the logic for subscribing should go into the observable class
        #   but we might have to split up a few things here
        #   easy fix is to just declare an attribute Observable at the class level
        #   and next assign a Computed to this attribute.
        #   not sure how this would work, because observable would return the computable
        #   not its internal value. So, you could either
        #   have a separate observable or let the observable check if the value
        #   is a computed and thus do an additional get operation on this

        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self._is_dirty = True

    def __get__(self, instance, owner):
        # fixme: not sure this will work correctly

        if self._is_dirty:
            self.value = self.callable(*self.args, **self.kwargs)
            self._is_dirty = False
        return self.value


class Observable:
    """Base Observable class."""
    # fixme, we might want to have a base observable
    #  and move some of this into this class and use super to allways use it
    #  for example the on_change notify can go there

    def __init__(self):
        """Initialize an Observable."""
        self.public_name: str
        self.private_name: str

        # fixme can we make this an innerclass enum?
        self.signal_types: set = set(
            "on_change",
        )
        self.fallback_value = None  # fixme, should this be user specifiable

    def __get__(self, instance, owner):  # noqa D103
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):  # noqa D103
        self.public_name = name
        self.private_name = f"_{name}"
        owner.observables[name] = self

    def __set__(self, instance: "HasObservables", value):  # noqa D103
        instance.notify(
            self.public_name, getattr(instance, self.private_name, self.fallback_value), value, "on_change"
        )
        setattr(instance, self.private_name, value)


class All:
    """Helper constant to subscribe to all Observables."""

    def __init__(self):
        self.name = "all_signals"

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


Signal = namedtuple("Signal", "owner observable old_value new_value signal_type")


class HasObservables:
    """HasObservables class."""

    observables: dict[str, Observable] = {}
    subscribers: dict[str, dict[str, weakref.WeakSet]]

    def __new__(cls, *args, **kwargs):  # noqa D102
        # fixme dirty hack because super does not work on agents
        obj = super().__new__(cls)

        # some kind of nested dict
        # we have the name of observable as a key
        # we have signal_type as a key
        # we want weakrefs for the callable

        obj.subscribers: dict[str, dict[str, weakref.WeakSet]] = defaultdict(
            functools.partial(defaultdict, weakref.WeakSet)
        )

        return obj

    def register_observable(self, observable: Observable):
        """Register an Observable.

        Args:
            observable: the Observable to register

        """
        self.observables[observable.public_name] = observable

    def observe(
        self,
        name: str | All,
        signal_type: str | All,
        handler: Callable,
    ):
        """Subscribe to the Observable <name> for signal_type.

        Args:
            name: name of the Observable to subscribe to
            signal_type: the type of signal on the Observable to subscribe to
            handler: the handler to call

        Raises:
            ValueError: if the Observable <name> is not registered or if the Observable
            does not emit the given signal_type


        fixme should name/signal_type also take a list?

        """
        # fixme: we have the same code here twice, can we move this to a helper method?
        if not isinstance(name, All):
            if name not in self.observables:
                raise ValueError(
                    f"you are trying to subscribe to {name}, but this Observable is not known"
                )
            else:
                names = [
                    name,
                ]
        else:
            names = self.observables.keys()

        if not isinstance(signal_type, All):
            if signal_type not in self.observables[name].signal_types:
                raise ValueError(
                    f"you are trying to subscribe to a signal of {signal_type}"
                    f"on Observable {name}, which does not emit this signal_type"
                )
            else:
                signal_types = [
                    signal_type,
                ]
        else:
            signal_types = self.observables[name].signal_types

        for name, signal_type in itertools.product(names, signal_types):
            self.subscribers[name][signal_type].add(handler)

    def unobserve(self, name: str | All, signal_type: str | All):
        """Unsubscribe to the Observable <name> for signal_type.

        Args:
            name: name of the Observable to unsubscribe to
            signal_type: the type of signal on the Observable to unsubscribe to

        """
        names = (
            [
                name,
            ]
            if not isinstance(name, All)
            else self.observables.keys()
        )

        if isinstance(signal_type, All):
            signal_types = self.observables[name].signal_types
        else:
            signal_types = [
                signal_type,
            ]

        for name, signal_type in itertools.product(names, signal_types):
            with contextlib.suppress(KeyError):
                del self.subscribers[name][signal_type]
                # we silently ignore trying to remove unsubscribed
                # observables and/or signal types

    def unobserve_all(self, name: str | All):
        """Clears all subscriptions for the observable <name>.

        if name is All, all subscriptions are removed

        Args:
            name: name of the Observable to unsubscribe for all signal types

        """
        if name is not isinstance(name, All):
            with contextlib.suppress(KeyError):
                del self.subscribers[name]
                # ignore when unsubscribing to  Observables that have no subscription
        else:
            self.subscribers = defaultdict(
                functools.partial(defaultdict, weakref.WeakSet)
            )

    def notify(self, observable: str, old_value: Any, new_value: Any, signal_type: str):
        """Emit a signal.

        Args:
            observable: the public name of the observable emitting the signal
            old_value: the old value of the observable
            new_value: the new value of the observable
            signal_type: the type of signal to emit

        """
        # fixme: currently strongly tied to just on_change signals
        #  this needs to be refined for e.g. list and dicts in due course
        #  idea is to just mimic how traitlets handles this.
        #  Traitlets uses a Bunch helper class which turns a dict into something with
        #  attribute access. This will be richer than the current Signal named tuple
        signal = Signal(self, observable, old_value, new_value, signal_type)

        observers = self.subscribers[observable][signal_type]
        for observer in observers:
            observer(signal)
