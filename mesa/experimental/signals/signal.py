"""Core classes for Observables."""

import contextlib
import functools
import itertools
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from collections.abc import Callable
from typing import Any

__all__ = ["Observable", "HasObservables"]

CURRENT_COMPUTED: "Computed" | None = None  # the current Computed that is evaluating


class BaseObservable(ABC):
    """Abstract base class for all Observables."""

    @abstractmethod
    def __init__(self):
        """Initialize a BaseObservable."""
        self.public_name: str
        self.private_name: str

        # fixme can we make this an innerclass enum?
        #  or some SignalTypes helper class?
        #  its even more complicated. Ideally you can define
        #  signal_types throughout the class hierarchy and they are just
        #  combined together.
        self.signal_types: set
        self.fallback_value = None  # fixme, should this be user specifiable?

    def __get__(self, instance, owner):
        value = getattr(instance, self.private_name)

        if CURRENT_COMPUTED is not None:
            # there is a computed dependent on this Observable, so let's add
            # this Observable as a parent
            CURRENT_COMPUTED._add_parent(self, instance, self.public_name, value)

        return value

    def __set_name__(self, owner: "HasObservables", name: str):
        self.public_name = name
        self.private_name = f"_{name}"
        owner.register_observable(self)

    @abstractmethod
    def __set__(self, instance: "HasObservables", value):
        # this only emits an on change signal, subclasses need to specify
        # this in more detail
        instance.notify(
            self.public_name,
            getattr(instance, self.private_name, self.fallback_value),
            value,
            "on_change",
        )


class Observable(BaseObservable):
    """Observable class."""

    def __init__(self):
        """Initialize an Observable."""
        super().__init__()

        # fixme can we make this an innerclass enum?
        #  or some SignalTypes helper class?
        self.signal_types: set = set(
            "on_change",
        )
        self.fallback_value = None  # fixme, should this be user specifiable

    def __set__(self, instance: "HasObservables", value):  # noqa D103
        super().__set__(instance, value)
        instance.notify(
            self.public_name,
            getattr(instance, self.private_name, self.fallback_value),
            value,
            "on_change",
        )
        setattr(instance, self.private_name, value)


class Computable(BaseObservable):
    """A Computable that is depended on one or more Observables.

    fixme how to make this work with Descriptors?
     just to it as with ObservableList and SingalingList
     so have a Computable and Computed class
     declare the Computable at the top
     assign the Computed in the instance

    """

    def __init__(self):
        """Initialize a Computable."""
        super().__init__()
        self.public_name: str
        self.private_name: str

        self.signal_types: set = {"on_change"}

    def __get__(self, instance, owner):
        computed = getattr(instance, self.private_name)

        old_value = computed.value
        new_value = computed()

        if new_value != old_value:
            instance.notify(
                self.public_name,
                old_value,
                new_value,
                "on_change",
            )
        else:
            return new_value

    def __set_name__(self, owner: "HasObservables", name: str):
        self.public_name = name
        self.private_name = f"_{name}"
        owner.register_observable(self)

    def __set__(self, instance: "HasObservables", value):
        setattr(instance, self.private_name, Computed(*value))


class Computed:
    def __init__(self, callable: Callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self._is_dirty = False
        self.value = None

        # fixme this is not correct, our HasObservable might have disappeared....
        #  so we need to use weakrefs here.
        self.parents: weakref.WeakKeyDictionary[HasObservables, dict[str], Any] = weakref.WeakKeyDictionary()

    def _set_dirty(self, signal):
        self._is_dirty = True
        # propagate this to all dependents

    def _add_parent(self, parent: "HasObservables", name: str, current_value: Any):
        """Add a parent Observable.

        Args:
            parent: the HasObservable instance to which the Observable belongs
            name: the public name of the Observable
            current_value: the current value of the Observable

        """
        parent.observe(name, All(), self._set_dirty)

        try:
            self.parents[parent][name] = current_value
        except KeyError:
            self.parents[parent] = {name: current_value}

    def _remove_parents(self):
        """Remove all parent Observables."""
        # we can ubsubscribe from everything on each parent
        for parent in self.parents:
            parent.unobserve(All(), All())

    def __call__(self):
        global CURRENT_COMPUTED  # noqa: PLW0603
        CURRENT_COMPUTED = self

        if self._is_dirty:
            changed = False

            # we might be dirty but values might have changed
            # back and forth in our parents so let's check to make sure we
            # really need to recalculate
            for parent in self.parents.keyrefs():
                # does parent still exist?
                if parent := parent():
                    # if yes, compare old and new values for all
                    # tracked observables on this parent
                    for name, old_value in self.parents[parent].items():
                        new_value = getattr(parent, name)
                        if new_value != old_value:
                            changed = True
                            break  # we need to recalculate
                    else:
                        # trick for breaking cleanly out of nested for loops
                        # see https://stackoverflow.com/questions/653509/breaking-out-of-nested-loops
                        continue
                    break
                else:
                    # one of our parents no longer exists
                    changed = True
                    break

            if changed:
                # the dependencies of the computable function might have changed
                # so we rebuilt
                self._remove_parents()

                old = CURRENT_COMPUTED
                CURRENT_COMPUTED = self

                try:
                    # fixme we need to handle error propagation somehow correctly
                    self._value = self.callable(*self.args, **self.kwargs)
                except Exception as e:
                    raise e
                finally:
                    CURRENT_COMPUTED = old

            self._is_dirty = False
        return self.value


class All:
    """Helper constant to subscribe to all Observables."""

    def __init__(self):
        self.name = "all"

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

    @classmethod
    def register_observable(cls, observable: BaseObservable):
        """Register an Observable.

        Args:
            observable: the Observable to register

        """
        cls.observables[observable.public_name] = observable

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
