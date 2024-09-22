
from _core import Signal, Computed

a = Signal(2)
b = Signal(3)

c = Computed(lambda: a() + b())

c()
a.set(5)