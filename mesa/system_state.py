import functools
from weakref import finalize


def accessor_method(column_name, self):
    return {k: v.value for k, v in self.columnsdict[column_name].items()}


class SystemState:
    # in principle are all columns knowable upfront
    # they are declared as part of the class definition
    # so __set_name__ could be used to register them as
    # column labels as well

    def __init__(self):
        self.rowsdict = {}
        self.columnsdict = {}
        self.datadict = {}

    def get_column(self, column_label):
        return self.columnsdict[column_label]

    def get_row(self, row_label):
        return self.rowsdict[row_label]

    def get_field(self, row_label, column_label):
        try:
            return self.datadict[(row_label, column_label)]
        except KeyError:
            return self._add_field(row_label, column_label)


    def _add_field(self, row_label, column_label):

        if row_label not in self.rowsdict:
            self.rowsdict[row_label] = {}

        if column_label not in self.columnsdict:
            self.columnsdict[column_label] = {}

            # nerdy trick to allow attribute access to columns
            # while returns the values of the fields instead the fields
            # itself.
            m = functools.partial(accessor_method, column_label)
            setattr(SystemState, column_label, property(fget=m))

        field = Field()
        self.rowsdict[row_label][column_label] = field
        self.columnsdict[column_label][row_label] = field
        self.datadict[(row_label, column_label)] = field
        return field

    def remove_row(self, row_label):
        row = self.rowsdict.pop(row_label)
        for column_label in row:
            try:
                del self.columnsdict[row_label][column_label]
                del self.datadict[(row_label, column_label)]
            except KeyError:
                pass

    def remove_column(self, column_label):
        column = self.columnsdict.pop(column_label)
        for row_label in column:
            del self.rowsdict[row_label][column_label]
            del self.datadict[(row_label, column_label)]

class Field:
    def __init__(self):
        self.value = None


class State:

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        self.private_field = f"_{name}_field"


def remover(key, system_state):
    system_state.remove_row(key)


class AgentState(State):
    def __set__(self, instance, value):
        key = instance.unique_id

        try:
            field = getattr(instance, self.private_field)
        except AttributeError:
            system_state = instance.model.system_state
            field = system_state.get_field(key, self.public_name)
            setattr(instance, self.private_field, field)

            if not hasattr(instance, "_finalizer_set"):
                finalize(instance, remover, instance.unique_id, system_state)
                instance._finalizer_set = True

        field.value = value
        setattr(instance, self.private_name, value)


class ModelState(State):
    def __set__(self, instance, value):
        key = "model"

        try:
            field = getattr(instance, self.private_field)
        except AttributeError:
            system_state = instance.system_state
            field = system_state.get_field(key, self.public_name)
            setattr(instance, self.private_field, field)

        field.value = value
        setattr(instance, self.private_name, value)
