# AutoGLM completion repair — 7 October 2026

**Latest continuation, 8 October:** source-backed v29 supersedes experimental
v21/v22 keypad guidance. Read [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md)
for the complete D1–D4/GitHub mapping and failure → diagnosis → fix → regression
ledger. v20 Wi-Fi/Camera each3/3 and v28 Contacts3/3 remain valid recorded
task-specific gates. Current Timer/Clipboard three-clean gates are incomplete.
Clipboard's latest model false_done survived a saved-state feedback probe, so
no unchanged live retry is justified. The source/native action contract, useful
errors, correct GUI app catalog, observed EditText recognition and bounded
recorder readiness repairs are implemented. All original failures are retained.
Sixteen offline checks pass. v29 bounds unchanged action cycles after the v28
repeats finished; it does not repair digit sequencing or false completion and
has no live success claim. No batch is running. See
[WARMUP_RESULTS.md](WARMUP_RESULTS.md) for all final gates and limitations.

The requested behavior is a model-issued `finish(...)` after the task's observed
final state, followed by independent official Android World verification.
A verifier PASS reached at the step limit does not satisfy this stopping goal.
Python does not feed the verifier score to the model or force task completion.

## Evidence and small changes

The original v2 Wi-Fi trial, `trial_SystemWifiTurnOn_20261007T200901_584580Z`,
had official PASS but no model finish after 12 steps. At step 9 the model called
a visibly enabled switch OFF and tapped it again. This was a state-recognition
error, not simply a missing step budget.

Explicit task completion conditions were added to the system and user messages.
Saved-screen tests still misread ON as OFF; original-resolution images did not
fix it. A native-history probe finished on both ON and OFF, so it failed to
distinguish true completion from false completion. All probe requests, images
and replies remain in `runs/autoglm_*probe_*`; none dispatched GUI actions.

Version v4 supplied a fresh Settings UI dump, including `checked=true`, alongside
the screenshot. Two fully recorded trials (seeds 42/43) still toggled Wi-Fi and
reached 12 steps without finish. Both had official PASS, but **zero clean
finishes out of two**. See [v4 raw results](../runs/easy_batch_20261007T203058_370014Z/RESULTS.md).
The scheduler stopped before seed 44 on its source-change guard when the next
implementation was prepared; existing trials used their original loaded code,
prompt and saved settings. Do not combine these trials with a later version.

The switch had no text of its own in Android's XML. Version v5 attaches the
containing GUI row's actual visible label and renders the observation concisely:
`Wi-Fi: switch ON (checked=true)` or `Wi-Fi: switch OFF (checked=false)`.
It does this generically for checkable controls; it does not inspect hidden
Wi-Fi settings or decide whether a benchmark task has succeeded.
The actual runtime prompt correctly finished on recorded ON and chose a tap on
recorded OFF in [the saved-state probe](../runs/autoglm_current_completion_probe_20261007T203552_910199Z/results.json).
This probe establishes discrimination on those saved states, not live reliability.

## Observation and action contract

One agent still performs observe → model → parse/check → GUI action → observe.
Official screenshot-only capture remains the base backend, avoiding the crashing
forwarder and animated Home widget's UIAutomator idle failure. Only configured
app packages receive supplemental UIAutomator observations. Each dump uses a
unique generated file, checks the dump/read responses and XML, and pairs it
with a fresh screenshot only if the scene remained visually unchanged. Changing
or unavailable XML falls back to the current screenshot and is logged.
This visual comparison is a practical guard, not proof of atomic capture.

The screenshots still ground normalized coordinate actions. Selected-target
freshness remains local rather than comparing the whole tree, so unrelated
clock/keyboard changes do not automatically invalidate a target. No uncertain
dispatch is replayed. Each function remains explicit with a concise docstring.

Every task has a visible completion condition: Wi-Fi enabled; exactly one new
photo; exact unstarted timer; saved exact contact; exact text copied through a
real editable GUI. Official task initialization and verification remain separate.
Clock's official verifier requires GUI duration elements, so the runner supplies
its existing UIAutomator backend only while verifying inside DeskClock, then
restores the screenshot backend. Verifier errors remain ERROR rather than false
PASS/FAIL; verifier feedback is not sent to the model.

## Evaluation gate and reproduction

`clean_agent_success` requires valid initialization/recording, official PASS,
model finish, completion stop reason and no runtime error. The older
`verified_agent_success` field retains its original verifier-PASS meaning.
The scheduler shows both counts and supports `--require-model-finish` to stop
after an unsuccessful clean completion. The requested next stage is three
fresh Wi-Fi runs (seeds 42/43/44), then the other warm-ups if that gate passes.

