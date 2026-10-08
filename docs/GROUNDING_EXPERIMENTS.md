# Tree-first learning experiments

Latest recorded Contacts trial: `trial_ContactsAddContact_20261007T173637_269613Z`, official FAIL, initial 0.0/final 0.0, 12 steps, 12 calls, 119.75 seconds, no manual intervention.

Current experiments and limits: [PERFORMANCE_AND_TRAJECTORIES.md](PERFORMANCE_AND_TRAJECTORIES.md). Preserve earlier failures below.

## Earlier record (historical)

## Independent execution follow-up

- `trial_ContactsAddContact_20261007T164836_344369Z`: v2, initial 0/final 0,
  official FAIL after five executed actions/6 calls, 77 s. The freshness stop
  compared an unlabelled/noninteractive cursor-handle FrameLayout that vanished;
  the selected index-7 field was unchanged.
- `trial_ContactsAddContact_20261007T165206_708350Z`: v2_1 excludes decoration
  while retaining full labelled/interactive controls in the signature. Replay
  checks accept the observed cursor disappearance and reject changed target
  bounds. Live run: initial 0/final 0, official FAIL, 12 GUI actions/13 calls,
  156.875 s, one image fallback at step 8, stop at step budget. No freshness
  error recurred. Repeated name-field taps triggered the image, which tapped
  the keyboard space; step 11 selected index 19 (Dash) instead of a form field.
  Final values: First name `Camila da Silva `, Phone `-+10433218196`; unsaved.

Both videos decoded to EOF: 578 and 858 frames respectively. No reported
recording errors or manual interventions. Launcher execution, logs and verifier
worked independently; task reliability is not established. Contacts learning
total is now 1/7 across different versions, not a frozen-baseline estimate.
The guard fix removed the measured false stop but did not improve task success
in this repeat. Proposed next change: targeted TYPE(field index, exact value)
using the existing Android World action contract, followed by a controlled test.

## Context repair: first verified success

`trial_ContactsAddContact_20261007T160201_407078Z`, version
`learning_context_feedback_v2`: official initial score 0/final score 1, agent
COMPLETE, 10 dispatched GUI actions, 11 calls, 157.67 seconds, no interventions,
zero image fallbacks. Same model, GPU setting, sampling, seed, task values,
JSON action schema and budgets as the previous JSON trial.

Changed together: semantic action/results history; general instructions in
`instructions/agent.md`, including Android World's automatic Enter after TYPE;
conditional inline contact procedure; repair of the missing official app snapshot.
Consequently the earlier FAIL versus this PASS is a diagnostic comparison with
confounders, not a controlled estimate of any one change's benefit.

Step 2 selected battery index 7 while describing a create-contact button;
step 3 selected the notification Allow button while describing a name field.
The model recovered, entered the complete name at step 7 and phone at step 9,
selected Save at step 10 and completed at step 11. Its `verify` text frequently
remains predictive, so it is not our success evidence. The final observed screen
and official contact verifier agree on the saved name/phone.

The video decoded to EOF: 866 frames, 540x1200, final frame timestamp 144.28 s.
The static final screen continued through the approximately 158 s trial;
decoding alone does not prove continuous recording coverage. No recorder error
was reported. Raw video, actions, requests and source snapshots are preserved.

A screenshot-with-tree request option was prepared after the wrong-index
choices. It was not exercised after tree success, and is disabled in the retained
configuration. Current Contacts learning total is 1/5 across mixed versions,
not a baseline success-rate estimate. Final evaluations and controlled guidance
comparison are pending. See `AGENT_WALKTHROUGH.md` for the understandable loop.

7 October 2026. Basic tasks use accessibility-tree observations and index
grounding, as chosen by the user. Screenshots are conditional fallbacks. Saving
a screenshot for review is different from sending one to the model.

## Implemented policy

- Each step starts with a fresh compact tree and its original indices. Code
  resolves the chosen index to that observation's bounds.
- Switch to an image when no labelled visible controls have bounds, validation
  still fails after correction, or a third identical action would repeat on an
  unchanged tree.
- At most two image fallbacks per learning run. One invalid-output correction
  is shared across modes: invalid tree + correction + one image request is at
  most three requests. These provisional limits are not course requirements.
