"""A signals implementation for Python based on @preact/signals."""

from __future__ import annotations

import typing
import weakref

__all__ = ["Signal", "batch", "computed", "effect"]

Disposer = typing.Callable[[], None]
Listener = typing.Callable[[], None]

# current computed that is running
CURRENT_COMPUTED: Computed | None = None

# a set of listeners which will be triggered after the batch is complete
BATCH_PENDING: set[Listener] | None = None

PROCESSING_SIGNALS: set[Signal] = set()

T = typing.TypeVar("T")


def batch(fn: typing.Callable[[], T]) -> T:
    """Combine multiple updates into one "commit" at the end of the provided callback.

    Batches can be nested, and changes are only flushed once the outermost batch
    callback completes. Accessing a signal that has been modified within a batch
    will reflect its updated value.

    Parameters
    ----------
    fn : Callable[[], T]
        The callback function to execute within the batch.

    Returns:
    -------
    T
        The value returned by the callback function.
    """
    global BATCH_PENDING  # noqa: PLW0603

    if BATCH_PENDING is None:
        listeners = set()
        old = BATCH_PENDING
        BATCH_PENDING = listeners

        try:
            return fn()
        finally:
            BATCH_PENDING = old
            PROCESSING_SIGNALS.clear()

            # trigger any pending listeners
            for listener in listeners:
                listener()
    else:
        return fn()


class Signal(typing.Generic[T]):
    """Represents a signal that can be subscribed to for changes in value."""

    __slots__ = ["__weakref__", "_children", "_value"]

    _value: T

    # Uses weak references to avoid memory leaks
    # If the child is not used anywhere, then it can be garbage collected
    _children: set[weakref.ref[Signal]]

    def __init__(self, value: T) -> None:
        self._value = value
        self._children = set()

    def __call__(self) -> T:
        """Get the current value of the signal."""
        return self.get()

    # def __str__(self) -> str:
    #     return f"{self()}"

    # def __repr__(self) -> str:
    #     return f"Signal({self()})"

    # Recurse down all children, marking them as diry and adding
    # listeners to batch_pending
    def _wakeup(self):
        to_remove = set()
        for child_ref in self._children:
            child = child_ref()
            if child is not None:
                child._wakeup()
            else:
                to_remove.add(child_ref)

        for child_ref in to_remove:
            # If the child has been garbage collected, remove it from the set
            self._children.remove(child_ref)

    def peek(self):
        """Get the current value of the signal without subscribing to changes."""
        return self._value

    def get(self) -> T:
        """Get the current value of the signal."""
        value = self._value
        if CURRENT_COMPUTED is not None:
            # this is ued to detect infinite cycles
            if BATCH_PENDING is not None:
                PROCESSING_SIGNALS.add(self)

            # if accessing inside of a computed, add this to the computed's parents
            CURRENT_COMPUTED._add_dependency(self, value)

        return value

    def set(self, value: T) -> None:
        if (
            CURRENT_COMPUTED is not None
            and BATCH_PENDING is not None
            and self in PROCESSING_SIGNALS
        ):
            raise RuntimeError("Cycle detected")

        self._value = value

        # If the value is set outside of a batch, this ensures that all of the
        # children will be fully marked as dirty before triggering any listeners
        batch(self._wakeup)

    def subscribe(
        self, fn: typing.Callable[[T], typing.Any]
    ) -> typing.Callable[[], None]:
        """Subscribe to changes in the signal.

        Parameters
        ----------
        fn : Callable[[T], None]
            The callback function to run when the signal changes.

        Returns:
        -------
        Callable[[], None]
            A function for unsubscribing from the signal.
        """
        return effect(lambda: fn(self()))


class Computed(Signal[T]):
    """Represents a signal whose value is derived from other signals."""

    __slots__ = ["_callback", "_dirty", "_first", "_has_error", "_parents", "_weak"]

    # Whether this is the first time processing the computed
    _first: bool

    # Whether any of the computed's parents have changed or not
    _dirty: bool

    # Whether the callback errored or not
    _has_error: bool

    # Weakrefs has their own object identity, so we must reuse the same weakref
    # over and over again
    _weak: weakref.ref[Signal | Computed]

    # The parent dependencies of this computed.
    _parents: dict[Signal, typing.Any]

    _callback: typing.Callable[[], T]

    def __init__(self, callback: typing.Callable[[], T]) -> None:
        super().__init__(typing.cast(T, None))
        self._first = True
        self._dirty = True
        self._has_error = False
        self._weak = weakref.ref(self)
        self._parents = {}
        self._callback = callback

    def __call__(self) -> T:
        return self.get()

    def _wakeup(self):
        """Mark this computed as dirty whenever any of its parents change."""
        self._dirty = True
        super()._wakeup()

    def _add_dependency(self, parent: Signal, value: typing.Any) -> None:
        """Add the Signal as a dependency of this computed.

        Called when another Signal's .value is accessed inside of this computed.
        """
        self._parents[parent] = value
        parent._children.add(self._weak)

    def _remove_dependencies(self):
        """Remove all links between this computed and its dependencies."""
        for parent in self._parents:
            parent._children.remove(self._weak)

    def peek(self) -> T:
        global CURRENT_COMPUTED  # noqa: PLW0603

        if self._dirty:
            try:
                changed = False
                if self._first:
                    self._first = False
                    changed = True
                else:
                    for parent, old_value in self._parents.items():
                        new_value = parent.peek()
                        if old_value != new_value:
                            changed = True

                if changed:
                    self._has_error = False
                    # Because the dependencies might have changed, we first
                    # remove all of the old links between this computed and
                    # its dependencies.
                    #
                    # The links will be recreated by the _addDependency method.
                    self._remove_dependencies()

                    old = CURRENT_COMPUTED
                    CURRENT_COMPUTED = self

                    try:
                        self._value = self._callback()
                    finally:
                        CURRENT_COMPUTED = old
            except Exception as e:
                self._has_error = True
                # We reuse the _value slot for the error, instead of using
                # a separate property
                self._value = typing.cast(T, e)

        if self._has_error:
            # We know that the value is an exception
            raise self._value

        return self._value

    def get(self) -> T:
        """Get the current value of the computed."""
        value = self.peek()

        if CURRENT_COMPUTED is not None:
            # If accessing inside of a computed, add this to the computed's parents
            CURRENT_COMPUTED._add_dependency(self, value)

        return value

    def set(self, value: T) -> None:
        raise AttributeError("Computed singals are read-only")

    # def __repr__(self) -> str:
    #     return f"Computed({self()})"


