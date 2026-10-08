# Course and primary-source review, 8 October 2026

This review precedes another live trial. The user's new rule is mandatory:
on failure, stop, inspect the actual trajectory, record the cause, correct it,
then run a bounded regression. Do not repeat an unchanged failed task or start
another broad batch to rediscover the same failure.

## First four days: requirements applied to this project

Read all extracted pages: D1 51, D2 52, D3 32, D4 39. Originals and page-numbered
extractions are preserved under course_content and .review/materials. Reviewed
the actual diagram on D2 p.36 and the rendered rule-stacking/recovery slides.
Also reread the supplied minimal_agent_example.py and D2 step3_skill_status.py.

| Source | Engineering requirement | Application |
| --- | --- | --- |
| D1 pp.6–8 | One agent/step(), easy/medium/hard, three runs each, video/trajectory/failure analysis | Warm-ups are preliminary; retain the agreed Markor/Calendar/harder-task scope. |
| D1 pp.27,35–41,49–50 | Validate output, observe real effects, bound loops, ground with actual GUI, classify failures | Keep checked pseudo-calls, fresh GUI state, bounded correction and independent verifier. |
| D2 pp.6–14,22–26 | Goal/rules/current state, ordered history, stable prefix, avoid rule stacking | Replace accumulated task recipes with the upstream contract and short visible completion criteria. |
| D2 pp.34–39 | Code-maintained factual status, preserve original context | Report actual observed GUI state/last effect, never invented progress or a computed next task action. |
| D3 pp.4–7,19–20,30–31 | Harness checks/executes; clear action and observation contracts; inspect result | Keep model-selected actions, exact inputs, one execution and before/after evidence. |
| D4 pp.10,15–18,23–27 | Classify failure, bounded recovery, verify the change; repeated valid calls need not progress | Stop the scheduler at the first failed clean gate, inspect its trace before any new run. |
| Course minimal example | A small direct entry point, explicit request/response and flushed trace | run_task.py remains independently executable with project Python; no extra framework. |

## Official GitHub sources and limits

Pinned public files, commits and SHA256 hashes are in
[the source manifest](sources/pinned_upstream.json).

