from _core import Computed, Signal

a = Signal(2)
b = Signal(3)

c = Computed(lambda: a() + b())

c()
a.set(5)
