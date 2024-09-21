import weakref
import functools

from typing import Callable, Any
from collections import defaultdict, namedtuple

__all__ = ["Observable", "HasObservables"]


class Computable:
    """A Computable that is depended on one or more Observables

    # fixme how to make this work with Descriptors?
    # we would need to now the owner (can also be in init)

    """

    def __init__(self, callable: Callable, *args, **kwargs):
        """

        Args:
            callable: the callable that is computed
            *args: arguments to pass to the callable
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

    def __get__(self):
        # fixme: not sure this will work correctly

        if self._is_dirty:
            self.value = self.callable(*self.args, **self.kwargs)
            self._is_dirty = False
        return self.value


class Observable:
    def __init__(self):
        self.public_name: str
        self.private_name: str
        self.signal_types: set = set("on_change", )
        self.fallback_value = None  # fixme, should this be user specifiable

    def __get__(self, instance, owner):
        # fixme how do we want to handle the fallback value
        # and when should it raise an attribute error?
        return getattr(instance, self.private_name, self.fallback_value)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        owner.observables[name] = self

    def __set__(self, instance: "HasObservables", value):
        instance.notify(self.public_name, self.__get__(instance, None), value, "on_change")
        setattr(instance, self.private_name, value)


class All:
    """Helper constant to subscribe to all Observables"""

    def __init__(self):
        self.name = "all_signals"

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


Signal = namedtuple("Signal", "owner observable old_value new_value signal_type")


class HasObservables:
    observables: dict[str, Observable] = {}

    def __new__(cls, *args, **kwargs):
        # fixme dirty hack because super does not work on agents
        obj = super().__new__(cls)

        # some kind of nested dict
        # we have the name of observable as a key
        # we have signal_type as a key
        # we want weakrefs for the callable
        obj.subscribers: dict[str, dict[str, weakref.WeakValueDictionary]] = defaultdict(
            functools.partial(defaultdict, weakref.WeakValueDictionary))

        return obj


    def register_observable(self, observable: Observable):
        """register an Observable

        Args:
            observable: the Observable to register

        """
        self.observables[observable.public_name] = observable

    def observe(self, name: str | All, signal_type: str, handler: Callable, ):
        """Subscribe to the Observable <name> for signal_type

        Args:
            name: name of the Observable to subscribe to
            signal_type: the type of signal on the Observable to subscribe to
            handler: the handler to call

        """
        names = [name, ] if not isinstance(name, All) else self.observables.keys()

        for name in names:
            if signal_type not in self.observables[name].signal_types:
                raise ValueError((f"you are trying to subscribe to a signal of {signal_type}"
                                  "on Observable {name}, which does not emit this signal_type")
                                 )

            self.subscribers[name][signal_type] = handler

    def unobserve(self, name: str | All, signal_type: str):
        """Unsubscribe to the Observable <name> for signal_type

        Args:
            name: name of the Observable to unsubscribe to
            signal_type: the type of signal on the Observable to unsubscribe to

        Returns:

        """
        names = [name, ] if not isinstance(name, All) else self.observables.keys()

        for name in names:
            del self.subscribers[name][signal_type]

    def unobserve_all(self, name: str | All):
        """Clears all subscriptions for the observable <name>

        if name is All, all subscriptions are removed

        Args
            name: name of the Observable to unsubscribe for all signal types

        """
        if name is not isinstance(name, All):
            del self.subscribers[name]
        else:
            self.subscribers = defaultdict(functools.partial(defaultdict, weakref.WeakValueDictionary))

    def notify(self, observable: str, old_value: Any, new_value: Any, signal_type: str):
        """emit a signal

        Args:
            observable: the public name of the observable emiting the signal
            old_value: the old value of the observable
            new_value: the new value of the observable
            signal_type: the type of signal to emit

        """
        # fixme: currently strongly tied to just on_change signals
        #  this needs to be refined for e.g. list and dicts in due course
        #  idea is to just mimic how traitlets handles this
        signal = Signal(self, observable, old_value, new_value, signal_type)

        observers = self.subscribers[observable][signal_type]
        for observer in observers:
            observer(signal)


if __name__ == "__main__":
    from mesa import Agent, Model

    import traitlets
    traitlets.Int


    class A(Agent, HasObservables):
        a = Observable(int)


    class B(A, HasObservables):
        b = Observable(int)


    model = Model()

    a = A(model)
    b = B(model)


    def specific_handler(arg: int):
        print(f"specific handler {arg}")


    def generic_handler(info: psygnal.EmissionInfo):
        signalinstance, arguments = info
        print(
            f"received signal from {signalinstance.instance} about {signalinstance.name}: {arguments}"
        )


    a.a_changed.connect(specific_handler)
    b.signals["a_changed"].connect(specific_handler)
    b.signals.connect(generic_handler)

    print(b.signals["a_changed"] == b.a_changed)

    a.a = 5
    b.a = 6
    b.b = 7
