import contextlib
from collections import defaultdict
from typing import Callable


class MessageType:
    # FIXME should there be only one instance for each name?
    # Should we dynamically create a class for each message type?
    # at least we should have some way to validate a message

    message_types = defaultdict(list)

    def __init__(self, message_fields: str | list[str] | None = None) -> None:
        if isinstance(message_fields, str):
            message_fields = [message_fields, ]
        self.message_fields: set[str] = set(message_fields)
        self.name: str | None = None
        self.defining_class: type | None = None

    def __set_name__(self, defining_class: type, name: str) -> None:
        self.defining_class = defining_class
        self.name = name

        type(self).message_types[name].append(defining_class)


class Message:
    def __init__(self, message_type: MessageType, sender, **kwargs):
        if not self.validate_content(message_type, kwargs):
            raise ValueError(f"message fields not correct for message type {message_type.name}"
                             f"expected {message_type.message_fields} but got {set(kwargs.keys())}")

        self.message_type = message_type
        self.sender = sender
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def validate_content(message_type, content):
        return set(content.keys()) == message_type.message_fields


class MessageProducer:

    def __init__(self, owner):
        self.subscribers = defaultdict(list)
        self.owner = owner

    def subscribe(self, message_type: [MessageType], event_handler: Callable):
        self.subscribers[message_type].append(event_handler)

    def unsubscribe(self, message_type: MessageType, event_handler: Callable):
        # FIXME how to deal with same eventtype defined on multiple classes?
        # or try except pass, which is slightly faster
        with contextlib.suppress(ValueError):
            self.subscribers[message_type].remove(event_handler)

    def send_message(self, message_type: MessageType, **kwargs):
        """send message of message type and with content in keyword arguments to all subscribers"""

        # copy is needed here because the handling of the event
        # might result in the receiver unsubscribing itself, causing a change
        # in the dict while iterating over it.
        message = Message(message_type, self.owner, **kwargs)

        for entry in self.subscribers[message_type].copy():
            entry(message)


class ObservableState:
    # observable is a descriptor that can be used on
    # objects to declare specific attributes as observable (i.e., they fire events)


    #TODO:: auto add the relevant {name}_state_change message to the class
    #TODO:: this allows for subscribing to specific state changes instead of subscribing to all

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        self.message_name = f"{name.upper()}_CHANGE"

        # dynamically add relevant MessageType to class
        mt = MessageType(message_fields=["attr_name", "value"])
        mt.__set_name__(type(owner), self.message_name)
        setattr(owner, self.message_name, mt)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)
        instance.event_producer.send_message(getattr(instance, self.message_name), attr_name=self.public_name,
                                             value=value)

if __name__ == '__main__':
    class A:
        a = ObservableState()

    a = A()
    print(a)