import psygnal


class Observable:
    def __init__(self, dtype, check_types=False):
        self.dtype = dtype
        self.check_types: bool = check_types
        self.public_name: str
        self.private_name: str
        self.signal_name: str

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        self.signal_name = f"{name}_changed"

        # dynamically add relevant Signal
        signal = psygnal.Signal(self.dtype)
        signal.__set_name__(type(owner), self.signal_name)
        setattr(owner, self.signal_name, signal)
        setattr(owner, self.private_name, None)
        owner.observables.append(self)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)

        signal_instance = getattr(instance, self.signal_name)
        signal_instance.emit(value, check_types=self.check_types)


# class ObservableCollection:
#     def __init__(self, dtype):
#         self.dtype = dtype
#
#     def __get__(self, instance, owner):
#         return getattr(instance, self.private_name)
#
#     def __set_name__(self, owner, name):
#         self.public_name = name
#         self.private_name = f"_{name}"
#         self.message_name = f"{name}_changed"
#
#         # dynamically add relevant Signal
#         # mt = psygnal.Signal(self.dtype)
#         # mt.__set_name__(type(owner), self.message_name)
#         # setattr(owner, self.message_name, mt)
#         setattr(owner, self.private_name, EventedList())
#
#     def __set__(self, instance, value):
#         # can we play a trick here similar to signal and signal instance
#         # basically you can call set only once?
#         # or check value and if empy container, just reset container?
#
#
#         setattr(instance, self.private_name, value)
#
#         a = getattr(instance, self.message_name)
#         a.emit(value, check_types=True)


class MesaSignalGroup(psygnal.SignalGroup):
    """Mesa specific subclass fo psygnal.SignalGroup"""

    def __init__(self, signals, owner):
        # add all container signals in the appropriate way here

        self._psygnal_instances = signals
        self._psygnal_relay = psygnal._group.SignalRelay(self._psygnal_instances, owner)


def _defined_signals_generator(obj):
    fields = [entry for entry in dir(obj) if not entry.startswith("__")]
    for field in fields:
        try:
            if isinstance(instance := getattr(obj, field), psygnal.SignalInstance):
                yield field, instance
        except AttributeError:
            # properties might not have their "protected" attribute set yet because this
            # happens during __init__
            continue


if __name__ == "__main__":
    from mesa import Agent, Model

    class A(Agent):
        a = Observable(int)

    class B(A):
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
