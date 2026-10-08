# General interaction guidance experiment, 8 October 2026

The user accepted the recommendation to make reusable interaction guidance the
main design and leave task recipes optional. v37 is prepared in general_config.json.
There is still one AutoGLM agent, one decision per step and the same Python runner.
No separate reflection request, second model or framework is introduced.

## Evidence motivating the change

Project v35 Clipboard seed43 cycled through Chrome menus for 12 actions without
typing or copying. Original upstream Clipboard copied only the selected domain
and false-finished. The before/after assessment experiment also generated wrong
feedback and added calls. Those failures are preserved in
[UPSTREAM_REFERENCE_COMPARISON.md](UPSTREAM_REFERENCE_COMPARISON.md) and
[STEP_ASSESSMENT_EXPERIMENT.md](STEP_ASSESSMENT_EXPERIMENT.md).
They motivate explicit reusable selection/recovery principles and a suitable
available editor, not longer untested reasoning or another unchanged retry.

## Prepared change and limits

- [android_interactions.md](../instructions/android_interactions.md) contains
  general focus/typing, exact selection, current-target grounding, observation
  feedback, evidence-based recovery and stopping principles. Native explanation
  stays brief; native one-line do/finish output is preserved.
- Available app descriptions are factual capabilities, filtered to the actual
  allowed apps. They supply no task route, tab name, coordinates or next digit.
- task_guidance=false and step_assessment=false. v36's per-task procedures remain
  optional and are absent from v37 action requests.
- Clipboard offers Markor as its editable GUI app. Official preparation installs
  and snapshots it before benchmark initialization/actions. No direct clipboard
  write or verifier feedback reaches the agent. Full selection and model finish
  must be supported by real observations; the final official verifier is separate.
- Source snapshots include the exact interaction file, config and readable
  requests. Native point checks/freshness and existing step/deadline limits remain.

This is an integration comparison against v35: both the available editor and
model guidance change. It cannot isolate the causal contribution of either.
It also has a constrained app catalog and is not an unrestricted leaderboard
evaluation. 29 offline checks pass before the first trial. Default v35 remains
unchanged until this variant is measured and its result reviewed.

## Source basis

