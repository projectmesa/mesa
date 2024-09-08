import psygnal


class Observable:

    def __init__(self, dtype):
        self.dtype = dtype

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        self.message_name = f"{name.upper()}_CHANGE"

        # dynamically add relevant Signal
        mt = psygnal.Signal(self.dtype)
        mt.__set_name__(type(owner), self.message_name)
        setattr(owner, self.message_name, mt)
        setattr(owner, self.private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)

        a = getattr(instance, self.message_name)
        a.emit(value, check_types=True)


class MesaSignalGroup(psygnal.SignalGroup):
    """Mesa specific subclass fo psygnal.SignalGroup"""

    def __init__(self, signals, owner):
        self._psygnal_instances = signals
        self._psygnal_relay = psygnal._group.SignalRelay(self._psygnal_instances, owner)


class Test:
    signals: MesaSignalGroup

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        # collect defined Signals to create a signal group
        signals = {k: v for k, v in _defined_signals_generator(obj)}
        setattr(obj, "signals", MesaSignalGroup(signals, obj))

        return obj


def _defined_signals_generator(obj):
    fields = [entry for entry in dir(obj) if not entry.startswith("__")]
    for field in fields:
        if isinstance(instance := getattr(obj, field), psygnal.SignalInstance):
            yield field, instance


if __name__ == '__main__':
    class A(Test):
        a = Observable(int)


    class B(A):
        b = Observable(int)


    a = A()
    b = B()


    def some_handler(arg: int):
        print(f"other handler {arg}")


    a.A_CHANGE.connect(some_handler)
    b.signals.connect(some_handler)
    b.signals.all.connect(some_handler)

    print(b.signals["A_CHANGE"] == b.A_CHANGE)

    a.a = 5
    b.a = 6
    b.b = 7
