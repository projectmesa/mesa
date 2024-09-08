# import solara
# from solara import Reactive
#
# class Observable:
#
#     def __init__(self, dtype):
#         self.dtype = dtype
#
#     def __get__(self, instance, owner):
#         return getattr(instance, self.private_name)
#
#     def __set_name__(self, owner, name):
#         self.public_name = name
#         self.private_name = f"_{name}"
#         self.message_name = f"{name.upper()}_CHANGE"
#
#         # dynamically add relevant Signal
#         mt = psygnal.Signal(self.dtype)
#         mt.__set_name__(type(owner), self.message_name)
#         setattr(owner, self.message_name, mt)
#
#     def __set__(self, instance, value):
#         setattr(instance, self.private_name, value)
#
#         a = getattr(instance, self.message_name)
#         a.emit(value, check_types=True)
#
#
# if __name__ == '__main__':
#
#     class A:
#         a = solara.Reactive(5)
#
#
#     a = A()
#     print(a.a)
#     repr(a.a)
import solara