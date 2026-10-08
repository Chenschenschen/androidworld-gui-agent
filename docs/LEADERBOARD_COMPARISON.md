# Android World leaderboard comparison

Reviewed 8 October 2026. Research findings and proposals, not implemented changes.
Local comparison: current v29 configuration/source and WARMUP_RESULTS.md.

## What the scores establish

The [official leaderboard](https://docs.google.com/spreadsheets/d/1cchzP9dlTZ3WXQTfYNhh3avxoLipqHN75v1Tb86uhHo/edit?gid=0)
lists community submissions without independent verification. Selected pass@1
entries: MobileRun 100%, ARTEMIS 99.1%, mobile-use 91.4%, AutoGLM-Mobile 80.2%.
The latter is a closed 9B checkpoint with screenshot/accessibility input; its
identity is not established as our hosted autoglm-phone-multilingual model.
Our task-specific three-seed warm-up gates are not a full-benchmark score.

The [Minitap paper](https://arxiv.org/html/2602.07787v1) reports 100%, whereas
its mobile-use leaderboard entry still shows 91.4%. Keep the claims separate.

## Documented architectural differences

| Primary source | Documented mechanism | Comparison with our implementation |
| --- | --- | --- |
| [MobileRun architecture](https://docs.mobilerun.ai/framework/concepts/architecture) | Reasoning mode alternates Manager planning/checking with atomic Executor actions; shared state tracks plan progress and errors. Direct mode also exists. | Our scratch holds fixed task inputs; chronological replies and factual results do not constitute an explicitly updated subgoal plan. |
| [Minitap paper](https://arxiv.org/html/2602.07787v1), sections 4.1–4.3 | Fresh screenshots and hierarchy, tracked subgoals, sequential execution with actual-field text validation, and cycle detection that triggers strategy changes. | We check action syntax, coordinates, freshness and focus, and report observed field contents. We do not systematically compare every intended effect with its actual result. v29 bounds cycles by stopping. |
| [ARTEMIS architecture](https://github.com/google/artemis#how-artemis-is-architected) | Pro uses live target checks, retains failed-action incidents for recovery, maintains a plan and performs a read-only final review. Both profiles compress older history. Flash is a simpler reactive loop. | Our finish is accepted as the model's decision; the separate official verifier can then fail it. Old images are removed, but there is no dedicated semantic history summary or final GUI reviewer. |
| [MAI-UI report](https://arxiv.org/html/2512.22047v1) | GUI trajectory training and online reinforcement learning across hundreds of environments improve the underlying policy. | We call an existing hosted model. A better wrapper cannot reproduce another model's training. Model capability and agent architecture are separate variables. |

These are current published mechanisms, not proof that a particular mechanism
caused a leaderboard score. The sheet does not identify every submission's
exact execution profile/configuration. Screenshot-only submissions also succeed;
a hierarchy or multiple agents is not universally required.

## A simple official baseline we have not fully adopted

The installed, pinned [Android World M3A source](https://github.com/google-research/android_world/blob/2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7/android_world/agents/m3a.py)
was inspected locally: its step makes a second model call with before/after
screenshots and UI descriptions (around lines 568–605). The summary evaluates
the intended action's outcome and becomes the next decision's history. Our
adaptation includes sourced guidance but not this reflection mechanism.

This directly matches the D4 distinction between a valid action and successful
progress. A changed screenshot is not sufficient evidence of the intended effect.

## Evidence and proposed next experiment

Our [recorded results](WARMUP_RESULTS.md) expose the practical gap:

- Timer omitted a required zero, then continued editing a full wrong entry.
  Its first wrong step changed the GUI, so an unchanged-screen guard could not
  detect the semantic mistake.
- Clipboard selected Clear input while describing Copy, then false-finished
  from an unrelated suggestion. Actual-control feedback alone did not fix it.

The smallest candidate experiment is M3A-style before/after reflection using
the same model and one agent class. It should record intended effect, observed
effect and unresolved mismatch, leaving the model to choose any recovery.
A separate bounded read-only GUI completion review is another candidate,
especially for Clipboard; test it independently rather than changing both
mechanisms at once. Neither uses Android World's hidden verifier as feedback.

Keep native AutoGLM actions checked, official evaluation separate, and the
independent run_task.py entry point. Diagnose the preserved failure, record
one change, then run a bounded comparable trial. Increasing step limits alone
does not correct an omitted digit or a false completion. Additional calls cost
latency/tokens and the same model may repeat its perceptual error; improvement
must be measured. No runtime, prompt or model change was made for this review.
