# AutoGLM migration and first Wi-Fi trials — 7 October 2026

The default runtime now uses `autoglm-phone-multilingual` through Z.ai.
`autoglm_agent.py` contains one agent class: capture screenshot → API request →
parse/validate one native action → Android World GUI execution → capture result.
`run_task.py`, `run.ps1` and the evaluation scheduler use this agent. No packages
were added. Local GELab source and every previous run remain preserved.

## What changed and why

Read all of [TRAJECTORY_FAILURE_ANALYSIS.md](TRAJECTORY_FAILURE_ANALYSIS.md)
before implementing. Status-bar-only trees are no longer model input. The model
always receives a real screenshot with exact task inputs and recent observed
results. Its native pseudo-calls are interpreted with AST/literal validation;
no model-generated code executes. Normal field-focus taps are allowed again.

Image freshness checks cover the selected point and broader screen changes,
excluding status/navigation bars. Unrelated whole-tree differences cannot abort
an unchanged target. A changed, unexecuted decision can be discarded once and
requested again from a uniquely logged fresh screenshot. Executed/uncertain
actions are never automatically replayed. With the current screenshot-only
backend there is no XML target identity/focus check; the checks are visual.
Their numeric thresholds are provisional and do not guarantee every modal or
moving-target change is detected.

Initially, a checked unique XML dump was added for UIAutomator. Its first trial
failed because the dumper could not obtain an idle state. A diagnostic reproduced
`ERROR: could not get idle state`, with no output file. The corrected version
uses Android World's official `A11yMethod.NONE` and bounded visual settling
instead. The failed XML adapter remains available only for later bounded probes.
The test AccessibilityForwarder service was disabled and force-stopped; other
services were retained. This infrastructure operation did not enable Wi-Fi.

Sampling: temperature 0, top_p 0.85, frequency_penalty 0.2, max_tokens 1024.
Budgets: 12 steps, 900 seconds, 120 seconds per API call, one invalid-reply
correction per step and one unexecuted-target recapture per step. Visual settling
uses at most three checks separated by 0.5 seconds. Full settings and exact
runtime source snapshots are retained in each run. These are initial learning
settings, not a measured optimal configuration or finalized baseline.

## Experiments and official outcomes

| Experiment | Evidence | Outcome |
| --- | --- | --- |
| Saved Home screenshot | [probe](../runs/autoglm_saved_screen_20261007T200459_147152Z/result.json) | One API call selected Settings; parsed point landed inside its icon. No GUI action/verifier. |
| v1 Wi-Fi, seed 42 | [summary](../runs/trial_SystemWifiTurnOn_20261007T200520_214952Z/summary.json) | Official FAIL; capture failed before any model call/action. Preserve as infrastructure failure. |
| v2 Wi-Fi, seed 42 | [summary](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/summary.json) | Official PASS; initial verifier 0, final 1; 12 GUI actions and 13 API calls. Agent did not declare finish. |

The v2 run lasted 86.094 seconds from the recorded run start, including setup,
loop, verification and recording finish. Agent-phase duration was 83.375 seconds.
API waits totalled 30.533 seconds (median 2.25 seconds). No reply hit the output
cap, and no invalid-reply correction was needed. The extra API call was a fresh
decision after step 2's target changed while Settings was loading.

These two versions give two official attempts, one PASS. The current v2 version
has one PASS in one attempt; neither count establishes repeatability. Do not
merge these trials into the frozen GELab v10 batch or claim an isolated model
improvement: model, prompt/action interface, observation and sampling changed.
Camera, Timer, Contacts and Clipboard were not evaluated with AutoGLM here.

## Useful recovery and remaining model error

At step 2, the first screenshot showed Settings' launch screen. The model
proposed tapping its center. Before dispatch, the local target image changed
by 0.296; the guard discarded that unexecuted choice. A new screenshot/request
selected Network & internet. This is an observed recovery, not action replay.

The agent subsequently reached Internet and toggled Wi-Fi repeatedly. In
[step 9's actual input](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/step_009/observation_0/screen.png),
the switch is blue with its thumb on the right: Wi-Fi is on. The
[reply](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/step_009/observation_0/response_0.json)
incorrectly calls it off and taps it again. Replies also describe a tree that
was not supplied. This is a model visual-state/stopping error despite a useful
screenshot, not evidence that all these inputs were stale. The final screenshot
and video show Wi-Fi on, matching the official verifier.

The run stops at its step budget with `agent_done: false`. Do not describe it as
clean autonomous completion. The next small experiment should address recognition
of the already-satisfied visible state and stopping, while preserving GUI-only
execution and independent verification. No further trial or prompt change was
made after this result. The earlier Camera readiness and multi-task value errors
remain unresolved; this Wi-Fi outcome cannot establish their repair.

## Evidence audit and local services

All 12 executed steps have action, execution-start, result and after-screen/tree
files; all 13 requests have provider responses. Both trial videos decode: 767
frames for v2 and 26 for the infrastructure failure. Decoding does not establish
gap-free timing. The v2 video's extracted final frame also shows Wi-Fi on.
See [audit and analysis](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/analysis.json),
[readable trajectory](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/trajectory.txt)
and [video](../runs/trial_SystemWifiTurnOn_20261007T200901_584580Z/video_001.mp4).

Five offline adapter tests passed: coordinate bounds, rejection of executable/
multi-action text, ordinary focus plus exact Type, unrelated suggestion changes,
and changed-target/modal rejection. Python compilation and launcher `-CheckOnly`
also passed. These do not replace real task evaluation.

Ollama's app and server were stopped at the user's request. No inference model
was loaded when inspected; remaining GPU allocation was 2281 MiB immediately
after shutdown, and 2387 MiB at the final check. There were no remaining identified
local model processes. Emulator/display use remains; do not claim zero GPU/RAM
allocation. The process shutdown record is in `.tools/local_model_shutdown_20261007.json`.

Automatic approval review initially rejected screenshot transmission. The saved
Home image was inspected and approved on retry. The user then explicitly
authorized successive test-emulator Home/Settings screenshots to Z.ai for this
Wi-Fi trial; the corrected run proceeded under that approval. Credentials stayed
out of requests, logs and source snapshots.
