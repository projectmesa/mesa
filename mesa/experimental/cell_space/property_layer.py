
import inspect
import warnings
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

import numpy as np

from .cell import Cell

Coordinate = Sequence[int]
T = TypeVar("T", bound=Cell)
class PropertyLayer:
    """A class representing a layer of properties in a two-dimensional grid.

    Each cell in the grid can store a value of a specified data type.

    Attributes:
        name: The name of the property layer.
        dimensions: The width of the grid (number of columns).
        data: A NumPy array representing the grid data.

    # Fixme do we need this class at all?
    #  what does it add to just a numpy array?

    """

    propertylayer_experimental_warning_given = False

    def __init__(
        self, name: str, dimensions: Sequence[int], default_value=0.0, dtype=float
    ):
        """Initializes a new PropertyLayer instance.

        Args:
            name: The name of the property layer.
            width: The width of the grid (number of columns).
            height: The height of the grid (number of rows).
            default_value: The default value to initialize each cell in the grid. Should ideally
                           be of the same type as specified by the dtype parameter.
            dtype (data-type, optional): The desired data-type for the grid's elements. Default is float.

        Notes:
            A UserWarning is raised if the default_value is not of a type compatible with dtype.
            The dtype parameter can accept both Python data types (like bool, int or float) and NumPy data types
            (like np.int64 or np.float64). Using NumPy data types is recommended (except for bool) for better control
            over the precision and efficiency of data storage and computations, especially in cases of large data
            volumes or specialized numerical operations.
        """
        self.name = name
        self.dimensions = dimensions

        # Check if the dtype is suitable for the data
        if not isinstance(default_value, dtype):
            warnings.warn(
                f"Default value {default_value} ({type(default_value).__name__}) might not be best suitable with dtype={dtype.__name__}.",
                UserWarning,
                stacklevel=2,
            )

        # fixme why not initialize with empty?
        self.data = np.full(self.dimensions, default_value, dtype=dtype)

        if not self.__class__.propertylayer_experimental_warning_given:
            warnings.warn(
                "The property layer functionality and associated classes are experimental. It may be changed or removed in any and all future releases, including patch releases.\n"
                "We would love to hear what you think about this new feature. If you have any thoughts, share them with us here: https://github.com/projectmesa/mesa/discussions/1932",
                FutureWarning,
                stacklevel=2,
            )
            self.__class__.propertylayer_experimental_warning_given = True


    def set_cell(self, position: Coordinate, value):
        """Update a single cell's value in-place."""
        self.data[position] = value

    def set_cells(self, value, condition: Callable|None = None):
        """Perform a batch update either on the entire grid or conditionally, in-place.

        Args:
            value: The value to be used for the update.
            condition: (Optional) A callable (like a lambda function or a NumPy ufunc)
                       that returns a boolean array when applied to the data.
        """
        if condition is None:
            np.copyto(self.data, value)  # In-place update
        else:
            if isinstance(condition, np.ufunc):
                # Directly apply NumPy ufunc
                condition_result = condition(self.data)
            else:
                # Vectorize non-ufunc conditions
                vectorized_condition = np.vectorize(condition)
                condition_result = vectorized_condition(self.data)

            if (
                not isinstance(condition_result, np.ndarray)
                or condition_result.shape != self.data.shape
            ):
                raise ValueError(
                    "Result of condition must be a NumPy array with the same shape as the grid."
                )

            np.copyto(self.data, value, where=condition_result)

    def modify_cell(self, position: Coordinate, operation: Callable, value=None):
        """Modify a single cell using an operation, which can be a lambda function or a NumPy ufunc.

        If a NumPy ufunc is used, an additional value should be provided.

        Args:
            position: The grid coordinates of the cell to modify.
            operation: A function to apply. Can be a lambda function or a NumPy ufunc.
            value: The value to be used if the operation is a NumPy ufunc. Ignored for lambda functions.
        """
        current_value = self.data[position]

        # Determine if the operation is a lambda function or a NumPy ufunc
        if is_single_argument_function(operation):
            # Lambda function case
            self.data[position] = operation(current_value)
        elif value is not None:
            # NumPy ufunc case
            self.data[position] = operation(current_value, value)
        else:
            raise ValueError("Invalid operation or missing value for NumPy ufunc.")

    def modify_cells(self, operation: Callable, value=None, condition_function: Callable|None = None):
        """Modify cells using an operation, which can be a lambda function or a NumPy ufunc.

        If a NumPy ufunc is used, an additional value should be provided.

        Args:
            operation: A function to apply. Can be a lambda function or a NumPy ufunc.
            value: The value to be used if the operation is a NumPy ufunc. Ignored for lambda functions.
            condition_function: (Optional) A callable that returns a boolean array when applied to the data.
        """
        condition_array = np.ones_like(
            self.data, dtype=bool
        )  # Default condition (all cells)
        if condition_function is not None:
            if isinstance(condition_function, np.ufunc):
                condition_array = condition_function(self.data)
            else:
                vectorized_condition = np.vectorize(condition_function)
                condition_array = vectorized_condition(self.data)

        # Check if the operation is a lambda function or a NumPy ufunc
        if isinstance(operation, np.ufunc):
            if ufunc_requires_additional_input(operation):
                if value is None:
                    raise ValueError("This ufunc requires an additional input value.")
                modified_data = operation(self.data, value)
            else:
                modified_data = operation(self.data)
        else:
            # Vectorize non-ufunc operations
            vectorized_operation = np.vectorize(operation)
            modified_data = vectorized_operation(self.data)

        self.data = np.where(condition_array, modified_data, self.data)

    def select_cells(self, condition: Callable, return_list=True):
        """Find cells that meet a specified condition using NumPy's boolean indexing, in-place.

        # fixme: consider splitting into two separate functions
        #  select_cells_boolean
        #  select_cells_index

        Args:
            condition: A callable that returns a boolean array when applied to the data.
            return_list: (Optional) If True, return a list of (x, y) tuples. Otherwise, return a boolean array.

        Returns:
            A list of (x, y) tuples or a boolean array.
        """
        condition_array = condition(self.data)
        if return_list:
            return list(zip(*np.where(condition_array)))
        else:
            return condition_array

    def aggregate_property(self, operation: Callable):
        """Perform an aggregate operation (e.g., sum, mean) on a property across all cells.

        Args:
            operation: A function to apply. Can be a lambda function or a NumPy ufunc.
        """
        return operation(self.data)


