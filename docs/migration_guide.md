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


### Automatic assignment of `unique_id` to Agents
<!-- TODO -->

- Ref: [PR #2226](https://github.com/projectmesa/mesa/pull/2226)


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
<!-- TODO -->