- [Open-AutoGLM English prompt](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/config/prompts_en.py): native single-line do/finish; Type means the currently focused input field. Preserve this contract rather than invent a keypad exception.
- [Open-AutoGLM agent](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/agent.py): one screen per decision, goal on first turn, ordered assistant history, remove prior images, reset each task.
- [Open-AutoGLM model client](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/model/client.py): image-first user content; temperature 0, top-p .85, frequency penalty .2, output cap 3000. Our 1024 cap differs and caused saved Clipboard truncations; adopt 3000 as a documented protocol repair, not speed tuning.
- [Open-AutoGLM action handler](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/actions/handler.py): focused text clear/type, no implicit Enter. We retain official Android World GUI helpers and the existing Windows adapter instead of installing another control stack.
- [Android World M3A](https://github.com/google-research/android_world/blob/main/android_world/agents/m3a.py): real screenshot/GUI/history, completion when desired state already holds, easiest available route, revise after repeated failure, exact text selection before Copy.
- [Android World base agent](https://github.com/google-research/android_world/blob/main/android_world/agents/base_agent.py): one step returns AgentInteractionResult; post-transition observation may use a fixed pause. Our bounded visual settling remains the recorded repair for this emulator's idle-capture failure.

Upstream also treats some parser/execution errors as finish. We keep errors
distinct from model completion because that is a project evaluation requirement.
Native coordinates remain normalized; checked GUI centers are observation data,
not a hardcoded task replay. The prompt adaptations and their sources are listed
with the runtime version, not represented as verbatim upstream behavior.

## Latest failures: diagnosis before another run

| Trial | Evidence | Cause and next correction |
| --- | --- | --- |
| Timer v20 seed42, step5 | Actual buffer20; model chooses7 for target200701 | Model digit-sequencing error despite correct centers; repeated literal/example prompt probes failed. More examples are not an established fix. |
| Timer v21 seed42, step3 onwards | Empty GUI; reply chooses individual taps despite new Type guidance; final207010 | Contradictory prompt: generic text-field Type/Clock Tap versus proposed keypad Type. v22 was edited but never run. Withdraw that experimental keypad extension; use the official contract and concise goal context. A manual keyboard diagnostic proves app behavior only, not upstream best practice. |
| Clipboard v20 seed43, step4 | Long Press [499,168] lands on a search suggestion below the actual field | Grounding, followed by repeated Wait; add Chrome's checked fresh editable/focused GUI centers using the existing paired observation method. No direct clipboard access. |
| Contacts v20 seed42, step12 | Save executes, officialPASS, budget ends without another decision | Budget/control limitation; allow16 Contacts steps so the model can inspect saved GUI and finish. Others remain12. |

v20 Wi-Fi and Camera already passed 3/3 clean each. Do not rerun those unchanged
tasks merely to fill another broad batch. Validate remaining corrections in
bounded regressions, then repeats. If the same failure survives the repair,
inspect and record it before doing anything else; do not claim success.

## Implemented v23 before the regression

The English prompt is extracted as data from the pinned upstream source, with
the date omitted for a stable prefix. Explicit adapter details and sourced M3A
completion/recovery/Copy guidance are appended. Native Type again requires a
focused editable field when fresh GUI elements are available: the experimental
Clock exception is removed, not hidden behind another prompt. Completion rules
are short observable goals, with no Chrome/Clock task replay. The original task
and exact values are sent once; later turns contain factual observations and
actual action effects. Original full logs remain preserved. The 3000-token cap
matches upstream and fixes a documented output-contract limitation; sampling
probabilities, elapsed-time bounds and retry counts are unchanged.

The scheduler now stops on the first failed clean trial even without the legacy
--require-model-finish flag and returns a nonzero exit status. No other task
starts after that failure. Fourteen offline adapter checks pass before live
regression; the new noneditable-keypad check verifies the withdrawn exception.

## Recorder startup failure before model calls

v23 Clipboard seed43, trial_SystemCopyToClipboard_20261008T075509_257918Z,
failed with zero model calls/actions: the fixed one-second startup check saw no
screenrecord PID. The trace records invalid evaluation and no video. Emulator
storage had 8.8GB free; a later check found the delayed recorder still running.
This supports a recorder startup/readiness race, not a model copy failure.
v24 changes recording readiness only: bounded PID polling, confirm its command
contains this run's remote filename, and never release GUI execution before it
is ready. Recover the orphan clip separately without changing the original
invalid summary. No model task replay and no model/prompt change in this repair.

v24 recording succeeded, but Clipboard seed43 stopped before GUI execution:
step1 selected unavailable Settings twice. The correction said only "use an app
available for this task" without repeating the valid values. The pinned prompt
also uses Settings as its generic Launch example. Diagnose this as model
wrong_app plus weak validation feedback, not the previous long-press grounding
failure. v25 changes the example to an app-name placeholder and includes the
actual allowed list in the validation error. This follows D3 pp.9,19 and D4 p.15
(clear argument contract and useful error). No unavailable action was executed.

v25 Clipboard43 then ran12 steps without copying: its action history alternates
Launch Clipper and Back. Clipper is a background broadcast service used by the
official initializer/verifier, but our action catalog listed it as a GUI app.
The model selected an advertised operation that cannot supply an editable UI.
v26 excludes this infrastructure service from model-facing GUI apps; official
setup/reset/verifier still use it. Chrome remains the available GUI input app.
This is an action-space correction supported by D3 pp.10,19 and the installed
SystemCopyToClipboard implementation, not a hardcoded GUI replay. The raw run
is preserved and not reclassified as a successful copy.

v26 reached Chrome's focused address field but rejected the model's correct Type
at steps3/4/5. The saved XML says class=android.widget.EditText and focused=true;
Android World's XML parser leaves is_editable=None because UIAutomator does not
supply that field. Our guard wrongly treated unknown as false. The screenshot
shows the cursor and keyboard. v27 derives editability only for the actual
standard EditText class when the flag is missing, records that provenance, and
renders editable/focused properties in the model observation (previously they
were in JSON but omitted by control_notes). Android's
[EditText reference](https://developer.android.com/reference/android/widget/EditText)
defines this editable text control. Unknown/custom noneditable controls remain
rejected. Test the saved-class boundary before the bounded regression; no new
task procedure or guidance is added.

v27 typed the exact email successfully, then called Tap on Clear input while
its reply called that control Copy. The next GUI field became empty; the model
misread the unrelated existing "Text you copied" suggestion as completion.
Official FAIL with model finish is false_done. Our result omitted the selected
control label and retained only Tap, weakening execution feedback. v28 includes
the actual fresh GUI control label/resource in the result, following D3 p.19
and D4 p.15. It does not compare with the goal or override an action/finish.
Use the saved failed screen to check this feedback change before another trial.

The [saved-state feedback probe](../runs/actual_control_feedback_probe_20261008T081535_861953Z/result.json)
still chose the same false finish despite the actual Clear input label. This
repair does not establish a Clipboard model fix. Do not run another unchanged
Clipboard trial or invent another task recipe. Preserve the failure and inspect
remaining independent bounded regressions. Actual-control feedback remains
useful factual logging, with no claim that it solved this model error.

v28's independent regressions: Contacts42 passed with model finish in11 steps
and officialPASS. Timer42 failed: step5 read observed buffer20 correctly but
selected7 instead of the required0, with actual GUI target7 correctly logged.
It eventually filled20h71m02s, then cycled among digit taps that could no longer
change the full entry. Final officialFAIL, no model finish. This remains a model
duration-entry/recovery failure under the reviewed native contract. Do not
repeat Timer unchanged or invent another digit prompt. Finish only the two
independent Contacts repeats using the same frozen sources; no broad batch.

Contacts43/44 also passed, eleven steps each, with identical v28 source hashes:
the reviewed Contacts gate is3/3 clean. v29 changes only the no-progress limit
after those repeats finish. Three consecutive unchanged results followed by a
repeat of any action in that short cycle stop with a control_no_progress error.
The earlier same-action bound remains. A new recovery action is allowed, small
actual GUI changes count as progress, and model finish is never overridden.
This follows D4 pp.26–27 and is checked offline against the concrete recorded
Timer cycle plus recovery/finish boundaries. It does not fix the model's wrong
duration or Clipboard false_done, so neither task is rerun unchanged. Current
v29's cycle guard has offline verification; the successful live gates are the
explicitly named v20/v28 versions. Do not claim current15/15.
