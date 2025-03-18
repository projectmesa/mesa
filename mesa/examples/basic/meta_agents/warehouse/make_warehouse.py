import random
import string

import numpy as np

# Constants
DEFAULT_ROWS = 22
DEFAULT_COLS = 20
DEFAULT_HEIGHT = 4
LOADING_DOCK_COORDS = [(0, i, 0) for i in range(0, 10, 2)]
CHARGING_STATION_COORDS = [(21, i, 0) for i in range(19, 10, -2)]


def generate_item_code() -> str:
    """Generate a random item code (1 letter + 2 numbers)."""
    letter = random.choice(string.ascii_uppercase)
    number = random.randint(10, 99)
    return f"{letter}{number}"


def make_warehouse(
    rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS, height: int = DEFAULT_HEIGHT
) -> np.ndarray:
    """
    Generate a warehouse layout with designated LD, CS, and storage rows as a NumPy array.

    Args:
        rows (int): Number of rows in the warehouse.
        cols (int): Number of columns in the warehouse.
        height (int): Number of levels in the warehouse.

    Returns:
        np.ndarray: A 3D NumPy array representing the warehouse layout.
    """
    # Initialize empty warehouse layout
    warehouse = np.full((rows, cols, height), "  ", dtype=object)

    # Place Loading Docks (LD)
    for r, c, h in LOADING_DOCK_COORDS:
        warehouse[r, c, h] = "LD"

    # Place Charging Stations (CS)
    for r, c, h in CHARGING_STATION_COORDS:
        warehouse[r, c, h] = "CS"

    # Fill storage rows with item codes
    for r in range(3, rows - 2, 3):  # Skip row 0,1,2 (LD) and row 17,18,19 (CS)
        for c in range(2, cols, 3):  # Leave 2 spaces between each item row
            for h in range(height):
                warehouse[r, c, h] = generate_item_code()

    return warehouse