Pinned Android World M3A GUIDANCE recommends easiest routes, direct open_app,
exact visible text selection and revising an unsuccessful approach:
[M3A source](https://github.com/google-research/android_world/blob/2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7/android_world/agents/m3a.py).
We adapt these to native AutoGLM coordinates and Type, without changing native
reply syntax: [AutoGLM source](https://github.com/zai-org/Open-AutoGLM/blob/86f55382982fb054e8fc98ca80609dff8a2cdc3c/phone_agent/config/prompts_en.py).
The local D4 slides pp.15–18 and 23–27 cover observed effects, failure classes
and bounded recovery; D2's procedural guidance remains distinct from factual
status. These are attributed adaptations, not a claim of original upstream
policy or guaranteed improvement. Numeric keypad caution is general mechanics,
not an instance-dependent task solution.

## Bounded evaluation

First changed trial: SystemCopyToClipboard, seed43, 12 steps/900 seconds,
same hosted autoglm-phone-multilingual and sampling as v35. No manual emulator
interaction during video. Freeze sources/prompts during the trial. On failure,
inspect the original trajectory, record the first error and correct before any
changed retry. No broad batch or unchanged failed retry is authorized by success
of offline checks alone.

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task SystemCopyToClipboard --seed 43 --config general_config.json
```

Live result pending. Keep agent completion, official verification and recording
validity separate. A setup/API error is not evidence of model task competence.

## First attempt: prerequisite failure, recorded before repair

trial_SystemCopyToClipboard_20261008T120006_301144Z stopped during official
initialization, with zero model calls/actions, no video and evaluation_valid=false.
Markor setup completed. Clipper launch failed and the reset broadcast could not
access the clipboard; final verification also errored. The saved trajectory
and summary preserve this as environment_setup_error, not a model FAIL.
After stopping, package inspection returned no installed ca.zgrs.clipper;
explicit launch returned Error type3 / activity does not exist. The runner had
accepted the old Clipper data snapshot as proof of readiness. It never checked
the actual installed package. This is a confirmed harness prerequisite omission;
why the package became absent is not established by these logs. Markor setup
is not shown to have removed it. Diagnostic files are .tools/general_v37_setup_logcat.txt,
general_v37_clipper_package.txt and general_v37_clipper_launch.txt.

Correction: before using a saved app snapshot, also call Android World's
is_package_installed. Missing package OR missing snapshot requires full official
install/setup and a new successful snapshot. Record both checks and preparation
in the trajectory. Keep general model guidance unchanged for the bounded retry.

## v38 live failure: goal drift and unverified progress

trial_SystemCopyToClipboard_20261008T120410_422924Z: official FAIL (initial0,
final0), no model finish, 12 dispatched actions/14 calls, 150.141 agent seconds,
181.719 total seconds, one recorded video and no recording error. Clipper was
installed/setup by the corrected prerequisite check; Markor's snapshot was reused.

Step1 discarded an unexecuted stale target and chose Launch on reobservation.
Steps4/5 opened a file-creation dialog and tapped its actual observed OK control.
The next screenshot and GUI tree showed an empty directory, no editor and no
new file entry. Step6 nonetheless claimed my_note.md had been created and
navigated into parent folders to find it. That reply supplied two different
calls, which were rejected before one corrected action executed. Steps7–12
cycled between directories, interpreting .app as a useful route; there was no
Type, full selection or Copy. This is wrong-route/recovery and unsupported
progress inference, not a stale-label explanation for the later cycle. The
general prose rules did not repair it. The no-effect guard does not catch
cycles with changing screens. The original summary's failure_class=null is
preserved; this diagnosis supplies the trace-based classification separately.
Markor all-files app-op permits access; retained logcat contains no specific
file-creation exception. Why OK did not yield a visible file is unestablished;
the model should not have assumed success from dialog dismissal.

Context inspection also found a source difference worth testing: native history
keeps the original goal only on the first user turn, and each new observation
adds only the last actual result. The older recent_actions config is unused.
Pinned M3A action selection repeats its current goal and ordered history in
every request. A bounded next correction will retain that native history but
add the original ongoing goal/exact inputs and three actual recent dispatched
results to each latest observation. These are factual context, not a computed
plan, task route or verifier result. This is a source-backed context experiment,
not proof that the model forgot the goal (its prose still mentions copying).

## v39 context regression: no task improvement

trial_SystemCopyToClipboard_20261008T121139_680477Z repeated the file-search
failure despite current-goal/exact-input/three-result context. Official FAIL,
11 dispatched actions, 14 calls, 12 steps including finish. At step12 the first
reply supplied both Tap and finish and was rejected; its one correction issued
finish while explicitly saying the task could not be completed. Thus native
finish means the model stopped, not that it claimed a successful copy. The
summary's generic false_done/complete mapping is preserved and must be read
with that message. No Type/selection/Copy occurred. v39 therefore establishes
no benefit from the added context on this instance.

The original summary marks evaluation_valid=false because recording had not
finished within its 30-second join budget; video_001.mp4 arrived afterwards.
This recording problem is retained separately, not retrospectively turned into
a valid unattended result. Shutdown kill/pull/remove commands lack timeouts,
so the join budget does not bound recorder work. A bounded shutdown with explicit
phase timings is the next infrastructure correction, before further evaluation.
The new test initially failed because recipe assertions were inserted into the
general-context case; the live trial was launched before noticing that failure.
Only the test file was corrected during the run; runtime sources/prompts remained
frozen, and all 32 offline checks then passed. This sequencing mistake is recorded.

Next read-only/GUI capability diagnostic: inspect the installed Markor QuickNote
editor. It may establish factual available-app capabilities; it is not a task
run, does not copy a task input, and does not establish model competence.

The separate diagnostic .tools/markor_editor_diagnostic used observed Launch/
QuickNote labels, saved before/after screens and found one focused EditText.
It typed/copied nothing and is excluded from model evaluation. v40 adds the
observed fact that QuickNote is an existing editable note while Files manages
files to Markor's capability description. It supplies no task-specific procedure.
Official snapshot restoration still returns the app to its original setup
state before a new run; the diagnostic does not seed an easier starting editor.
The bounded shutdown repair now records phase timing and applies signal5s,
wait15s, pull20s and remove5s budgets; join55s covers those phases. A failed pull
retains the remote original. One final bounded Clipboard comparison tests this
changed app fact, retaining the same v39 general guidance and actual context.

## v40: correct editor choice, failed typing transport

trial_SystemCopyToClipboard_20261008T121918_952583Z opened Markor, selected
QuickNote and chose the exact task Type at step3 after correcting an out-of-range
pixel coordinate. The new capability fact changed the observed route on this
instance; it does not yet establish task success. Android World's Type helper
timed out on input text john.doe@example.com after10s on each of two internal
attempts. Source adb_controller.execute_command restarts ADB on failed attempts;
the owned recorder exited. Original result: evaluation_valid=false, officialFAIL,
2 completed actions, 4 calls, execution error and no model finish/video. The
Type is an attempted uncertain dispatch and is not included in completed-action
counts. No selection/Copy was attempted. This is an execution/recording failure,
not evidence that model selection of the editor/text was wrong.

Native Open-AutoGLM uses ADB Keyboard's focused-input clear/UTF-8 broadcast,
switching and restoring the original IME. That native transport already typed
the comparison email in the preserved upstream trial. v41 will adapt that
transport with an enabled-IME preflight, a shared bounded deadline and no retry
or ADB-server restart. It performs GUI text input only, never clipboard writes,
and adds no Enter. Keep v40 model guidance/capabilities unchanged for one bounded
changed regression. Existing Android World typing remains available in older
configs. This is a source-backed transport repair, not another model policy.

## v42 assisted diagnostic: observation recovery kills recording

trial_SystemCopyToClipboard_20261008T123647_174079Z reached QuickNote in two
actions, then an8-second UIAutomator dump timed out during observation. SDK
recovery restarted ADB and the recorder exited. OfficialFAIL but invalid
evaluation,2 calls/2 actions, no typing/copy/finish. It cannot measure assisted
completion or the native typing repair. The two different sources of SDK
timeout (input and observation) expose a common runtime recovery fault.
Installed adb_controller.execute_command hardcodes two attempts with a server
restart between them; its log misleadingly says 'of3'. Preserve this distinction.

v43 adapts that one method in the project process to preserve its command,
timeout and byte-return/error contract while executing once with no retry or
server restart. Installed dependencies remain unchanged. This applies to SDK
setup/observations/actions only in configs opting in; native reference commands
and existing old configs retain their documented behavior. Read-only XML failure
can use the existing fresh screenshot fallback, while an uncertain execution
still stops. Regression checks prove a timed-out dump invokes one subprocess
and zero restarts. Retry the assisted diagnostic only after this recorded repair,
with unchanged guidance and app facts. General route failures remain unresolved.

## v44 reset prerequisite failure, corrected before retry

trial_SystemCopyToClipboard_20261008T124920_040210Z stopped before model calls,
official initialization and video: the GUI reset requested a global UIAutomator
tree after opening QuickNote, and dump did not confirm a fresh file (idle failure).
No reset or task success was established. Do not reintroduce that mandatory
global observation path; it was already a known unreliable backend.
The v43 saved image and tree confirm corrupted stale text
john.doe@example.john.doe@example.c, which the model incorrectly read as the
complete email. This is real retained text as well as model lost_value, not
merely a claim in its reply. A read-only filename inspection identified the
actual backing file /storage/emulated/0/Documents/markor/QuickNote.md.

v45 replaces the failed GUI reset with Android World's official remove_single_file
utility, a pattern used for benchmark environment preparation. Only this exact
synthetic note is removed, after closing Markor; absence is checked and logged.
No requested task value is written and no clipboard Copy/set occurs in this
reset. The official Clipboard initializer/verifier stay unchanged. Installed
Markor uses lowercase markor here; the upstream Markor task constant uses
uppercase Markor, so blindly applying that directory constant would miss it.
This supersedes the v44 GUI-reset proposal above. Model coordinates still remain
checked; unit feedback is clearer without automatic pixel guessing. One changed
assisted trial follows the recorded preparation correction.

## v43 assisted diagnostic: grounding-unit failure and stale editor

trial_SystemCopyToClipboard_20261008T124033_256747Z: valid recorded officialFAIL,
2 executed actions/4 calls, no finish, no recording error. Step3 proposed Long
Press [540,1245], then its one correction proposed [540,1188]; both exceed the
normalized0..1000 contract and neither executed. The correction feedback named
the range but did not explicitly distinguish pixel coordinates from normalized
centres. v44 will clarify that same existing contract without guessing or
automatically executing a rescaled point. Native typing is still unexercised.

The latest screenshot/reply also show the email already in QuickNote. The
uncertain v40 input can have produced text despite its failed return; exact
provenance is not established. App-data snapshot restore does not clear Markor's
external QuickNote text. Earlier claims of a clean editor from app-data snapshot
alone were too strong. This preparation omission is separate from model error.
v44 will clear only the synthetic editor through GUI focus and empty native Type,
then return to Files/Home before initialization/recording. It never inserts a
task value or copies text. The initial cleared field and reset operations are
logged as environment preparation, not model actions or benchmark success.
This keeps the optional diagnostic meaningful rather than reusing previous text.

## v41: general routing still fails

trial_SystemCopyToClipboard_20261008T122528_654658Z: valid recorded evaluation,
officialFAIL (initial0/final0), no finish, 12 actions/13 calls, two videos and
no recording error. Steps2–12 alternate Create file and OK without a visible
editor or new file. No Type/selection/Copy occurred, so this trial does not
exercise the native text transport and cannot establish its live repair.
The model did not consistently use the observed QuickNote capability. Recording
rollover/shutdown completed under the new bounds. Sources/prompts were frozen.

No unchanged general-routing retry follows. The optional v42 diagnostic enables
the already prepared task procedure on this same instance, leaving general
guidance, app facts, sampling, budgets and native typing unchanged. This is a
deliberately assisted route/interaction diagnostic to distinguish procedure
choice from execution/copy ability; it is not a general-agent success claim or
authority to expand to harder tasks. One bounded trial, then diagnosis/audit.
