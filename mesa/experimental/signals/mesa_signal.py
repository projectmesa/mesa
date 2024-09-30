"""Core classes for Observables."""

from __future__ import annotations

import contextlib
import functools
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from collections.abc import Callable
from typing import Any

from mesa.experimental.signals.signals_util import create_weakref

__all__ = ["Observable", "HasObservables", "All", "Computable"]

_hashable_signal = namedtuple("_HashableSignal", "instance name")

CURRENT_COMPUTED: Computed | None = None  # the current Computed that is evaluating
PROCESSING_SIGNALS: set[tuple[str,]] = set()


class BaseObservable(ABC):
    """Abstract base class for all Observables."""

    @abstractmethod
    def __init__(self, fallback_value=None):
        """Initialize a BaseObservable."""
        super().__init__()
        self.public_name: str
        self.private_name: str

        # fixme can we make this an innerclass enum?
        #  or some SignalTypes helper class?
        #  its even more complicated. Ideally you can define
        #  signal_types throughout the class hierarchy and they are just
        #  combined together.
        self.signal_types: set = set()
        self.fallback_value = fallback_value

    def __get__(self, instance: HasObservables, owner):
        value = getattr(instance, self.private_name)

        if CURRENT_COMPUTED is not None:
            # there is a computed dependent on this Observable, so let's add
            # this Observable as a parent
            CURRENT_COMPUTED._add_parent(instance, self.public_name, value)

            # fixme, this can be done more cleanly
            #  problem here is that we cannot use self (i.e., the observable), we need to add the instance as well
            PROCESSING_SIGNALS.add(_hashable_signal(instance, self.public_name))

        return value

    def __set_name__(self, owner: HasObservables, name: str):
        self.public_name = name
        self.private_name = f"_{name}"
        # owner.register_observable(self)

    @abstractmethod
    def __set__(self, instance: HasObservables, value):
        # this only emits an on change signal, subclasses need to specify
        # this in more detail
        instance.notify(
            self.public_name,
            getattr(instance, self.private_name, self.fallback_value),
            value,
            "on_change",
        )

    def __str__(self):
        return f"{self.__class__.__name__}: {self.public_name}"


class Observable(BaseObservable):
    """Observable class."""

    # fixme, cycles
    # fixme, how do we "traverse" the tree
    #  do we go by layer, or by branch? it seems signals goes by layer with its batch construction

    def __init__(self, fallback_value=None):
        """Initialize an Observable."""
        super().__init__(fallback_value=fallback_value)

        # fixme can we make this an innerclass enum?
        #  or some SignalTypes helper class?
        self.signal_types: set = {
            "on_change",
        }

    def __set__(self, instance: HasObservables, value):  # noqa D103
        if (
            CURRENT_COMPUTED is not None
            and _hashable_signal(instance, self.public_name) in PROCESSING_SIGNALS
        ):
            raise ValueError(
                f"cyclical dependency detected: Computed({CURRENT_COMPUTED.name}) tries to change "
                f"{instance.__class__.__name__}.{self.public_name} while also being dependent it"
            )

        setattr(instance, self.private_name, value)

        super().__set__(instance, value)  # send the notify

        PROCESSING_SIGNALS.clear()  # we have notified our children, so we can clear this out


class Computable(BaseObservable):
    """A Computable that is depended on one or more Observables.

    .. code-block:: python

       class MyAgent(Agent):
           wealth = Computable()

           def __init__(self, model):
                super().__init__(model)
                wealth = Computed(func, args, kwargs)

    """

    def __init__(self):
        """Initialize a Computable."""
        super().__init__()
        self.public_name: str
        self.private_name: str

        self.signal_types: set = {"on_change"}

    def __get__(self, instance, owner):  # noqa: D105
        computed = getattr(instance, self.private_name)
        old_value = computed._value

        # fixme, we are not detecting if one computable is dependent on another
        if CURRENT_COMPUTED is not None:
            CURRENT_COMPUTED._add_parent(instance, self.public_name, old_value)

        new_value = computed()

        if new_value != old_value:
            instance.notify(
                self.public_name,
                old_value,
                new_value,
                "on_change",
            )
            return new_value
        else:
            return old_value

    def __set__(self, instance: HasObservables, value):  # noqa D103
        # no on change event?
        setattr(instance, self.private_name, value)
        value.name = self.public_name
        value.owner = instance


class Computed:
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_dirty = True
        self._first = True
        self._value = None
        self.name: str = ""  # set by Computable
        self.owner: HasObservables  # set by Computable

        self.parents: weakref.WeakKeyDictionary[HasObservables, dict[str, Any]] = (
            weakref.WeakKeyDictionary()
        )

    def __str__(self):
        return f"COMPUTED: {self.name}"

    def _set_dirty(self, signal):
        self._is_dirty = True
        # fixme propagate this to all dependents

    def _add_parent(
        self, parent: HasObservables, name: str, current_value: Any
    ) -> None:
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
        # we can unsubscribe from everything on each parent
        for parent in self.parents:
            parent.unobserve(All(), All())

    def __call__(self):
        global CURRENT_COMPUTED  # noqa: PLW0603

        if self._is_dirty:
            changed = False

            if self._first:
                # fixme might be a cleaner solution for this
                #  basicaly, we have no parents.
                changed = True
                self._first = False

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
                # so, we rebuilt
                self._remove_parents()

                old = CURRENT_COMPUTED
                CURRENT_COMPUTED = self

                try:
                    self._value = self.func(*self.args, **self.kwargs)
                except Exception as e:
                    raise e
                finally:
                    CURRENT_COMPUTED = old

            self._is_dirty = False

        return self._value


class All:
    """Helper constant to subscribe to all Observables."""

    def __init__(self):  # noqa: D107
        self.name = "all"

    def __copy__(self):  # noqa: D105
        return self

    def __deepcopy__(self, memo):  # noqa: D105
        return self


Signal = namedtuple("Signal", "owner observable old_value new_value signal_type")


class HasObservables:
    """HasObservables class."""

    # we can't use a weakset here because it does not handle bound methods correctly
    # also, a list is faster for our use case
    subscribers: dict[str, dict[str, list]]
    observables: dict[str, BaseObservable]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a HasObservables."""
        super().__init__(*args, **kwargs)
        self.subscribers = defaultdict(functools.partial(defaultdict, list))
        self.observables = dict(descriptor_generator(self))

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

        # fixme, see unsubscribe, but event types differ across names
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

        for name in names:
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

            ref = create_weakref(handler)
            for signal_type in signal_types:
                self.subscribers[name][signal_type].append(ref)

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

        for name in names:
            # we need to do this here because signal types might
            # differ for name so for each name we need to check
            if isinstance(signal_type, All):
                signal_types = self.observables[name].signal_types
            else:
                signal_types = [
                    signal_type,
                ]
            for signal_type in signal_types:
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

        # because we are using a list of subscribers
        # we should update this list to subscribers that are still alive
        observers = self.subscribers[observable][signal_type]
        active_observers = []
        for observer in observers:
            if active_observer := observer():
                active_observer(signal)
                active_observers.append(observer)
        # use iteration to also remove inactive observers
        self.subscribers[observable][signal_type] = active_observers


def descriptor_generator(obj) -> [str, BaseObservable]:
    """Yield defined Observables on obj."""
    # we need to traverse the entire class hierarchy to properly get
    # also observables defined in super classes
    for base in type(obj).__mro__:
        base_dict = vars(base)

        for entry in base_dict.values():
            if isinstance(entry, BaseObservable):
                yield entry.public_name, entry