# Project decisions

Use this page to find cross-cutting decisions and their rationale; it complements, rather than replaces, the relevant contributor and user documentation. When a decision is made, add an entry in the PR that implements it. If a decision changes, mark the earlier entry as superseded rather than deleting it.

## Scope of Mesa core

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2026-01-18 | Keep Mesa focused on agent-based modeling; surrogate modeling, calibration, and sensitivity analysis belong in external libraries. Use examples to demonstrate integrations with those tools. | Keeping adjacent research and analysis workflows out of core helps keep Mesa’s scope focused. | ([#3170](https://github.com/mesa/mesa/issues/3170)) | current |
| 2026-01-04 | Treat `mesa.space` as maintenance-only: avoid new functionality and optimization work unless it addresses a clear or critical bug. Direct new development toward newer space APIs. | Mesa’s development direction is the newer space APIs; the older module is maintained, not actively developed. | ([#3066](https://github.com/mesa/mesa/issues/3066)), ([#3082](https://github.com/mesa/mesa/issues/3082)), ([#3111](https://github.com/mesa/mesa/issues/3111)) | superseded: `mesa.space` removed in Mesa 4.0 (see the [migration guide](../migration_guide)) |

## Ecosystem and repository boundaries

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2024-10-18 | Keep core examples under `mesa.examples`. Use the separate `mesa-examples` repository for community models. | Packaging examples as a separate top-level package led to inconsistent imports. A separate repository also provides room for community examples that Mesa cannot maintain in core. | ([#2387](https://github.com/mesa/mesa/issues/2387)), ([#2383](https://github.com/mesa/mesa/issues/2383)) | current |
| 2026-01-16 | Add new examples to Mesa’s core repository only with broad prior maintainer agreement. Otherwise, submit them to `mesa-examples`. | Core examples need to justify their ongoing maintenance in Mesa. | ([#3149](https://github.com/mesa/mesa/issues/3149)) | current |
| 2025-01-21 | Keep SolaraViz experimental during Mesa 3.x; minor releases may include API-breaking changes. | Time alone does not establish stability, and the component remains under active development. | ([#2636](https://github.com/mesa/mesa/issues/2636)) | current |
| 2025-12-05 | Do not duplicate Mesa’s visualization API in Mesa-Geo. Geo-specific needs, such as raster and vector layers, may require a distinct design. | Geospatial data and visualization have domain-specific needs. | ([#2927](https://github.com/mesa/mesa/discussions/2927)) | current |

## Release and deprecation

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2022-06-15 | Use semantic versioning; treat incompatible public API changes as major-version changes. | Users rely on version constraints and need incompatible changes to be signaled. | ([#1353](https://github.com/mesa/mesa/discussions/1353)), ([#1365](https://github.com/mesa/mesa/issues/1365)) | current |
| 2026-01-14 | Deprecate an API when a stable replacement exists; defer deprecation when there is no replacement. | Users need a viable path forward before we ask them to migrate. | ([#3136](https://github.com/mesa/mesa/issues/3136)) | current |
| 2026-03-16 | Stage deprecations: start with `PendingDeprecationWarning`, address resulting breakage and integrations, then use `FutureWarning` when a stable alternative is available. Update relevant documentation, tutorials, and the migration guide before or when the user-visible warning is introduced. | A user-visible warning should point to a stable alternative, and early warnings help identify issues that need to be resolved before removal. | ([#3547](https://github.com/mesa/mesa/issues/3547)), ([#3551](https://github.com/mesa/mesa/issues/3551)), ([#2900](https://github.com/mesa/mesa/issues/2900)), ([#2905](https://github.com/mesa/mesa/issues/2905)) | current |
| 2025-05-27 | Normally remove deprecated behavior only after at least one minor release, with migration guidance and release notes, examples updated to the replacement, and the replacement ready. Choose the breaking-change version explicitly for visualization changes. | Users need time and guidance to move to a stable replacement. | ([#2797](https://github.com/mesa/mesa/issues/2797)) | current |
| 2026-02-17 | Do not add API deprecation warnings on the Mesa 4.0 development branch. Establish the scope of 4.0 changes first, then add appropriate warnings on the 3.x branch. | Warnings are useful to current users only once the planned changes are clear. | ([#3330](https://github.com/mesa/mesa/issues/3330)) | current |

## Documentation and examples

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2022-06-12 | Use the Jupyter notebook as the tutorial source and render it for the documentation, rather than maintaining a parallel `.rst` copy. | Keeping two copies in sync causes drift and cumbersome diffs. | ([#1361](https://github.com/mesa/mesa/issues/1361)), ([#1363](https://github.com/mesa/mesa/issues/1363)) | current |
| 2024-09-04 | Make notebook execution errors fail the Read the Docs build. | A failing tutorial should be visible in the documentation build, not pass silently. | ([#2270](https://github.com/mesa/mesa/issues/2270)), ([#2276](https://github.com/mesa/mesa/issues/2276)) | current |
| 2024-11-02 | Keep the migration guide easy to find in the top-level documentation navigation. | Existing users need to locate migration guidance easily. | ([#2450](https://github.com/mesa/mesa/issues/2450)) | current |
| 2026-02-17 | Update examples when APIs change, but consider rewriting migration guides and tutorials together when preparing the Mesa 4 beta, after the accumulated changes are clearer. | A complete migration guide is more useful once the scope of release changes is known. | ([#3337](https://github.com/mesa/mesa/issues/3337)) | current |

## Dependencies and supported versions

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2023-10-30 | As a library, avoid pinning dependencies to specific releases. Set minimum versions when needed and otherwise support a broad range; users who need exact reproducibility should pin dependencies in their own projects. | Pins limit interoperability and flexibility, and maintaining them creates ongoing work. | ([#1852](https://github.com/mesa/mesa/issues/1852)) | current |
| 2026-03-22 | Keep NetworkX optional by importing it lazily when a Network space is instantiated. | Users should be able to import Mesa with the base installation without importing NetworkX. | ([#3596](https://github.com/mesa/mesa/issues/3596)), ([#2343](https://github.com/mesa/mesa/issues/2343)), ([#3598](https://github.com/mesa/mesa/issues/3598)) | current |

## Contribution process

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2021-02-03 | Use GitHub Discussions for general questions and community conversation; reserve issues for problems or feature requests about Mesa itself. | This gives questions and ideas a suitable venue and keeps the issue tracker focused. | ([#987](https://github.com/mesa/mesa/issues/987)), ([#994](https://github.com/mesa/mesa/discussions/994)) | current |
| 2026-01-14 | Use issues to track concrete work and Discussions for broader or less-defined exploration. | Separating tracked work from open-ended exploration helps contributors choose the right place to start. | ([#3135](https://github.com/mesa/mesa/issues/3135)) | current |
| 2026-02-27 | Get maintainer approval in an issue or discussion before opening an implementation PR for a feature or enhancement. Clear, scoped bug fixes can generally be submitted directly. | Prior alignment reduces avoidable review work. | ([#3395](https://github.com/mesa/mesa/issues/3395)) | current |
| 2026-03-06 | For substantial or experimental features, agree on the problem, conceptual solution, and high-level design before implementation. Use discussion, pathfinding PRs, and a tracking issue where helpful. | Early alignment makes substantial work easier to assess and reduces the risk of implementing an unagreed design. | ([#3456](https://github.com/mesa/mesa/issues/3456)), ([#3266](https://github.com/mesa/mesa/issues/3266)), ([#2921](https://github.com/mesa/mesa/discussions/2921)), ([#3132](https://github.com/mesa/mesa/issues/3132)), ([#3135](https://github.com/mesa/mesa/issues/3135)) | current |
| 2026-03-09 | Keep contributions atomic, address a specific agreed-upon problem, and submit them to the repository that owns the work. Align broad or multi-problem proposals with maintainers before opening a PR. | Focused work is easier to review and avoids sending changes to the wrong repository. | ([#3484](https://github.com/mesa/mesa/issues/3484)), ([#3485](https://github.com/mesa/mesa/discussions/3485)) | current |
| 2026-09-27 | Follow Mesa’s PR process and use the prescribed PR template. | Review capacity is limited, so clear and consistent submissions help maintainers review changes. | ([#3886](https://github.com/mesa/mesa/issues/3886)), ([#3888](https://github.com/mesa/mesa/issues/3888)) | current |
| 2025-08-06 | Reproduce a reported bug before proposing a fix; include a minimal reproducer and relevant error output when asking for help. | Reproducing the behavior helps us diagnose its cause and avoid masking a problem with an unrelated workaround. | ([#2824](https://github.com/mesa/mesa/issues/2824)), ([#1056](https://github.com/mesa/mesa/issues/1056)) | current |
| 2025-11-29 | Contributors using AI assistance must understand and verify their changes; acknowledge AI assistance where used. Low-effort, unverified AI-generated submissions are not acceptable. | Contributions need to be grounded in understanding and good-faith work. | ([#2898](https://github.com/mesa/mesa/issues/2898)), ([#3773](https://github.com/mesa/mesa/issues/3773)) | current |

## Governance and community

| Date | Decision | Why | Refs | Status |
|---|---|---|---|---|
| 2026-01-08 | Keep issue labeling and stale-item decisions as deliberate maintainer triage rather than automating labels or stale marking. Direct questions to Discussions. | Maintainers want triage to reflect the context of each issue and avoid automated messages disrupting varied contribution timelines. | ([#3094](https://github.com/mesa/mesa/issues/3094)) | current; under re-evaluation |
| 2026-03-09 | Use automated PR tooling for triage, not code review; monitor and improve the tooling over time. | Triage can help manage maintainer capacity, but the system itself needs ongoing attention. | ([#3485](https://github.com/mesa/mesa/discussions/3485)) | current; under re-evaluation |

## Ideas we decided against

- **Adding surrogate modeling, calibration, or sensitivity analysis to Mesa core.** These are outside Mesa’s agent-based modeling scope. Use external libraries and demonstrate integrations in examples. Refs: ([#3170](https://github.com/mesa/mesa/issues/3170)).
- **Presenting a model as an example of a capability it does not need.** For example, a model that does not need discrete-event scheduling should not be presented as a DEVS example. Submit it to `mesa-examples` if it is not a suitable core example. Refs: ([#3040](https://github.com/mesa/mesa/issues/3040)).

## Open questions

- What APIs and other user-facing changes will be in scope for Mesa 4, and which deprecations should be introduced on the 3.x line? ([#3271](https://github.com/mesa/mesa/issues/3271)), ([#3330](https://github.com/mesa/mesa/issues/3330))
- Which examples should Mesa’s CI continue to test across repository boundaries, and should that set change for Mesa 4? ([#3173](https://github.com/mesa/mesa/issues/3173))
- What substantive changes are needed in the tutorial on agent activation, event scheduling, and time progression? Migrating examples to `run_for()` does not resolve that work. ([#3270](https://github.com/mesa/mesa/issues/3270))