- Log mode/reason/request/action. Stop on exhausted fallback budget, recording
  failure or changed UI. Do not automatically replay uncertain execution.

## Saved-screen evidence

Two trees: Contacts with First name selected and keyboard visible, and the
launcher where Settings had not opened. Explicit probes requested TYPE `Camila`
and opening Settings. No Android actions executed. Same BF16 model, 16 GPU layers,
temperature 1, top-k 20, top-p .95, context 4096, output cap 256, seed 42.
Three repeats per case; these are tiny fixed-seed interface tests, not task runs.

| Interface | First valid | Intended action first | Valid after correction | Intended after correction |
| --- | --- | --- | --- | --- |
| Native base, tree contract | 3/6 | 3/6 | 4/6 | 3/6 |
| Same plus three examples | 3/6 | 0/6 | 3/6 | 0/6 |
| JSON prompt plus engine schema | 6/6 | 6/6 | 6/6 | 6/6 |

Native run: `prompt_tree_20261007T152216_674313Z`. A/B order alternated; examples
were the sole within-comparison change. They worsened this result and were
rejected. No excluded warm-up was run; raw load/prompt/generation timings remain.
Aggregate wall time does not establish a controlled speedup.

JSON run: `json_tree_20261007T153232_202294Z`. This changed the output interface
package (prompt and decoding schema), not examples alone. It ran afterward;
ordering/cache effects were not balanced against native. Do not infer broad
reliability or task success from six replies on two screens.

D1 p.27 recommends constrained decoding. Installed Ollama accepted the JSON
schema and produced usable replies. See
[official documentation](https://docs.ollama.com/capabilities/structured-outputs).
This adapts GELab output rather than reproducing its native tab protocol. Code
still rejects duplicate keys, wrong types/actions, invalid targets, disabled
controls, unknown apps, and excessive waits. Valid JSON can make wrong decisions.

## Recorded Contacts trials

| Version | GUI actions | Model calls | Image fallbacks | Verifier | Seconds |
| --- | --- | --- | --- | --- | --- |
| Native `learning_tree_first_v1` | 2 | 8 | 2 | FAIL | 121.36 |
| `learning_tree_first_json_v1` | 8 | 9 | 0 | FAIL | 100.94 |

Run IDs: `trial_ContactsAddContact_20261007T152803_891284Z` and
`trial_ContactsAddContact_20261007T153448_933813Z`. Official seed-42 initialization,
initial score zero, videos, no manual intervention. A missing Contacts app snapshot
warning followed emulator restart; provider initialization worked. This is a
setup/reproducibility limitation: GUI/onboarding states across older runs are
not assumed perfectly matched.

Native exhausted fallbacks at step 3. JSON parsed every reply and executed eight
GUI actions: opened Contacts, entered the form, selected First name and typed
`Camila`, selected Last name and typed only `da`. The task requires
`Camila da Silva`; `Silva` was lost despite exact parameters in context. No phone
was entered and no contact saved. Step 9 selected Cancel but did not execute,
because the freshness guard detected changed UI. Completion false; official score 0.

Version 1 did not save the exact fresh observation causing that stop, so the
changed element cannot be identified from its logs. Version 1.1 now saves fresh
execution trees and mismatch screenshots; the guard is unchanged. This logging
change has not been evaluated as a behavioral improvement.

Formatting/progress improved; task success remained 0/1 in both versions.
Overall valid learning results: Contacts 0/4, Wi-Fi 0/1, excluding the earlier
already-satisfied Wi-Fi PASS. Final repeated evaluations are pending.

## Next experiment and checks

The partial surname supports testing one short reusable contact workflow guide:
preserve the complete name/phone, check fields before Save, and check the saved
result before completion. Load it explicitly; no seed-specific answers or tap
positions. It has not been loaded/tested yet. Capture a real fresh-state mismatch
before relaxing or expanding stale-target recovery.

Offline boundary checks in `.review/test_grounding_policy.py` use mocks, not task
results. They passed original index mapping, no images in tree requests, a shared
correction budget, stopping after invalid fallback, duplicate-key/type/action and
disabled-target rejection, and exact phone text. Dependency/syntax checks passed.
