# Code, test and documentation standards

These conventions apply across Mesa. Keep contributions focused, and check the surrounding code and documentation when deciding how a change should fit.

## Code style and tooling

- Follow PEP 8 and use Ruff for linting and formatting. The project configures Ruff’s docstring checks to use Google style; run the configured checks before submitting changes. (`pyproject.toml`)
- Use pre-commit to run the project’s code checks locally. Install the hooks with `pre-commit install`; they can apply automatic fixes that you should review and commit.
- Keep a pull request focused on an atomic change. Separate unrelated fixes, refactoring, or design decisions so each can be reviewed on its own. ([#3564](https://github.com/mesa/mesa/issues/3564), [#3599](https://github.com/mesa/mesa/issues/3599); [#3260](https://github.com/mesa/mesa/issues/3260))
- Write tests and documentation as part of the change, and inspect rendered documentation rather than relying only on the source markup. ([#3135](https://github.com/mesa/mesa/issues/3135); [#2697](https://github.com/mesa/mesa/issues/2697))

## API and naming conventions

- Design public APIs around clear concepts and consistent behavior. Prefer clarity over shorter names, and avoid adding overlapping methods just to preserve an old interface when a major-version change is appropriate. ([#1953](https://github.com/mesa/mesa/issues/1953); [#1566](https://github.com/mesa/mesa/issues/1566))
- Use operation-first names for space methods. For example, `iter_neighbors` yields agents, while `iter_neighborhood` yields neighborhood coordinates. ([#1184](https://github.com/mesa/mesa/issues/1184))
- Use built-in `TypeError` and `ValueError` for ordinary argument validation. Add a Mesa-specific exception only when it provides clear domain context or API value. ([#3380](https://github.com/mesa/mesa/issues/3380), [#3384](https://github.com/mesa/mesa/issues/3384))
- Document stable public APIs, not private implementation details. Use Mesa’s established private naming conventions for internal attributes, and make reserved names clear to users of subclasses. ([#1873](https://github.com/mesa/mesa/issues/1873); [#1942](https://github.com/mesa/mesa/issues/1942); [#2230](https://github.com/mesa/mesa/discussions/2230))
- Use the `|` syntax for union type annotations. For new generic typing work, use PEP 695 syntax, supported by Mesa’s Python 3.12 minimum. ([#1345](https://github.com/mesa/mesa/issues/1345); [#2885](https://github.com/mesa/mesa/issues/2885); `pyproject.toml`)
- When an API accepts a collection of fields, prefer a named argument such as `fields=[...]` where that makes the call clearer. Do not make arguments keyword-only by default; choose that form when it helps keep an API clear or extensible. ([#3156](https://github.com/mesa/mesa/issues/3156); [#3066](https://github.com/mesa/mesa/issues/3066), [#2972](https://github.com/mesa/mesa/discussions/2972))

## Errors and exceptions

Across Mesa, prefer clear and predictable exception behavior:

- Avoid raising generic `Exception`; use a specific built-in or Mesa-specific exception instead.
- For standard validation and input errors, prefer the most appropriate Python built-in exception.
- Use Mesa-specific exceptions when they add meaningful domain context or hide internal implementation details from callers.
- Follow the existing Mesa exception hierarchy: use the most specific `MesaException` subclass that fits the failure before introducing a new one.
- Always check with the maintainers as part of a PR or issue when you think you need a new exception.
- When wrapping internal exceptions, use `raise... from...` to preserve the original cause.
- Write exception messages that are actionable — users should immediately understand what went wrong and how to fix it.

When changing exception behavior, update or add tests to assert the expected exception type and message.

## Determinism and randomness

- Use the model’s seeded random-number generator for randomized setup and model behavior. Do not use an unrelated generator when you expect a model seed to make runs reproducible. ([#992](https://github.com/mesa/mesa/issues/992); [#2541](https://github.com/mesa/mesa/issues/2541), [#2561](https://github.com/mesa/mesa/issues/2561))
- Pass the model’s generator explicitly to components that do not have access to the model. Use the generator supported by the relevant API—for example, `random=model.random` or `rng=model.rng`—rather than relying on a component’s implicit default. ([#1994](https://github.com/mesa/mesa/issues/1994); [#2978](https://github.com/mesa/mesa/issues/2978))
- Let models accept a seed and pass it to the base `Model` constructor. In tutorials and examples, expose the seed so readers can reproduce a run. ([#2669](https://github.com/mesa/mesa/discussions/2669); [#2372](https://github.com/mesa/mesa/issues/2372))
- Keep ordering deterministic when results could depend on sets or other unordered sources. For example, sort graph traversal results when traversal order is not otherwise guaranteed. ([#1564](https://github.com/mesa/mesa/issues/1564), [#1569](https://github.com/mesa/mesa/issues/1569))
- When testing randomized behavior, use controlled seeds and assert the behavior that matters. Avoid relying on incidental output from a random run as if it were guaranteed.

## Performance changes and benchmarks

- Profile before optimizing. Measure elapsed time and locate the actual bottleneck; a lower function-call count alone does not establish a speedup. ([#1185](https://github.com/mesa/mesa/issues/1185); [#1452](https://github.com/mesa/mesa/issues/1452), [#1453](https://github.com/mesa/mesa/issues/1453))
- Compare the old and new implementations under the same conditions, including the same seed where relevant. Use workloads that reflect the proposed change, and check for regressions across relevant cases. ([#2696](https://github.com/mesa/mesa/issues/2696), [#2723](https://github.com/mesa/mesa/issues/2723); [#3388](https://github.com/mesa/mesa/issues/3388))
- Make benchmark comparisons fair: compare equivalent workloads, including equivalent data-collection work. Report the runtime environment and distinguish an operation-level improvement from a whole-simulation improvement. ([#995](https://github.com/mesa/mesa/discussions/995), [#977](https://github.com/mesa/mesa/issues/977); [#1546](https://github.com/mesa/mesa/issues/1546), [#1565](https://github.com/mesa/mesa/issues/1565))
- Consider both elapsed time and percentage changes. A large percentage change in a very small runtime may not matter to real models. Treat results from shared CI runners as noisy evidence, not definitive measurements. ([#3108](https://github.com/mesa/mesa/issues/3108), [#3128](https://github.com/mesa/mesa/issues/3128); [#3160](https://github.com/mesa/mesa/issues/3160))
- Prefer readable, maintainable code unless measured results show a meaningful benefit for realistic use. Keep benchmark code separate from tests; `tests/benchmark` is an established location. ([#1476](https://github.com/mesa/mesa/issues/1476); [#1565](https://github.com/mesa/mesa/issues/1565))

## Dependencies

- Keep specialized dependencies optional when they are needed only for particular features. Mesa’s project configuration separates extras such as `network` and `viz` from core dependencies. (`pyproject.toml`; [#3365](https://github.com/mesa/mesa/issues/3365), [#3366](https://github.com/mesa/mesa/issues/3366))
- Avoid adding every example’s optional packages to the development dependency set. Keep development installs manageable as examples grow. ([#1394](https://github.com/mesa/mesa/discussions/1394))
- Specify a minimum dependency version only when Mesa needs a newer feature; do not pin Python library dependencies to exact versions. ([#2790](https://github.com/mesa/mesa/issues/2790))
- Keep imports of optional packages within the functionality that requires them, so users who have not installed an extra can still use unrelated core functionality. For example, `Network` imports NetworkX only when it is instantiated. ([#3598](https://github.com/mesa/mesa/issues/3598))

## Tests

- Add or update tests for behavior changes, and put them with the tests for the relevant source module. The `tests/` directory mirrors the source-module structure; keep its hierarchy one level deep. ([#2994](https://github.com/mesa/mesa/issues/2994))
- Check for existing coverage before adding tests. Extend the relevant test module for a small change rather than creating a separate file or duplicating coverage. ([#3117](https://github.com/mesa/mesa/issues/3117), [#3118](https://github.com/mesa/mesa/issues/3118); [#3544](https://github.com/mesa/mesa/issues/3544))
- Write tests that verify the behavior users rely on, including relevant edge cases. For failures, exercise the exception path explicitly—for example, with `pytest.raises`—and check the expected type and message. ([#2605](https://github.com/mesa/mesa/issues/2605))
- Give tests a docstring, even if it is a single line. Keep fixtures local to the test module unless other test files need them. ([#2981](https://github.com/mesa/mesa/issues/2981); [#2931](https://github.com/mesa/mesa/issues/2931))
- Use pytest for unit tests and run the relevant tests after your change. Check coverage as well; aim to keep it from going down and cover changed behavior as fully as reasonably possible. ([#2605](https://github.com/mesa/mesa/issues/2605))
- Use model-based tests where they help verify that Mesa features work together. Example tests primarily check that models run; they do not need to assert a particular simulation result in every case. ([#2390](https://github.com/mesa/mesa/issues/2390))

## Documentation, tutorials and examples conventions

- Use Google-style docstrings for API reference. Start with a brief description before sections such as `Args:` so autodocumentation can include the function. Keep reference documentation focused on public APIs; use tutorials to explain how to use Mesa. ([#2294](https://github.com/mesa/mesa/issues/2294), [#2298](https://github.com/mesa/mesa/issues/2298); [#1091](https://github.com/mesa/mesa/issues/1091); [#1873](https://github.com/mesa/mesa/issues/1873))
- Document public features where users can find them. For a changed or removed API, explain the issue, the change, and what users need to do; do not rely on readers finding that context in a linked issue. ([#2214](https://github.com/mesa/mesa/issues/2214); [#2209](https://github.com/mesa/mesa/issues/2209))
- Follow the [deprecation policy](#deprecations-and-breaking-changes) below for changes to stable APIs.
- Use the migration guide for incompatible changes and removed APIs. Give a practical migration recipe, with before-and-after examples where useful; use release notes for new features that do not break existing models. ([#2233](https://github.com/mesa/mesa/issues/2233); [#1731](https://github.com/mesa/mesa/issues/1731))
- Keep documentation in Markdown, use cross-references for links between documentation pages, and use relative links without an `.html` suffix. Build and inspect the rendered pages. ([#2034](https://github.com/mesa/mesa/issues/2034), [#2035](https://github.com/mesa/mesa/issues/2035), [#2036](https://github.com/mesa/mesa/issues/2036), [#2041](https://github.com/mesa/mesa/issues/2041); [#2244](https://github.com/mesa/mesa/issues/2244); [#2274](https://github.com/mesa/mesa/issues/2274); [#2697](https://github.com/mesa/mesa/issues/2697))
- Do not commit files generated during the documentation build. Maintain the source material and let the build generate its rendered output. ([#2392](https://github.com/mesa/mesa/issues/2392), [#2382](https://github.com/mesa/mesa/issues/2382); [#2448](https://github.com/mesa/mesa/issues/2448))
- For tutorial notebooks, keep the explanation instructional and outputs concise. Clear cell outputs before committing notebook changes. When adding, renaming, or reordering tutorials, update the related listings, inbound links, prerequisites, and Colab or Binder links as applicable. ([#2194](https://github.com/mesa/mesa/issues/2194); [#1661](https://github.com/mesa/mesa/issues/1661), [#1694](https://github.com/mesa/mesa/issues/1694), [#1695](https://github.com/mesa/mesa/issues/1695); [#3280](https://github.com/mesa/mesa/issues/3280))
- Keep examples focused on demonstrating Mesa features. Core examples should be canonical and lean; contribute broader or alternative examples to `mesa-examples`. ([#2706](https://github.com/mesa/mesa/issues/2706); [#3286](https://github.com/mesa/mesa/issues/3286); [#3383](https://github.com/mesa/mesa/issues/3383), [#3533](https://github.com/mesa/mesa/issues/3533))
- Demonstrate new features in an example when that helps users understand them and gives us an integration check. Keep examples using only stable features in the basic group, and make sure examples using experimental APIs are clearly grouped as experimental. ([#2748](https://github.com/mesa/mesa/issues/2748); [#3785](https://github.com/mesa/mesa/issues/3785))

## Experimental code

- Mark experimental features clearly, including where users should import them. Experimental APIs may change between releases; do not present them as stable public APIs. ([#2587](https://github.com/mesa/mesa/issues/2587), [#2597](https://github.com/mesa/mesa/issues/2597); [#2675](https://github.com/mesa/mesa/issues/2675))
- Use experimental code to test ideas with real models and community feedback. Keep the initial change focused; experimental work can be refined as the design develops. ([#3145](https://github.com/mesa/mesa/issues/3145); [#2927](https://github.com/mesa/mesa/discussions/2927))
- Where useful, add an illustrative example alongside experimental code. Keep it in the experimental examples group, and remove or relocate it once the API stabilizes. ([#2575](https://github.com/mesa/mesa/issues/2575); [#3785](https://github.com/mesa/mesa/issues/3785))
- When an experimental API changes, communicate the change in release notes. Do not imply that experimental APIs have the same compatibility guarantees as stable APIs. ([#2675](https://github.com/mesa/mesa/issues/2675); [#3785](https://github.com/mesa/mesa/issues/3785))

## Examples: core and community
Mesa maintains a curated set of core examples within the main repository, complemented by a separate [mesa-examples](https://github.com/mesa/mesa-examples) repository for community contributions. This two-tier structure balances maintainability with community creativity.

### Core examples (in `mesa/examples`)
Core examples in the main Mesa repository are classic, well-known agent-based models that demonstrate Mesa's capabilities and serve as learning resources. They are organized into two categories:

- **Basic Examples** use only stable Mesa features and are ideal starting points for beginners.
- **Advanced Examples** are more complex models that may use experimental features to demonstrate advanced concepts.

Core examples are:
- Tested in CI, including batch runs and visualizations
- Maintained to high code quality standards
- Updated to work with each Mesa release
- Documented and included in ReadTheDocs
- Some are used in performance benchmarking

### Community examples (in mesa-examples)
The [mesa-examples](https://github.com/mesa/mesa-examples) repository serves as a gallery for user-contributed models and creative applications of Mesa. We welcome diverse contributions here with more relaxed maintenance requirements. Examples in this repository should include:
- A clear README explaining the model
- Requirements or environment files for reproducibility
- Working code compatible with at least one Mesa major version

We accept contributions liberally to this repository to showcase the breadth of Mesa applications, even if we cannot actively maintain all examples long-term.

### Contributing examples
When contributing a new example, consider:
- **For core examples**: Propose additions through a GitHub discussion first. Core examples should be:
  - widely-recognized canonical models
  - demonstrate specific Mesa features effectively (that are not already sufficiently demonstrated by other models)
- **For community examples**: Open a PR directly to mesa-examples with your model, README, and environment file.
- **Improving existing examples**: PRs to update or enhance any example are always welcome in either repository.

This structure allows us to maintain a stable, high-quality set of learning resources while encouraging community creativity and diverse applications of Mesa.

Historical context and further motivation can be found in discussion [#2330](https://github.com/mesa/mesa/discussions/2330) and PR [#2349](https://github.com/mesa/mesa/pull/2349).

## Deprecations and breaking changes
Mesa follows [Semantic Versioning](https://semver.org/) (SemVer) and has a structured deprecation process to ensure users have time to migrate to new APIs while maintaining backward compatibility.

### Deprecation process
#### Step 1: Introduce alternative
When implementing a replacement feature:

- Add the new, stable alternative
- Optionally add a `PendingDeprecationWarning` to the old feature (signals intent in source code, hidden by default)

```python
warnings.warn(
    "old_feature() will be deprecated in a future release. "
    "Use new_feature() instead.",
    PendingDeprecationWarning,
    stacklevel=2,
)
```

#### Step 2: Complete prerequisites
Before active deprecation, all of the following must be complete:

1. **Documentation updated**: All relevant docs and tutorials reflect the new approach
2. **Migration guide entry added**: Clear entry in the [Migration Guide](https://github.com/mesa/mesa/blob/main/docs/migration_guide.md) explaining what changed and how to update code
3. **Examples updated**: All example models use the new API

#### Step 3: Active deprecation
The alternative must be available for *at least one minor release* before adding a `FutureWarning`. This warning is visible to all users by default.

```python
warnings.warn(
    "old_feature() is deprecated and will be removed in Mesa X.0. "
    "Use new_feature() instead. "
    "See: https://mesa.readthedocs.io/latest/migration_guide.html#section",
    FutureWarning,
    stacklevel=2,
)
```

#### Step 4: Remove deprecated feature
Remove the old feature in the next major version.

### Version requirements
| Action | Allowed in |
|--------|------------|
| Add alternative + `PendingDeprecationWarning` | Any release |
| Add `FutureWarning` | Minor release (patch only with compelling reason) |
| Remove deprecated feature | Major release only |

### Experimental features
For features in `mesa.experimental`, steps 1–3 can be done simultaneously, and step 4 can occur in any subsequent release (including minor/patch). Experimental features:

- Can be changed or removed in any release
- Don't require a deprecation warning period
- Should still communicate changes through release notes

Following the full process is encouraged when feasible.

### Migration guide entry format
Place new entries at the top (newest first). Include:

1. Clear heading describing the change
2. Brief explanation of what changed and why
3. Before/after code examples
4. Links to relevant PRs/issues

````markdown
## Mesa X.Y.0
### Feature Name Change
Brief description of what changed and why.

```python
 Old
old_method()

 New
new_method()
```

- Ref: [PR #1234](https://github.com/mesa/mesa/pull/1234), [Documentation](link)
````