def computed(fn: typing.Callable[[], T]) -> Computed[T]:
    """Create a new signal that is computed based on the values of other signals.

    The returned computed signal is read-only, and its value is automatically
    updated when any signals accessed from within the callback function change.

    Parameters
    ----------
    fn : Callable[[], T]
        The function to compute the value of the signal.

    Returns:
    -------
    Computed[T]
        A new read-only signal.
    """
    return Computed(fn)


class Effect(Computed[T]):
    """Represents a side-effect that runs in response to signal changes."""

    __slots__ = ["_listener"]

    _listener: Listener | None

    def __init__(self, fn: typing.Callable[[], T]) -> None:
        self._listener = None
        super().__init__(fn)

    def __repr__(self) -> str:
        return f"Effect({self()})"

    def _wakeup(self):
        """Mark this effect as dirty whenever any of its parents change."""
        if BATCH_PENDING is None:
            raise RuntimeError("invalid batch_pending")

        if self._listener is not None:
            BATCH_PENDING.add(self._listener)

        super()._wakeup()

    def _listen(self, callback: typing.Callable[[T], None]) -> Disposer:
        old_value = self()

        def listener():
            nonlocal old_value
            new_value = self()
            if old_value != new_value:
                old_value = new_value
                callback(old_value)

        self._listener = listener
        callback(old_value)

        def dispose():
            self._listener = None
            self._remove_dependencies()

        return dispose


def _effect(fn: typing.Callable[[], None]) -> Disposer:
    """Create an effect to run arbitrary code in response to signal changes.

    An effect tracks which signals are accessed within the given callback
    function `fn`, and re-runs the callback when those signals change.

    The callback may return a cleanup function. The cleanup function gets
    run once, either when the callback is next called or when the effect
    gets disposed, whichever happens first.

    Parameters
    ----------
    fn : Callable[[], None]
        The effect callback.

    Returns:
    -------
    Callable[[], None]
        A function for disposing the effect.
    """
    return Effect(lambda: batch(fn))._listen(lambda _: None)


@typing.overload
def effect(  # noqa: D418
    deps: typing.Sequence[Signal],
    *,
    defer: bool = False,
) -> typing.Callable[[typing.Callable[..., None]], Disposer]:
    """Create an effect with explicit dependencies.

    An effect is a side-effect that runs in response to signal changes.

    Parameters
    ----------
    deps : Sequence[Signal]
        The signals that the effect depends on.

    defer : bool, optional
        Defer the effect until the next change, rather than running immediately.
        By default, False.

    Returns:
    -------
    Callable[[Callable[..., None]], Disposer]
        A decorator function for creating effects.
    """


@typing.overload
def effect(fn: typing.Callable[[], None], /) -> Disposer:  # noqa: D418
    """Create an effect to run arbitrary code in response to signal changes.

    An effect tracks which signals are accessed within the given callback
    function `fn`, and re-runs the callback when those signals change.

    The callback may return a cleanup function. The cleanup function gets
    run once, either when the callback is next called or when the effect
    gets disposed, whichever happens first.

    Parameters
    ----------
    fn : Callable[[], None]
        The effect callback.

    Returns:
    -------
    Callable[[], None]
        A function for disposing the effect.
    """


def effect(*args, **kwargs) -> typing.Callable:
    """Create an effect to run arbitrary code in response to signal changes."""
    if len(args) == 1 and callable(args[0]):
        return _effect(args[0])

    deps = args[0] if len(args) == 1 else kwargs.get("deps", [])
    defer = kwargs.get("defer", False)

    def wrap(fn):
        return _effect(on(deps=deps, defer=defer)(fn))

    return wrap


def on(deps: typing.Sequence[Signal], *, defer: bool = False):
    """Make dependencies for a function explicit.

    Parameters
    ----------
    deps : Sequence[Signal]
        The signals that the effect depends on.

    defer : bool, optional
        Defer the effect until the next change, rather than running immediately.
        By default, False.

    Returns:
    -------
    Callable[[Callable[..., None]], Callable[[], None]]
        A callback function that can be registered as an effect.
    """

    def decorator(fn: typing.Callable[..., None]) -> typing.Callable[[], None]:
        # The main effect function that will be run.
        def main():
            return fn(*(dep() for dep in deps))

        func = main

        if defer:
            # Create a void function that accesses all of the
            # dependencies so they will be tracked in an effect.
            def void():
                nonlocal func
                for dep in deps:
                    dep()
                func = main

            func = void

        return lambda: func()

    return decorator
