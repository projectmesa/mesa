# Design principles and trade-offs

Mesa is for modellers with varying programming experience, including researchers and educators. When a contribution touches a trade-off below, name it in the discussion or pull request, say which side you chose, and explain why.

## Start with the modelling problem, not the requested mechanism

A request for an API or optimization is a clue, not yet a design. Establish who is modelling what, what happens now, and what outcome they need before settling on a solution. For substantial changes, agree on the problem and conceptual direction before code makes that decision harder to revisit.

**Questions we ask:**
- Which model, workflow, or user is affected?
- Can we reproduce the problem or otherwise show it matters?
- Is the proposed mechanism necessary to achieve the desired outcome?

**In practice:**
- For a new feature, discuss its direction before implementing it; a pathfinding PR can test an uncertain design without presenting it as settled ([#1889](https://github.com/mesa/mesa/issues/1889); [#1944](https://github.com/mesa/mesa/discussions/1944)).
- For performance proposals with unresolved design trade-offs, discuss the approach and assess its implications before opening an implementation PR ([#3846](https://github.com/mesa/mesa/issues/3846)).

**Where it gets hard:** A focused bug fix may not need lengthy design discussion. A public API or architectural change usually does, and review is less useful when it becomes the first place the project decides what the API should mean.

## Keep core focused on broadly useful modelling capabilities

Core functionality becomes a commitment to every Mesa user: it costs space in the API, documentation, testing, and maintenance. We favour building blocks that serve recurring modelling needs, and examples or integrations that show how to use the wider Python ecosystem. Specialised capabilities can still belong in core when the use case and value justify that commitment.

**Questions we ask:**
- Is this a common modelling need, or a specialised workflow?
- Could an example, extension, or established library address it?
- Would the abstraction remain useful beyond the motivating model?

**In practice:**
- Maintainers have favoured keeping specialised capabilities outside Mesa core and showing how to use established tools for sophisticated sensitivity analysis ([#1010](https://github.com/mesa/mesa/issues/1010); [#1908](https://github.com/mesa/mesa/issues/1908)).
- Mesa should focus on running models and leave adjacent work such as surrogate modelling to external libraries, with integrations demonstrated in examples ([#3170](https://github.com/mesa/mesa/issues/3170); [#3207](https://github.com/mesa/mesa/discussions/3207)).

**Where it gets hard:** A capability may be specialised today but become a useful foundation for many models. Concrete models and community use help us judge that better than generality alone.

## Prefer a coherent API with visible contracts

An API should make its behaviour, return values, and costs understandable. We favour one clear way to do a common task over overlapping methods or speculative configuration, and use explicit contracts where guessing would be surprising. Convenience is worthwhile when it removes real burden without hiding important semantics.

**Questions we ask:**
- Is there an obvious way to do this already?
- Can users infer what the method returns and what it changes?
- Does an option clarify a real choice, or add branches for hypothetical cases?

**In practice:**
- Mesa rejected a new `count` method when existing selection and `len` already expressed the operation ([#3391](https://github.com/mesa/mesa/issues/3391)).
- `AgentSet.get` did not gain a `skip` mode for missing attributes without concrete use cases ([#2279](https://github.com/mesa/mesa/issues/2279)).
- Mesa documents ambiguous sequence interpretation in `Agent.create_agents` rather than silently changing the behaviour ([#3780](https://github.com/mesa/mesa/issues/3780)).

**Where it gets hard:** Defaults and implicit conventions can make common tasks easier, but hidden rules can make models difficult to reason about. Prefer an explicit choice when the hidden behaviour would affect a model’s meaning.

## Keep components independent where users may combine them differently

Mesa should provide components that work together without forcing one component to own another’s responsibilities. This supports different model structures and makes it easier to replace, customise, or omit a component. Shared abstractions are useful when they reflect a real common concept, not just similar-looking code.

**Questions we ask:**
- Does this component need to know how another one is initialised or used?
- Can a model use it without adopting the rest of the proposed system?
- Is a shared abstraction simpler than keeping the concepts separate?

**In practice:**
- Mesa’s grids are modular rather than requiring every grid to be attached to a model ([#1116](https://github.com/mesa/mesa/issues/1116)).
- Visualization should not impose assumptions about model initialization or data collection ([#1213](https://github.com/mesa/mesa/issues/1213)).
- Signals are intended as an optional way to connect components, not a requirement to make models fully reactive ([#2972](https://github.com/mesa/mesa/discussions/2972)).

**Where it gets hard:** Independence can mean extra integration work or repeated code. We accept some separation when coupling would impose assumptions on models that do not need the feature.

## Keep Mesa teachable as well as flexible

Mesa serves people learning agent-based modelling and people building complex research models. The common path should be understandable and documented, while advanced users should be able to extend it without Mesa prescribing their model’s behaviour. Examples are part of that learning path: they should be focused, canonical demonstrations, not a home for every variant.

**Questions we ask:**
- Is the common task easy to learn and explain?
- Does the added flexibility create a steeper learning curve?
- Would an example help more users than a new core feature?

**In practice:**
- Maintainers have favoured readable, pedagogical code over a modest performance gain ([#1711](https://github.com/mesa/mesa/issues/1711)).
- Mesa’s own examples should use simple, canonical implementations; exploratory alternatives can live in mesa-examples ([#3286](https://github.com/mesa/mesa/issues/3286)).
- A model should demonstrate the capability it claims to demonstrate, rather than use a feature it does not need ([#3040](https://github.com/mesa/mesa/issues/3040)).

**Where it gets hard:** A beginner-friendly default can constrain advanced workflows; flexibility can also make the first steps harder. Examples and composable APIs can often support both without making every option part of the core API.

## Require performance evidence, and weigh it against complexity

Performance matters, but a plausible optimisation or a faster microbenchmark does not by itself justify added complexity. Compare equivalent workloads, use current APIs, and consider both the absolute time saved and the effect on a whole model. Prefer the smallest change that addresses a measured bottleneck.

**Questions we ask:**
- Is the benchmark representative of a real model and workload?
- Are the old and new implementations measured under the same conditions?
- Is the gain meaningful in elapsed time, and worth the maintenance cost?

**In practice:**
- Performance changes should be demonstrated on realistic usage and balanced against readability ([#1476](https://github.com/mesa/mesa/issues/1476)).
- Broad refactors with uncertain gains should give way to small, independently measured changes across relevant workloads ([#3388](https://github.com/mesa/mesa/issues/3388); [#3619](https://github.com/mesa/mesa/issues/3619)).
- Benchmark results from shared CI runners are evidence, but noisy evidence ([#1931](https://github.com/mesa/mesa/discussions/1931)).

**Where it gets hard:** A small per-operation cost can matter in a hot path, while a large percentage gain may barely affect a full simulation. State which level your evidence measures; do not treat one benchmark as universal.

## Make behaviour predictable and preserve reproducibility

Models depend on behaviour they can understand, control, and reproduce. Mesa should not silently guess at user intent, hide errors, or make outcomes depend on incidental ordering. Where a choice affects model behaviour, expose it or document it clearly.

**Questions we ask:**
- Could a user reasonably mistake what this operation does?
- Does an error remain visible enough to diagnose?
- Could iteration order, randomness, or a hidden default change results?

**In practice:**
- Mesa preserves deterministic selection when choosing from empty cells rather than relying on unordered-set iteration ([#3088](https://github.com/mesa/mesa/issues/3088)).
- Missing agent-type registration remains an error rather than silently returning an empty `AgentSet` ([#3608](https://github.com/mesa/mesa/issues/3608)).
- Mesa uses explicit RNG dependencies where components need randomness ([#2323](https://github.com/mesa/mesa/issues/2323)).

**Where it gets hard:** Extra validation and safeguards can themselves add overhead or complexity. Prefer checks where they prevent consequential mistakes, and do not add extensive validation when the underlying operation already gives a clear, inexpensive error ([#3545](https://github.com/mesa/mesa/issues/3545)).

## Treat stability and experimentation as different commitments

Stable public APIs deserve deliberate compatibility and migration care. Experimental features are a way to learn from use and feedback, not a label that makes an unclear design or unbounded breakage harmless. Say what is stable, what can change, and what users should do when it does.

**Questions we ask:**
- Is this public behaviour already relied on by users?
- Is the feature stable or experimental, and is that boundary clear?
- If behaviour changes, what is the migration path and release boundary?

**In practice:**
- Experimental APIs may change as they mature; stable features follow semantic versioning ([#2675](https://github.com/mesa/mesa/issues/2675)).
- Minor releases should not break existing models merely because the change is easy to describe ([#1917](https://github.com/mesa/mesa/issues/1917)).
- Mesa used a warning in Mesa 2.2 to prepare users for a return-type change planned for Mesa 3.0 ([#1965](https://github.com/mesa/mesa/issues/1965)).

**Where it gets hard:** A clean break can simplify a future design, but users need a credible transition. A major release is not itself a migration plan ([#2026](https://github.com/mesa/mesa/issues/2026)).

## Give users control without making every choice a setting

Meaningful defaults help people get started; forced conventions can limit models that need something different. Prefer defaults that match familiar expectations, and let users control behaviour when modelling needs genuinely vary. Avoid configuration whose only purpose is to cover possibilities no user has demonstrated.

**Questions we ask:**
- Is this a sensible default for the users Mesa serves?
- Would users need to override it for legitimate models?
- Is the choice part of the model’s meaning, or only an implementation detail?

**In practice:**
- Visualization APIs should let users control styling explicitly while providing useful defaults ([#2668](https://github.com/mesa/mesa/issues/2668)).
- Mesa rejected automatically mapping a cell’s `color` attribute to visualization colour, which would couple model data to backend conventions ([#2557](https://github.com/mesa/mesa/issues/2557); [#2558](https://github.com/mesa/mesa/issues/2558)).
- Custom rendering can be supplied as an additional component rather than expanding the built-in renderer to cover every case ([#2939](https://github.com/mesa/mesa/discussions/2939); [#2853](https://github.com/mesa/mesa/issues/2853)).

**Where it gets hard:** More options can preserve flexibility but make the API harder to learn. Prefer a clear extension point over a growing list of built-in settings when the need is specialised.

## Keep contributions reviewable and feedback actionable

A focused change makes it easier to understand what problem it solves and what evidence supports it. Separate required changes from optional follow-up ideas, and make review comments explain the concern and a useful next step. Rigour does not require contributors to infer the decision from a long list of disconnected requests.

**Questions we ask:**
- Is the change atomic, with unrelated work separated?
- Does the PR state its motivation, scope, and evidence?
- Are review comments clear about what is required and what is optional?

**In practice:**
- Keep PR diffs focused on the requested change, including in documentation ([#3074](https://github.com/mesa/mesa/issues/3074)).
- Separate required merge changes from interesting follow-up work ([#2430](https://github.com/mesa/mesa/issues/2430)).
- For a contributor new to tests, review can start with one relevant test and leave broader work for later ([#1481](https://github.com/mesa/mesa/issues/1481)).

**Where it gets hard:** A large review may uncover real design issues, but late or fragmented feedback can overwhelm contributors. Raise foundational questions early where possible, then consolidate the remaining asks into a manageable next step ([#1625](https://github.com/mesa/mesa/issues/1625); [#1898](https://github.com/mesa/mesa/issues/1898)).

## How these principles evolved

- In 2021–22, reviews often sought reproductions and benchmarks, while questions of architecture and scope could arrive late in implementation ([#982](https://github.com/mesa/mesa/issues/982); [#1278](https://github.com/mesa/mesa/issues/1278); [#1139](https://github.com/mesa/mesa/issues/1139)).
- In 2023–24, maintainers stated the sequence more explicitly: agree on the problem, then the concept, then the implementation. Compatibility and experimental boundaries became more visible ([#1889](https://github.com/mesa/mesa/issues/1889); [#1944](https://github.com/mesa/mesa/discussions/1944); [#1965](https://github.com/mesa/mesa/issues/1965)).
- In 2025–26, proposal-first expectations became more operational, especially for features and performance work. The intent is to prevent speculative effort, not to make process a substitute for explaining the design or the next step ([#3395](https://github.com/mesa/mesa/issues/3395); [#3846](https://github.com/mesa/mesa/issues/3846); [#3886](https://github.com/mesa/mesa/issues/3886); [#3888](https://github.com/mesa/mesa/issues/3888)).
- Across these shifts, Mesa has continued to value evidence, teachability, and manageable core scope; the emphasis has increasingly been on making design decisions early and legibly ([#1711](https://github.com/mesa/mesa/issues/1711); [#3207](https://github.com/mesa/mesa/discussions/3207); [#2972](https://github.com/mesa/mesa/discussions/2972)).

## Contested or open

- The scope of Mesa core and its module or repository boundaries remains unsettled; modularity can help components evolve independently, but it also adds maintenance commitments ([#1295](https://github.com/mesa/mesa/discussions/1295); [#2330](https://github.com/mesa/mesa/discussions/2330); [#2954](https://github.com/mesa/mesa/discussions/2954)).
- Maintainers have not settled a consistent threshold for merging a new non-experimental feature or how prior API approval relates to full review ([#2336](https://github.com/mesa/mesa/issues/2336)).
- The 2026 `FixedAgent` discussions show that repeated proposals can stall when desired behaviour has not been agreed and there is no clear route to consensus ([#3775](https://github.com/mesa/mesa/issues/3775); [#3794](https://github.com/mesa/mesa/issues/3794); [#3822](https://github.com/mesa/mesa/issues/3822); [#3823](https://github.com/mesa/mesa/issues/3823)).
- Performance trade-offs are workload-dependent. A result can support one strategy on one model and point the other way on another; maintainers may still differ on how much complexity a gain justifies ([#3388](https://github.com/mesa/mesa/issues/3388); [#3619](https://github.com/mesa/mesa/issues/3619); [#3932](https://github.com/mesa/mesa/issues/3932)).