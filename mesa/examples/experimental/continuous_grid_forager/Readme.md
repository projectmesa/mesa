# Continuous Grid Forager

## Summary

This small model demonstrates the manual workflow of moving an agent through
continuous space and looking up the discrete grid cell under its position. The
forager harvests a limited amount of the cell's `resource` property each step.

The forager subclasses `ContinuousSpaceAgent` only. After moving, it calls
`grid.find_nearest_cell(self.position)` and interacts with the returned cell.
Finding a cell this way does not add the forager to `cell.agents` or synchronize
discrete-space membership. The grid is used here for cell lookup and resource
properties, not as an agent container for the forager.

## Boundary policy

Both spaces are toroidal. The forager wraps its next position with modulo before
assigning it, keeping coordinates in `[0, width) x [0, height)`. This avoids
passing a maximum-edge coordinate to the grid lookup.

## Run

From the repository root, run:

```console
python -m mesa.examples.experimental.continuous_grid_forager.model
```

The deterministic run starts in cell `(0, 0)`, moves into `(1, 0)`, and harvests
that cell's resource. It then continues across the row. The resource array is
initialized with distinct values so the affected cell is easy to identify.

## Files

- `agents.py`: Continuous forager movement and cell-property interaction.
- `model.py`: Scenario, continuous space, grid, resource layer, and runnable demo.
