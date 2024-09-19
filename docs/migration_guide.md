# Mesa Migration guide
This guide contains breaking changes between major Mesa versions and how to resolve them.

Non-breaking changes aren't included, for those see our [Release history](https://github.com/projectmesa/mesa/releases).

## Mesa 3.0
<!-- TODO small introduction-->

_This guide is a work in progress. The development of it is tracked in [Issue #2233](https://github.com/projectmesa/mesa/issues/2233)._

### Reserved and private variables
<!-- TODO: Update this section based on https://github.com/projectmesa/mesa/discussions/2230 -->

#### Reserved variables
Currently, we have reserved the following variables:
  - Model: `agents`, `current_id`, `random`, `running`, `steps`, `time`.
  - Agent: `unique_id`, `model`.

You can use (read) any reserved variable, but Mesa may update them automatically and rely on them, so modify/update at your own risk.
#### Private variables
Any variables starting with an underscore (`_`) are considered private and for Mesa's internal use. We might use any of those. Modifying or overwriting any private variable is at your own risk.

- Ref: [Discussion #2230](https://github.com/projectmesa/mesa/discussions/2230), [PR #2225](https://github.com/projectmesa/mesa/pull/2225)


### Removal of `mesa.flat` namespace
The `mesa.flat` namespace is removed. Use the full namespace for your imports.

- Ref: [PR #2091](https://github.com/projectmesa/mesa/pull/2091)


### Mandatory Model initialization with `super().__init__()`
In Mesa 3.0, it is now mandatory to call `super().__init__()` when initializing your model class. This ensures that all necessary Mesa model variables are correctly set up and agents are properly added to the model.

Make sure all your model classes explicitly call `super().__init__()` in their `__init__` method:

```python
class MyModel(mesa.Model):
    def __init__(self, *args, **kwargs):
        super().__init__()  # This is now required!
        # Your model initialization code here
```

This change ensures that all Mesa models are properly initialized, which is crucial for:
- Correctly adding agents to the model
- Setting up other essential Mesa model variables
- Maintaining consistency across all models

If you forget to call `super().__init__()`, you'll now see this error:

```
RuntimeError: The Mesa Model class was not initialized. You must explicitly initialize the Model by calling super().__init__() on initialization.
```

- Ref: [PR #2218](https://github.com/projectmesa/mesa/pull/2218), [PR #1928](https://github.com/projectmesa/mesa/pull/1928), Mesa-examples [PR #83](https://github.com/projectmesa/mesa-examples/pull/83)


### Automatic assignment of `unique_id` to Agents
In Mesa 3.0, the `unique_id` is now automatically assigned to agents upon creation. This change simplifies agent initialization and ensures uniqueness of agent identifiers.

_Key changes_
1. Agent initialization:
   - Old: `Agent(unique_id, model, ...)`
   - New: `Agent(model, ...)`
2. The `Model.next_id()` method is deprecated and will be removed in a future version.
3. The `Model.current_id` counter now starts at 0 instead of 1.

_Migration steps_
1. Update agent creation calls:
   ```python
   # Old
   agent = MyAgent(self.next_id(), self, ...)

   # New
   agent = MyAgent(self, ...)
   ```
2. Remove any custom logic for managing `unique_id` assignments.
3. If you were using `Model.next_id()` for purposes other than agent creation, replace it with alternative logic.
4. Be aware that agent IDs now start at 0 instead of 1, which may affect some model logic or data analysis.

- Ref: [PR #2226](https://github.com/projectmesa/mesa/pull/2226), [PR #2260](https://github.com/projectmesa/mesa/pull/2226), Mesa-examples [PR #194](https://github.com/projectmesa/mesa-examples/pull/194)


### AgentSet and `Model.agents`
#### AgentSet
<!-- TODO  -->

#### `Model.agents`
<!-- TODO  -->


### Time and schedulers
<!-- TODO general explanation-->

#### Automatic increase of the `steps` counter
The `steps` counter is now automatically increased. With each call to `Model.steps()` it's increased by 1, at the beginning of the step.

You can access it by `Model.steps`, and it's internally in the datacollector, batchrunner and the visualisation.

- Ref: [PR #2223](https://github.com/projectmesa/mesa/pull/2223), Mesa-examples [PR #161](https://github.com/projectmesa/mesa-examples/pull/161)

#### Removal of `Model._time` and rename `._steps`
- `Model._time` is removed. You can define your own time variable if needed.
- `Model._steps` steps is renamed to `Model.steps`.

#### Removal of `Model._advance_time()`
- The `Model._advance_time()` method is removed. This now happens automatically.

<!-- TODO deprecate all schedulers? -->


### Visualisation

Mesa has adopted a new API for our frontend. If you already migrated to the experimental new SolaraViz you can still use
the import from mesa.experimental. Otherwise here is a list of things you need to change.

#### Model Initialization

Previously SolaraViz was initialized by providing a `model_cls` and a `model_params`. This has changed to expect a model instance `model`. You can still provide (user-settable) `model_params`, but only if users should be able to change them. It is now also possible to pass in a "reactive model" by first calling `model = solara.reactive(model)`. This is useful for notebook environments. It allows you to pass the model to the SolaraViz Module, but continue to use the model. For example calling `model.value.step()` (notice the extra .value) will automatically update the plots. This currently only automatically works for the step method, you can force visualization updates by calling `model.value.force_update()`.

#### Default space visualization

Previously we included a default space drawer that you could configure with an `agent_portrayal` function. You now have to explicitly create a space drawer with the `agent_portrayal` function

```python
# old
from mesa.experimental import SolaraViz

SolaraViz(model_cls, model_params, agent_portrayal=agent_portrayal)

# new
from mesa.visualization import SolaraViz, make_space_matplotlib

SolaraViz(model, components=[make_space_matplotlib(agent_portrayal)])
```

#### Plotting "measures"

"Measure" plots also need to be made explicit here. Previously, measure could either be 1) A function that receives a model and returns a solara component or 2) A string or list of string of variables that are collected by the datacollector and are to be plotted as a line plot. 1) still works, but you can pass that function to "components" directly. 2) needs to explicitly call the `make_plot_measure()`function.

```python
# old
from mesa.experimental import SolaraViz

def make_plot(model):
    ...

SolaraViz(model_cls, model_params, measures=[make_plot, "foo", ["bar", "baz"]])

# new
from mesa.visualization import SolaraViz, make_plot_measure

SolaraViz(model, components=[make_plot, make_plot_measure("foo"), make_plot_measure("bar", "baz")])
```

#### Plotting text

To plot model-dependent text the experimental SolaraViz provided a `make_text` function that wraps another functions that receives the model and turns its string return value into a solara text component. Again, this other function can now be passed directly to the new SolaraViz components array. It is okay if your function just returns a string.

```python
# old
from mesa.experimental import SolaraViz, make_text

def show_steps(model):
    return f"Steps: {model.steps}"

SolaraViz(model_cls, model_params, measures=make_text(show_steps))

# new
from mesa.visualisation import SolaraViz

def show_steps(model):
    return f"Steps: {model.steps}"

SolaraViz(model, components=[show_steps])
```