class HasPropertyLayers:
    """Mixin-like class to add property layer functionality to Grids."""
    # fixme is there a way to indicate that a mixin only works with specific classes?
    def __init__(self, *args, **kwargs):
        """Initialize a HasPropertyLayers instance."""
        super().__init__(*args, **kwargs)
        self.property_layers = {}
        # Initialize an empty mask as a boolean NumPy array

        # fixme: in space.py this is a boolean mask with empty and non empty cells
        #  this does not easily translate (unless we handle it in the celll, via add and remove agents?)
        #  but then we might better treat this as a default property layer that is just allways added
        self.add_property_layer("empty", True, dtype=bool)

    def add_property_layer(
        self, name: str, default_value=0.0, dtype=float,
    ):
        """Add a property layer to the grid.

        Args:
            name: The name of the property layer.
            default_value: The default value of the property layer.
            dtype: The data type of the property layer.
        """
        # fixme, do we want to have the ability to add both predefined layers
        #  as well as just by name?

        self.property_layers[name] = PropertyLayer(name, self.dimensions, default_value=default_value, dtype=dtype)
        # fixme: this should be automagical
        # if add_to_cells:
        #     for cell in self._cells.values():
        #         cell._mesa_property_layers[property_layer.name] = property_layer

    def remove_property_layer(self, property_name: str, remove_from_cells: bool = True):
        """Remove a property layer from the grid.

        Args:
            property_name: the name of the property layer to remove
            remove_from_cells: whether to remove the property layer from all cells (default: True)
        """
        del self.property_layers[property_name]
        # fixme: this should be automagical
        # if remove_from_cells:
        #     for cell in self._cells.values():
        #         del cell._mesa_property_layers[property_name]

    def set_property(
        self, property_name: str, value, condition: Callable[[T], bool] | None = None
    ):
        """Set the value of a property for all cells in the grid.

        Args:
            property_name: the name of the property to set
            value: the value to set
            condition: a function that takes a cell and returns a boolean
        """
        self.property_layers[property_name].set_cells(value, condition)

    def modify_properties(
        self,
        property_name: str,
        operation: Callable,
        value: Any = None,
        condition: Callable[[T], bool] | None = None,
    ):
        """Modify the values of a specific property for all cells in the grid.

        Args:
            property_name: the name of the property to modify
            operation: the operation to perform
            value: the value to use in the operation
            condition: a function that takes a cell and returns a boolean (used to filter cells)
        """
        self.property_layers[property_name].modify_cells(operation, value, condition)


    def get_neighborhood_mask(
        self, pos: Coordinate, moore: bool, include_center: bool, radius: int
    ) -> np.ndarray:
        """Generate a boolean mask representing the neighborhood.

        Args:
            pos (Coordinate): Center of the neighborhood.
            moore (bool): True for Moore neighborhood, False for Von Neumann.
            include_center (bool): Include the central cell in the neighborhood.
            radius (int): The radius of the neighborhood.

        Returns:
            np.ndarray: A boolean mask representing the neighborhood.
        """
        # Fixme, should this not move into the cell?
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        mask = np.zeros((self.width, self.height), dtype=bool)

        # Convert the neighborhood list to a NumPy array and use advanced indexing
        coords = np.array(neighborhood)
        mask[coords[:, 0], coords[:, 1]] = True
        return mask

    def select_cells(
        self,
        conditions: dict | None = None,
        extreme_values: dict | None = None,
        masks: np.ndarray | list[np.ndarray] = None,
        only_empty: bool = False,
        return_list: bool = True,
    ) -> list[Coordinate] | np.ndarray:
        """Select cells based on property conditions, extreme values, and/or masks, with an option to only select empty cells.

        Args:
            conditions (dict): A dictionary where keys are property names and values are callables that return a boolean when applied.
            extreme_values (dict): A dictionary where keys are property names and values are either 'highest' or 'lowest'.
            masks (np.ndarray | list[np.ndarray], optional): A mask or list of masks to restrict the selection.
            only_empty (bool, optional): If True, only select cells that are empty. Default is False.
            return_list (bool, optional): If True, return a list of coordinates, otherwise return a mask.

        Returns:
            Union[list[Coordinate], np.ndarray]: Coordinates where conditions are satisfied or the combined mask.
        """
        # fixme: consider splitting into two separate functions
        #  select_cells_boolean
        #  select_cells_index
        #  also we might want to change the naming to avoid classes with PropertyLayer


        # Initialize the combined mask
        combined_mask = np.ones((self.width, self.height), dtype=bool)

        # Apply the masks
        if masks is not None:
            if isinstance(masks, list):
                for mask in masks:
                    combined_mask = np.logical_and(combined_mask, mask)
            else:
                combined_mask = np.logical_and(combined_mask, masks)

        # Apply the empty mask if only_empty is True
        if only_empty:
            combined_mask = np.logical_and(combined_mask, self.empty_mask)

        # Apply conditions
        if conditions:
            for prop_name, condition in conditions.items():
                prop_layer = self.property_layers[prop_name].data
                prop_mask = condition(prop_layer)
                combined_mask = np.logical_and(combined_mask, prop_mask)

        # Apply extreme values
        if extreme_values:
            for property_name, mode in extreme_values.items():
                prop_values = self.property_layers[property_name].data

                # Create a masked array using the combined_mask
                masked_values = np.ma.masked_array(prop_values, mask=~combined_mask)

                if mode == "highest":
                    target_value = masked_values.max()
                elif mode == "lowest":
                    target_value = masked_values.min()
                else:
                    raise ValueError(
                        f"Invalid mode {mode}. Choose from 'highest' or 'lowest'."
                    )

                extreme_value_mask = prop_values == target_value
                combined_mask = np.logical_and(combined_mask, extreme_value_mask)

        # Generate output
        if return_list:
            selected_cells = list(zip(*np.where(combined_mask)))
            return selected_cells
        else:
            return combined_mask


