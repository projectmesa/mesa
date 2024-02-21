# How-to Guide

This guide provides concise instructions and examples to help you start with common tasks in Mesa.

## Models with Discrete Time

For models involving agents of multiple types, including those with a time attribute, you can construct a discrete-time model. This setup allows each agent to perform actions in steps that correspond to the model's discrete time.

Example:
```python
if self.model.schedule.time in self.discrete_time:
    self.model.space.move_agent(self, new_pos)
```

## Implementing Model-Level Functions with Staged Activation

In staged activation scenarios, to designate functions that should only operate
at the model level (and not at the agent level), prepend the function name with
"model." in the function list definition. This approach is useful for
model-wide operations, like adjusting a wage rate based on demand.

Example:
```python
stage_list = [Send_Labour_Supply, Send_Labour_Demand, model.Adjust_Wage_Rate]
self.schedule = StagedActivation(self, stage_list, shuffle=True)
```

## Using `numpy.random`

To incorporate `numpy`'s random functions, such as for generating a Poisson
distribution, initialize a random number generator in your model's constructor.

Example:
```python
import mesa
import numpy as np

class MyModel(mesa.Model):
    def __init__(self, seed=None):
        super().__init__()
        self.random = np.random.default_rng(seed)
```

Usage example:
```python
lambda_value = 5
sample = self.random.poisson(lambda_value)
```

## Multi-process `batch_run` on Windows

When using `batch_run` with `number_processes = None` on Windows, you might
encounter progress display issues or `AttributeError: Can't get attribute
'MoneyModel' on <module '__main__' (built-in)>`. To resolve this, run
your code outside of Jupyter notebooks and use the following pattern,
incorporating `freeze_support()` for multiprocessing support.

Example:
```python
from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

params = {"width": 10, "height": 10, "N": range(10, 500, 10)}

if __name__ == '__main__':
    freeze_support()
    results = batch_run(
        MoneyModel,
        parameters=params,
        iterations=5,
        max_steps=100,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )
```

If you would still like to run your code in Jupyter, adjust your code as
described and consider integrating external libraries like
[nbmultitask](https://nbviewer.org/github/micahscopes/nbmultitask/blob/39b6f31b047e8a51a0fcb5c93ae4572684f877ce/examples.ipynb)
or refer to [Stack
Overflow](https://stackoverflow.com/questions/50937362/multiprocessing-on-python-3-jupyter)
for multiprocessing tips.
