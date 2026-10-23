# Reviewing contributions

Review is how we decide whether a change solves a real problem and fits Mesa—not just whether the code runs. We want to be rigorous and welcoming at the same time. Give contributors enough context to understand our concerns, and a clear next step they can take.

This guide is for maintainers, collaborators, and peer reviewers, including GSoC contributors. For the values behind these questions, see [Design principles and trade-offs](principles). Reviewers can help clarify a problem, test an approach, and improve an implementation. Maintainers decide project direction and whether a change is ready to merge.

## Review in order: problem, concept, implementation

Work through three questions, in order:

1. **Problem:** Is there a real, sufficiently understood problem for Mesa to solve?
2. **Concept:** Do we agree on what a good solution should do and what it will cost?
3. **Implementation:** Does the code deliver that agreed solution safely?

This is a sequence of attention, not a demand for a long process. A small, reproducible bug fix may move through all three quickly. A new public API or architectural change usually needs more discussion before code review can be useful. For feature work, look for prior agreement on the direction; clear, scoped bug fixes can generally come directly as PRs ([#3395](https://github.com/mesa/mesa/issues/3395)).

If the problem or concept is unsettled, reviewing implementation details can waste everyone’s time. A reviewer might request tests, names, or edge-case handling for a design that will change—or be declined. That is also why line-level AI review bots have not worked well for us as a substitute for stage-aware review: they can focus attention on local code details before we know whether that code should exist, and can add noise ([#2851](https://github.com/mesa/mesa/issues/2851); [#3485](https://github.com/mesa/mesa/discussions/3485)).

## What to review at each level

### Problem: what are we solving?

Start with the user’s task and the observed behavior. Ask:

- Who is affected, and in what model or workflow?
- What did they expect, and what happened instead?
- Can we reproduce the behavior with a minimal example, logs, or other relevant evidence?
- Is this a Mesa bug, an intentional constraint, a misunderstanding, or an issue in another component?
- Does the need belong in Mesa core, an example, an extension, or another project?

**Ready to move on:** We can describe the user’s problem without relying on the proposed implementation. The behavior is reproducible, or the missing evidence is clear. We have a plausible understanding of where the issue belongs.

When a report is hard to diagnose, ask for the smallest useful missing piece rather than guessing at a fix. Reproducing a report before proposing a change helps distinguish a root cause from a nearby symptom ([#982](https://github.com/mesa/mesa/issues/982); [#2811](https://github.com/mesa/mesa/issues/2811); [#2824](https://github.com/mesa/mesa/issues/2824)).

### Concept: what should the solution mean?

Once the need is clear, discuss the user-visible behavior before getting lost in code. Ask:

- What should users be able to do, and what should they observe?
- What should happen for important edge cases, defaults, and errors?
- Which alternatives could solve the problem? What does each trade away?
- Does the change add public API or affect stable behavior?
- What are the costs to complexity, performance, teaching, compatibility, and maintenance?
- Is the work appropriately scoped to Mesa and the relevant repository?

**Ready to move on:** We share a high-level understanding of the intended behavior and scope. The main trade-offs are visible, and the API direction has maintainer alignment where needed. If the design is still uncertain, a discussion, issue, or draft pathfinding PR can help test it before a full implementation ([#1944](https://github.com/mesa/mesa/discussions/1944); [#2564](https://github.com/mesa/mesa/issues/2564)).

Treat experimental status as useful context, not a substitute for a coherent proposal. Be clear about what is open to change and what the experiment is meant to establish.

### Implementation: does the code deliver?

Now review whether the implementation matches the agreed concept. Ask:

- Does it implement the intended behavior, including important edge cases?
- Do tests demonstrate the reported problem and verify the changed behavior?
- Are the tests placed with related coverage, and do they add useful coverage?
- Are performance claims backed by representative workloads and a fair comparison?
- Do docs and examples match the behavior? Are migration notes needed?
- Is the change focused enough to review, test, and maintain?

**Ready for final review:** The PR description explains the motivation and approach; the code and tests address the agreed scope; relevant checks pass or failures are understood. Performance and compatibility claims have suitable evidence where applicable. Keep the PR atomic: separate independent changes so reviewers can assess each one clearly ([#3484](https://github.com/mesa/mesa/issues/3484); [#3714](https://github.com/mesa/mesa/issues/3714)).

## Give feedback people can act on

Warm feedback is specific. It does not mean avoiding disagreement or lowering the bar. It means explaining the bar and helping the contributor see how to meet it.

- **Reproduce first.** Try the example or test the claim before recommending a fix. If you cannot reproduce it, say what you tried and ask for the evidence you still need.
- **Explain the reason.** Say what risk, user expectation, project boundary, or design concern is behind the comment. “This API is unclear” leaves the author guessing; explain what a user would find ambiguous.
- **Give one clear next step.** Ask for the smallest change or piece of evidence that will move the review forward. When several changes are needed, number them.
- **Separate required from optional.** Label what blocks approval and what is a suggestion or follow-up idea. Interesting cleanup should not hold up an otherwise focused change ([#2430](https://github.com/mesa/mesa/issues/2430)).
- **Consolidate asks.** Before asking for more work, check the whole diff and prior comments. Give a current, coherent list rather than making the contributor piece together requirements across scattered reviews.
- **Acknowledge uncertainty.** Say when you are unsure, invite correction, and identify what evidence would resolve the question. Review is discussion, not a verdict on the person.
- **Praise specifically.** Point to a useful test, clear explanation, or improvement in the code. Specific praise tells the contributor what worked and shows that we have read the change.

For example: “I can reproduce the error with this small model. It comes from the grid topology, not caching, so adding a cache would mask the cause. Could you add a regression test for this placement case first? Then we can check the fix against it.” This gives evidence, a reason, and one next step.

Interactions tend to go cold when we correct someone without explaining how to proceed, introduce new requirements late, or treat disagreement as a personal failing. Blunt skepticism can shut down useful investigation; so can a long list of fragmented requests that leaves the contributor to infer which ones matter. If the review has uncovered a design question, say so and move the discussion to the right level rather than continuing to debate code that may be discarded ([#1625](https://github.com/mesa/mesa/issues/1625); [#1898](https://github.com/mesa/mesa/issues/1898)).

## Close or redirect a PR kindly

A PR does not have to merge to have been worthwhile. If we cannot proceed, explain the reason plainly: for example, the need is not demonstrated, the design is unsettled, the work belongs elsewhere, or another change has superseded it.

Then give a path forward where one exists. That might be a minimal reproducer, a discussion to agree on the behavior, a narrower PR, a different repository, or a link to the work that superseded it. If there is no useful next step yet, explain what is missing rather than implying that more code will solve it. When closing because a contributor has not responded or required checks remain unresolved, summarize what is still needed and whether reopening or submitting a new PR would make sense.

Do not make process enforcement the whole explanation. If a feature needed prior design agreement, say what decision remains open and where to discuss it. A clear reason and route forward make a closure easier to understand, even when the answer is no ([#3886](https://github.com/mesa/mesa/issues/3886); [#3888](https://github.com/mesa/mesa/issues/3888)).

## Peer review by contributors

Peer review is valuable even when you are not a maintainer. Help make the problem, design, or implementation clearer: reproduce the issue, ask about an unclear contract, check a test, or point out an edge case. If you have a different design suggestion, explain the user need or trade-off behind it.

Be clear about what you can assess and what you cannot. You can say, “I tested this case and it fails,” or “I’m not sure this API is agreed yet.” Do not present your preference as Mesa policy or imply that maintainers have approved a direction. For GSoC peer reviewers, focus on learning and actionable feedback: explain how to investigate, invite questions, and keep the next task manageable. Maintainers remain responsible for project decisions and merge approval.

## Using AI tools in review

AI tools can help you inspect code, draft test ideas, summarize a long discussion, or spot a possible inconsistency. Treat every suggestion as a lead to verify—not as evidence by itself. Check it against the actual code, tests, current documentation, and the problem the PR is meant to solve.

Respect the review stage. If the problem or concept is unsettled, surface that first; do not let a stream of naming or line-level comments make the implementation look ready. If you use a bot, triage its comments before passing them on. Do not ask maintainers or contributors to sort a batch of unverified suggestions for you ([#2851](https://github.com/mesa/mesa/issues/2851)).

A bot cannot speak for maintainer consensus, approve a design, or decide that a PR should close. Keep human responsibility visible: explain which findings you verified, which remain uncertain, and what you recommend next.