class HasProperties:
    """Mixin-like class to add property layer functionality to cells."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.properties = {}
        # do we want attribute like access to properties or not?

    def _add_property(self, name):
        pass

    def _remove_property(self):
        pass


   # PropertyLayer methods
    def get_property(self, property_name: str) -> Any:
        """Get the value of a property."""
        return self._mesa_property_layers[property_name].data[self.coordinate]

    def set_property(self, property_name: str, value: Any):
        """Set the value of a property."""
        self._mesa_property_layers[property_name].set_cell(self.coordinate, value)

    def modify_property(
        self, property_name: str, operation: Callable, value: Any = None
    ):
        """Modify the value of a property."""
        # fixme, do we want to support this?
        self._mesa_property_layers[property_name].modify_cell(
            self.coordinate, operation, value
        )


class PropertyDescriptor:
    """Descriptor for giving cells attribute like access to values defined in property layers."""

    def __init__(self, property_layer: PropertyLayer):  # noqa: D105
        self.layer = property_layer.data
    def __get__(self, instance: Cell):  # noqa: D105
        return self.layer[self.coordinate]
    def __set__(self, instance: Cell, value):  # noqa: D105
        self.layer[self.coordinate] = value
    def __set_name__(self, owner: Cell, name: str):  # noqa: D105
        self.public_name = name
        self.private_name = f"_{name}"

def is_single_argument_function(function):
    """Check if a function is a single argument function."""
    return (
        inspect.isfunction(function)
        and len(inspect.signature(function).parameters) == 1
    )

def ufunc_requires_additional_input(ufunc):  # noqa: D103
    # NumPy ufuncs have a 'nargs' attribute indicating the number of input arguments
    # For binary ufuncs (like np.add), nargs is 2
    return ufunc.nargs > 1