```powershell
& .venv\Scripts\python.exe -X utf8 run_task.py --task SystemWifiTurnOn --seed 42
& .venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks SystemWifiTurnOn --require-model-finish
& .venv\Scripts\python.exe -X utf8 -m unittest test_autoglm_adapter -v
```

Seven offline checks passed, including faithful true/false switch observations,
discarding XML after a screen transition, argument safety, exact typing and
target freshness. The `.env` key remains outside logs/source snapshots. No new
packages, agent framework, fixed GUI action replay or local-model service is
required. Live results will be recorded below without replacing earlier evidence.

## Sources

Adapted the native action/message contract from the official
[Open-AutoGLM client](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/model/client.py)
and [English instructions](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/config/prompts_en.py).
Its message builder also places the image before text; that ordering was already
correct in this adapter. Reviewed the official
[Android World T3A instructions](https://github.com/google-research/android_world/blob/main/android_world/agents/t3a.py)
for checking whether a goal is already satisfied, and the installed official
Clock task/verifier, controller, UI representation and action executor.
The custom labeled-state supplement is our measured adaptation, not an upstream
claim that AutoGLM handles every screenshot correctly.

## Live Wi-Fi gate

The frozen v5 batch [easy_batch_20261007T203707_388358Z](../runs/easy_batch_20261007T203707_388358Z/RESULTS.md)
passed **3/3 (100%)** official verifications and **3/3 model-issued finishes**.
Seeds 42/43/44 each used five steps: four GUI taps, then finish. Full durations
were 65.77, 62.42 and 62.56 seconds. Each started with verifier 0 and ended with
verifier 1, with no recorded manual intervention, runtime or recording error.
The saved tree transition shows Wi-Fi OFF → ON and no subsequent toggle OFF.
The videos decode, all expected step artifacts exist, saved sources match the
batch fingerprints, and the private key is absent from readable artifacts.
The final video frame was inspected and shows the enabled switch. See the
[audit](../runs/easy_batch_20261007T203707_388358Z/audit_20261007T204120_839572Z/artifact_review.json).
Three runs are a small sample; this establishes the requested gate, not broad
reliability. Compared with v2/v4, prompt wording and observed-state presentation
changed; do not describe this as a prompt-only improvement.

## First other warm-up and infrastructure repair

Camera seed 42 in [easy_batch_20261007T204109_047689Z](../runs/easy_batch_20261007T204109_047689Z/RESULTS.md)
failed (12 steps, no finish, official score 0). The screen stays at Camera's
loading icon, and the model invents a shutter there. This is the previously
recorded readiness failure plus an incorrect model interpretation. The scheduler
stopped before repeating it. Its video/artifacts were audited and preserved.

Read-only camera diagnostics found repeated `Camera3-Stream` errors with the
same negative, non-increasing frame timestamp. The AVD's rear camera was
`virtualscene`; front was `emulated`. A bounded infrastructure experiment restarts
the same AVD with `-camera-back emulated -camera-front emulated`, leaving the AVD
files intact. Android's official command-line documentation supports these
[camera overrides](https://developer.android.com/studio/run/emulator-commandline).
Diagnostics and exact launch flags are in `runs/camera_infrastructure_20261007`.
The first relaunch raced the old emulator's shutdown; a second launch after exit
is retained separately. No photo was injected and no shutter was executed as
an infrastructure action. New task trials still use official initialization.

The software-camera retry (`trial_CameraTakePhoto_20261007T204534_946005Z`)
showed a real preview and a new thumbnail after the first shutter tap, confirming
the loading symptom improved. It still failed: the model repeatedly pressed the
shutter instead of finishing. The old semantic history recorded only `Tap` and
lost the distinction between onboarding and capturing. The retry's complete
source/video/audit remain in [its batch](../runs/easy_batch_20261007T204534_402262Z/RESULTS.md).
Changing the backend is an infrastructure experiment; it does not by itself
establish Camera agent success or isolate the emulator bug's root cause.

Version v6 retains the last three actually executed native user/assistant
decisions, removes old images as upstream does, and supplies the newest image.
It still keeps actual observed result summaries. Rejected/stale choices and
uncertain execution are not added as executed conversation. The Camera rule
now explicitly says to finish after the first capture and a new thumbnail.
An actual-runtime saved-state [Camera probe](../runs/autoglm_camera_completion_probe_20261007T204849_578147Z/results.json)
chose a shutter tap before capture and finish after one capture. No new GUI
action was dispatched by the probe. Accepted downside: larger context and past
coordinates in native history; every live point is still checked against the
latest observation and may be reconsidered once before dispatch.

The v6 Wi-Fi check correctly chose finish at step 5, but unescaped quotes around
`AndroidWifi` made its message invalid Python string syntax. Its correction
repeated the same message. Official PASS, no accepted model finish: an adapter
validation failure, not a Wi-Fi state-recognition failure. Preserve
[the run](../runs/easy_batch_20261007T205015_923723Z/RESULTS.md).
Version v7 accepts this specific native finish-text wrapper as inert text,
following the upstream [finish-message handling](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/actions/handler.py).
Extra arguments, action sequences and executable expressions remain rejected;
GUI calls still require checked AST literal arguments. Eight offline checks pass.
Official setup that needs GUI labels now temporarily uses the official
UIAutomator backend and saves a snapshot only after `app.setup()` succeeds;
the upstream convenience wrapper can catch setup errors and cache incomplete
onboarding. Screenshot capture is restored afterward. Existing snapshots and
recorded failures remain intact. New v7 live outcomes will be recorded next.

Version v7's [frozen batch](../runs/easy_batch_20261007T205329_154297Z/RESULTS.md)
again passed three Wi-Fi trials with model finish (five steps each), but Camera
still repeatedly captured. The complete saved messages showed another native
protocol mismatch: every observation reissued `Task: Take one photo`. The
upstream loop gives the original goal once and follows it with observations.

Version v8 now keeps the full executed conversation within the existing
12-step bound, removes old images, and makes subsequent user turns observations
of the same original task. The system retains exact goal/inputs/completion
condition; it does not ask for a new photo each turn. This replaces v6/v7's
three-pair window and repeated user goal. The actual Camera images/history from
the failed v7 trial passed a [before/after-one probe](../runs/autoglm_camera_completion_probe_20261007T205922_587512Z/results.json)
with this format. Its first new live Camera trial, seed 42, passed the official
verifier and issued finish after four steps in 25.25 seconds. The additional
repeats and other warm-ups are in
[the v8 batch](../runs/easy_batch_20261007T205955_772699Z/RESULTS.md).
Do not count the earlier false/cyclic Camera runs as successful repeats.

## Remaining warm-ups, 8 October 2026

The completed v8 batch established Camera **3/3 clean finishes**, each in four
steps. Timer then failed: a native coordinate tap intended as `0` hit `00`,
and the model also skipped or repeated requested digits. v9's exact input string
did not resolve it. The [v10 batch](../runs/easy_batch_20261007T210910_435797Z/RESULTS.md)
supplied actual Clock GUI labels and repeated the original input contract:
Timer **1/3 clean**, Contacts **0/3 valid evaluations**, Clipboard **0/3 clean**.
These results remain preserved; they are not a successful warm-up batch.

Contacts failed before initialization, recording or model calls. Official app
setup tried to dismiss an absent optional notification permission dialog. Its
historical summaries call this a validation error; this review classifies it as
an **environment setup failure**, not a model failure. Clipboard used Chrome,
but our stock Android World text action appended Enter, changing the screen
instead of leaving the exact text in its editable field. Native AutoGLM Type
does not add that submission. Timer seed 42's saved GUI proves `0` and `00`
have different bounds; image-coordinate estimates selected the wrong control.

**Correction from the v13 live capture:** the earlier "absent dialog" diagnosis
was incorrect. The permission dialog is visible and its button uses `Don’t allow`
(U+2019), while upstream searches for `Don't allow` (ASCII). The
[v13 bounded attempt](../runs/easy_batch_20261008T054913_432009Z/RESULTS.md)
failed before any model call and preserved the actual setup image/tree.
v14 handles only that observed Contacts notification dialog through its fresh
GUI bounds, then requires the ready main `Create contact` control before saving
the official snapshot. This is environment onboarding, not benchmark completion.

Current v13 is a bounded repair, awaiting remaining-task live evaluation:

- Accept only the known absent Contacts notification dialog, and only after a
  fresh official GUI tree proves the main `Create contact` control is available.
  Preserve the setup image/tree and save the official snapshot afterward.
- Replace focused text through official Android World ADB typing helpers without
  appending Enter. Selection/deletion are fixed checked keyboard operations.
- When the actual Clock timer keypad tree is present, require an exact visible
  clickable label for Tap. Resolve its current bounds; ambiguous or absent labels
  fail validation. One correction is allowed. The model chooses each digit,
  correction and finish; Python supplies no next digit or verifier result.

Eleven offline safety/freshness/action checks pass. Actual GUI label/state changes now count as observed progress even when small timer digits affect very few pixels. This does not establish live
success. An automatic approval review rejected new Contacts/clipboard API trials
because the explicit earlier screenshot approval covered Home/Settings. Broader
test-emulator screen and synthetic-input approval was then explicitly granted
by the user's "Yes you can" reply on 8 October. No rejected trial was run through
a workaround. Bounded v13 live trials resumed after that approval.

A [v12 Wi-Fi regression](../runs/easy_batch_20261008T054552_376254Z/RESULTS.md) passed in five steps with model finish and official PASS. Its audit found matching frozen sources, no missing artifacts, valid JSON, no logged credential and a fully decoded video. Standalone run.ps1 -CheckOnly also passed from outside the project directory on 8 October. Ollama was absent from the host process check. These checks do not replace pending Contacts/Timer/Clipboard trials.

The v10 artifact audit found matching sources, no missing completed-step artifacts, valid JSON and no logged API credential. All six recorded Timer/Clipboard videos decoded. Its aggregate videos_decode=false includes the three Contacts setup-invalid attempts, which never reached recording; those are expected absent videos, not damaged recorded trials.

## Bounded continuation after approval

Contacts v14 passed seeds 42/43/44 with model finish and official PASS: 12/11/11
steps, 95.78/60.50/63.64 seconds including setup. Seed 42 is in
[the bounded batch](../runs/easy_batch_20261008T055051_343225Z/RESULTS.md);
the [two repeats](../runs/easy_batch_20261008T055326_952249Z/RESULTS.md) use identical
source hashes and settings. All three are recorded and unattended. The same
bounded batch preserved Clipboard's empty-field tapping failure.

Clipboard v15 clarified that the target must first be typed, without submitting
Chrome. It then selected the entire target and tapped Copy: official PASS.
It still did not finish, and tapping Gboard's copied-text chip pasted a duplicate
back into the field. Preserve
[the PASS without finish](../runs/easy_batch_20261008T055645_206545Z/RESULTS.md).
v16 explains that Copy's disappearing selection toolbar and new clipboard chip
are completion evidence; the chip must not be tapped. Its first Clipboard
attempt instead chose unavailable Messages and failed validation before any GUI
action. A saved-Home probe changing only the model-facing `clipboard_content`
key to `text_to_copy` chose Chrome, avoiding the mistaken existing-state reading.
A consistently updated saved after-Copy probe then chose finish. Original task
parameters and raw logs remain intact; this is goal wording, not clipboard-state
feedback. The probes do not count as live successes.

The Timer exact-label-only format was not adopted as the final protocol: a
saved-state probe still returned coordinates after one correction. v16 retains
native coordinate Tap and supplies actual Clock GUI tap centers beside observed
labels. Its instruction asks the model to compare the current displayed digits
with the requested HHMMSS input prefix and choose each next key itself. The
[first live case](../runs/easy_batch_20261008T060217_159970Z/RESULTS.md), seed 42,
passed in nine steps with exact **20h 07m 01s**, unstarted, and model finish.
Further repeats are pending. No Python next-digit computation or verifier result
is supplied to the model.

The v16 Timer repeats yielded seed 43 PASS/finish and seed 44 FAIL/no finish:
**2/3 clean**, not three successes. Seed 44's step 8 appended a fifth `3` to the
five-digit correct prefix `13333`; the six-digit display became `13h 33m 33s`.
Subsequent `4` taps could not change a full keypad. All coordinates now matched
their intended observed key; this remaining failure was digit-position reasoning.
v18 renders the actual GUI display as an unpadded digit string and its count,
without comparing it to the goal or selecting an action. The requested input
is numbered by position. A saved partial-entry probe chose the correct `4`, but
its full-wrong-entry probe still chose a blocked digit instead of Delete. Keep
both results: this does not establish general recovery from an incorrect entry.

Clipboard v17 copied correctly again but both subsequent replies reached the
1,024-token bound while debating a missing Gboard chip. Its source, original
replies/video and official PASS without accepted finish remain preserved.
The v18 condition makes the chip/toast optional: full exact selection, a visible
Copy command and subsequent selection-menu closure are the GUI completion cue.
No hidden clipboard read is supplied to the model; the official verifier remains
independent. The first seed 44 trial passed with model finish; remaining v18
repeats are pending.

The first frozen v18 full batch stopped after Wi-Fi seed 43 returned a normalized
four-integer bounding box twice. Seed 42 passed; seed 43 failed validation before
any GUI dispatch. Preserve
[the stopped batch](../runs/easy_batch_20261008T062430_834075Z/RESULTS.md).
v19 accepts an ordered, nonempty, in-range model-chosen box and taps its center.
This is geometric coordinate conversion, not a new task decision. Inverted,
zero-area, out-of-range and Boolean-valued boxes are rejected. The unused
exact-label Tap extension is removed after its failed native-format probes;
ordinary point Tap remains supported. Twelve offline checks pass, including box
validation and the stateless GUI digit representation. The exact failed Wi-Fi
seed is being checked in a bounded regression before restarting final repeats.

The v19 Wi-Fi regression passed; its new full batch again passed all three
Wi-Fi seeds, then Camera seed 43 failed. The original Camera step 4 reply already
recognized the new thumbnail and chose finish, but repeated the **identical
finish call twice**. Rejecting that reply caused the correction to select another
shutter tap, followed by repeated taps until the budget. This is a parser/protocol
fault compounded by model correction behavior, distinct from failing to recognize
the captured image. Preserve
[the stopped v19 batch](../runs/easy_batch_20261008T063135_459707Z/RESULTS.md).

v20 collapses only exact duplicate native call lines (or identical answer blocks)
into one unique decision. Different actions or different finish messages still
fail validation. Execution remains once at most, never replayed; raw replies and
the duplicate count are logged. No model completion is fabricated. The original
Camera reply now parses as the finish the model actually supplied. Thirteen
offline checks pass, including distinct-call rejection and exact deduplication.

## v20 outcomes and bounded v21 repairs, 8 October

[The frozen v20 batch](../runs/easy_batch_20261008T064328_366877Z/RESULTS.md)
passed Wi-Fi 3/3 (five steps each) and Camera 3/3 (four steps each), then stopped
on Timer seed 42. The model read buffer `20` correctly but chose `7` rather than
the required next `0`. Literal-list, numbered-position and small-example probes
on that saved screen also failed. These are real model digit-sequencing errors;
the correct GUI coordinates alone did not fix them.

[Contacts v20](../runs/easy_batch_20261008T065558_880497Z/RESULTS.md) saved the
correct contact at step 12: official PASS but no model finish before the budget.
v21 gives Contacts 16 steps, leaving the other tasks at 12. This budget comes
from the observed Save path, not verifier-triggered completion.

[Clipboard v20](../runs/easy_batch_20261008T070141_600020Z/RESULTS.md) passed
seed 42 with finish, then failed seed 43. It long-pressed a search suggestion
below the editable address field and repeatedly waited for a nonexistent menu.
v21 pairs Chrome's fresh checked XML with an unchanged screenshot and supplies
observed editable/focus flags and tap centers. This extends the existing bounded
Settings/Clock supplement; it does not select a control on the model's behalf.

AOSP's [TimerSetupView](https://android.googlesource.com/platform/packages/apps/DeskClock/+/6ac43d8368e8b09c4d683d6d993e1862b4f09464/src/com/android/deskclock/timer/TimerSetupView.java)
maps physical digit keys to its visible keypad buttons. The installed Google
Clock was checked separately: [the GUI transport diagnostic](../runs/clock_keyboard_diagnostic_20261008T070742_091657Z/result.json)
typed literal `120405` through Android World's `adb_utils.type_text` and observed
`12h 04m 05s`, without Enter or Start. This manual diagnostic is not an agent
evaluation. Its first attempt stopped on a stale local assertion after the final
Delete; the attempted diagnostic directory is retained.

v21 allows the model's native Type with 1–6 ASCII digits only when fresh GUI
evidence shows the Clock keypad empty. It sends the model's exact string as
normal keyboard input, skips editable-field clear commands, and never adds
Enter. Freshness checks include the actual display. A nonempty keypad rejects
Type; model-chosen GUI Delete/Tap remains available. Python neither computes the
next digit from progress nor chooses the task action. The model receives the
original HHMMSS input value, inspects the real resulting display and chooses
finish; the official verifier runs independently afterwards. Fourteen offline
checks pass. Bounded live regressions precede the remaining repeat gate.

The preceding v21 keyboard extension is historical: v21 failed and v22 was
edited but never evaluated. Following the user's source-review correction,
v23 withdrew the keypad Type extension and long task recipes. The diagnostic
proves app keyboard support only; it is not evidence of recommended upstream
AutoGLM usage or a successful model trial. Current native Type again targets a
focused editable field. See the latest review ledger above for subsequent
recorder/catalog/XML faults and the preserved model false_done.
