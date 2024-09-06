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

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)

        a = getattr(instance, self.message_name)
        a.emit(value, check_types=True)


if __name__ == '__main__':
    class A:
        a = Observable(int)

    a = A()


    @a.A_CHANGE.connect
    def some_handler(*args, **kwargs):
        print(*args, **kwargs)

    def some_other_handler(arg:int):
        print(f"other handler {arg}")


    a.A_CHANGE.connect(some_other_handler)

    a.a = 5
    a.a = 5.5

