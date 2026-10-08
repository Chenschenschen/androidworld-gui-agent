# Project decisions

Evidence publication, 8 October: the user explicitly approved the previously
blocked emulator screenshots and diagnostic artifacts. Publish the selected
original export and its hash manifest; keep credentials and unrelated local
archives excluded. No runtime change or new task success claim.

Repository preparation, 8 October: the user requested publication to
Chenschenschen/androidworld-gui-agent. Added current installation/contribution
guides, a credential template, pinned-dependency instructions and aggregate
outcome reports; full evidence remains local after approval review rejected
uploading raw screenshots/diagnostic artifacts. No runtime
behavior changed. See [REPOSITORY_RELEASE.md](REPOSITORY_RELEASE.md).

Latest user correction, 8 October: research official GitHub and apply the first
four days' slides; on failure stop, read trajectory, record cause, fix, then
bounded regression. v29 follows the pinned upstream English contract and short
visible goals. Experimental Clock keypad Type and long task recipes are
withdrawn. Source/default deviations, concrete adapter faults and every
subsequent outcome are in [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md).
Sixteen offline checks pass. Recorder readiness, app-catalog validation and XML
EditText recognition were corrected from actual evidence. Clipboard's latest
false_done survived an unexecuted factual-feedback probe; no unchanged full
retry is justified. Wi-Fi/Camera v20 and Contacts v28 each passed three clean
trials; Contacts' source hashes match across all three seeds. Timer v28 still
failed digit sequencing and recovery. v29 bounds unchanged action cycles but
has only offline checks; it does not solve those model errors. No trial is
running, no current15/15 claim, and no broad batch or speed tuning. See
[WARMUP_RESULTS.md](WARMUP_RESULTS.md). Earlier continuation entries are history.

Latest validation, v20: the v19 full batch had Wi-Fi 3/3 clean, then stopped on
Camera seed 43's duplicate-finish rejection. The model had recognized the first
capture; correction after our rejection induced extra taps. v20 collapses exact
duplicate calls to one decision, still rejects distinct calls and executes once.
The Camera regression passed in four steps. Frozen batch
easy_batch_20261008T064328_366877Z now runs all five warm-ups three times. No
runtime/prompt changes are allowed during that batch. Earlier attempts stay
visible; they are not silently replaced by successful retries.

Current v18 validation stage: bounded Clipboard seed 44 and Timer seed 44 both
passed with model finish and official PASS. Contacts v14 already passed all three
seeds. A final frozen v18 batch now evaluates all five warm-ups three times,
stopping on any failed clean-completion gate. The user authorized these test
trials and the remaining screen transmissions. Speed tuning stays paused.
Timer's observed digit string/count is a stateless GUI representation, not a
goal comparison or next-action controller. Clipboard requires full selection,
Copy and menu closure; a transient chip/toast is optional. Original parameter
names remain in task.json; the model-facing goal says text_to_copy.

8 October continuation update: the user explicitly authorized the remaining
test-emulator screenshots and synthetic inputs to Z.ai. v13's bounded Contacts
attempt exposed a curly-apostrophe permission label mismatch, correcting the
earlier absent-dialog assumption. v14 handles that actual notification dialog
using fresh GUI bounds and proves main-screen readiness before snapshotting.
No task contact is created during setup. The failed attempt is retained as an
environment setup failure. Native Type and exact timer labels remain unchanged.

Current continuation, 8 October 2026: Wi-Fi v5/v7 each achieved 3/3 clean finishes; Camera v8 achieved 3/3. The completed v10 remaining-task batch had Timer 1/3 clean, Contacts three setup-invalid evaluations and Clipboard 0/3. v12 repairs only the observed causes: optional Contacts permission dialog with ready-GUI proof, native text entry without appended Enter, and exact observed-label taps on the Clock keypad. Ten offline checks pass; live remaining-task results are pending explicit broader screenshot authorization after automatic approval review rejected Contacts/clipboard transmission. No new broad batch before bounded trials. See AUTOGLM_COMPLETION_REPAIR.md. Earlier version descriptions below are history.

## Latest stage — model completion, 7 October 2026

The user requested three clean Wi-Fi completions before the other warm-ups.
Explicit completion wording alone failed saved-state probes. Anonymous GUI
checked flags also failed in two recorded v4 trials (official PASS, no finish).
Current v5 links the fresh switch state to its actual containing-row label,
which passed an ON/OFF saved-state discrimination probe. Live results are pending.
Keep all original failures. See [AUTOGLM_COMPLETION_REPAIR.md](AUTOGLM_COMPLETION_REPAIR.md).
Require official PASS **and** model finish for this gate. Keep one simple agent,
standalone Python, official initialization/execution/verifiers and recorded evidence.
No hidden task-state feedback or Python-forced completion is adopted.
Earlier sections below describe historical stages and their then-current results.

The v5 Wi-Fi gate completed: 3/3 official PASS and 3/3 model finishes, five steps
each. Camera then exposed the known loading symptom and a camera-service frame
timestamp error. Reversible software-camera launch flags restore a visible
preview, but a retry took extra captures rather than finishing. Current v7
retains the native executed conversation and explicit one-photo completion cue.
It also reads quoted finish messages as inert native text after v6's correctly
chosen finish was blocked by our Python-string parser. Eight offline checks
pass; fresh v7 live results are pending. Preserve all intermediate failures and
do not conflate infrastructure repair, model behavior and parser errors.

Current v8 follows the native conversation more closely: original goal once,
subsequent user turns as observations, full executed conversation within the
12-step bound and old images removed. The repeated `Take one photo` goal in
every v7 user turn was replaced after a live Camera repeat-capture failure.
The actual failed images/history passed a new saved-state probe; a fresh live
Camera seed 42 then passed in four steps with model finish. Remaining v8 trials
are recorded in easy_batch_20261007T205955_772699Z. Wi-Fi also passed 3/3 in v7.

## Latest implementation — AutoGLM migration, 7 October 2026

The requested migration is implemented in `autoglm_agent.py`, with standalone
`run.ps1`/`run_task.py` and scheduler integration. Default v2 uses screenshots,
the native AutoGLM pseudo-call contract, checked GUI actions and official
Android World `A11yMethod.NONE`. This avoids the reproduced UIAutomator idle
failure and old incomplete-tree model input. Normal focus taps are allowed;
unexecuted choices can be reconsidered once when visual target freshness changes.
The user approved successive benchmark Home/Settings screenshots to Z.ai.
Ollama's app and server are stopped. No package installation was needed.

Two recorded Wi-Fi attempts are retained: v1 failed before any model/action on
XML capture; v2 passed the official verifier on seed 42 (initial 0/final 1).
The v2 agent used 12 steps/13 calls and stopped at its budget without declaring
completion. It misread an already-on switch and toggled it repeatedly, so this
does not establish clean stopping or repeatability. Do not run a broad batch.
Read [AUTOGLM_FIRST_TRIAL.md](AUTOGLM_FIRST_TRIAL.md) for audit, full evidence
and remaining issues. Earlier entries below are historical decisions/results.

## Latest user decision — AutoGLM API, 7 October 2026

The user selected `AutoGLM-Phone-9B-Multilingual` hosted by Z.ai to replace
local GELab-Zero. This supersedes the local-only model preference for the next
implementation stage. The official hosted model name is
`autoglm-phone-multilingual`, at `https://api.z.ai/api/paas/v4`.
The project's `.env` already has these settings and a `ZAI_API_KEY`.
A bounded text request received HTTP 200 and the requested model identity;
it establishes API access only. No GUI action, visual probe or verifier ran.
The runtime still uses GELab/Ollama; migration is pending. Preserve original
experiments and observation-failure analysis, and start with a bounded
compatibility stage before further batches. See [AUTOGLM_API.md](AUTOGLM_API.md)
for official sources, exact probe settings and evidence. Earlier local-model
decisions below remain the history of the implemented v10 baseline.

Current comparison batch: `easy_batch_20261007T191040_731527Z`, v10.
Completed v9 batch: fifteen valid recorded attempts, all official FAIL. Twelve
were blocked before action 1 because a whole-screen freshness check also applied
to AWAKE. Restrict that guard to click/long_press/input_text; fixed app launches
and BACK do not reuse screen coordinates. Repeat the four blocked tasks unchanged
apart from that guard. Wi-Fi switches to screenshots after 0/3 valid tree-first
results, as an evidence-backed application of the agreed fallback policy. Its
comparison changes interface plus guard, so do not claim an isolated image effect.
No speed/model/sampling/budget change. Results pending; failures remain preserved.

Fresh unattended batch: `runs/easy_batch_20261007T184229_043036Z`.
The preceding v9 batch was stopped after the user confirmed manual emulator
interaction. It is excluded from unattended repeatability claims; the exact
affected time range is unknown. Model/settings/agent behavior are unchanged
for the restart. All diagnostic evidence remains on disk. Results pending.

Current requested stage: evaluate SystemWifiTurnOn, CameraTakePhoto,
ClockTimerEntry, ContactsAddContact and SystemCopyToClipboard three times each.
Task seeds 42/43/44; model seed and sampling frozen. Speed tuning is paused.
This easy-only stage does not replace the later medium/hard presentation scope.

Version v9 supports all five task names and checked GUI LONGPRESS. The model
receives available app names; AWAKE is limited to those apps. Clipper's direct
writes occur only in official initialization/reset, never as model actions.
Chrome is restored from its official snapshot per clipboard trial to avoid
cross-run state. Every trial has immediate TXT/JSONL, raw requests, source/settings,
video and official verification. evaluate_tasks.py runs trials sequentially,
freezes configuration and stops if runtime source hashes change.

The first two Wi-Fi diagnostic runs exposed screenshot/tree mismatch and are
excluded from capability evaluation, with original evidence preserved. Use
Android World's official UIAutomator backend for Wi-Fi only; do not construct
the network-dependent a11y wrapper there. A probe confirms Settings matches
its tree, Network & internet is groundable, and Wi-Fi remains off. Text inside
clickable rows can be grounded at its actual visible center. Other tasks retain
gRPC observations. Fifteen-trial frozen batch: runs/easy_batch_20261007T182934_895562Z.
Results are pending; never interpret a model COMPLETE as verifier PASS.

Current update, 7 October 2026 (revision 0.10): Latest recorded Contacts trial: `trial_ContactsAddContact_20261007T173637_269613Z`, official FAIL, initial 0.0/final 0.0, 12 steps, 12 calls, 119.75 seconds, no manual intervention.

Readable TXT and structured JSONL trajectories now flush every event, following
the course logging example. Preserve full raw evidence and link requests/images.
For tree-first grounding, the model chooses an exact visible label; Python
resolves its current index and pixels. Ambiguous labels are rejected, with one
correction per step and at most two screenshot fallbacks per run. Restrict named
targets to interactive app controls. Targeted TYPE chooses the editable field
and exact value; a separate editable-field CLICK is rejected in this provisional
contract. COMPLETE while the creation form remains open is rejected; this is
only a visible-state guard, not the official verifier.

The conditional contact guide is justified by lost/duplicated values; no separate
skill file is required. Recent model context keeps semantic actions and observed
values, omitting stale pixels/indices and model predictions; originals remain on
disk. The v6-to-v7 guide-only comparison holds task/sampling/GPU/budgets fixed.
Other preceding repairs changed multiple variables and are diagnostic only.

User authorized approximately 80% GPU use. Retain 22 offloaded layers: peak
6,393/8,188 MiB (78.1%), warm tree median 6.61 s and image 19.25 s, modest gains
over 16 layers. This is a memory target, not a compute-utilization cap. Change
`options.num_gpu` back to 16 if memory pressure occurs, and remeasure. All choices
remain provisional/configurable; edit the instruction contract consistently
when changing `targeted_type`/`direct_type_only`/`label_grounding`. Keep the same
local BF16 model. No hard-task reliability claim follows from a Contacts PASS.

Read [PERFORMANCE_AND_TRAJECTORIES.md](PERFORMANCE_AND_TRAJECTORIES.md) for exact
evidence, limits and failure analysis. Earlier entries below are historical;
their "proposed/not implemented" TYPE wording and older counts are superseded.


## Earlier record (historical)

Independent execution verified end to end: current launcher supports Contacts
and Wi-Fi; both latest Contacts repeats failed and remain preserved. v2_1 fixed
the measured cursor-only freshness stop, but the repeat still misgrounded a
keyboard Dash key and exhausted steps. Next proposal is targeted TYPE(index,
exact value), using the installed Android World contract. Test it as a single
action-interface change. Do not claim reproducible task success from one PASS.

Independent launcher follow-up: version `learning_context_feedback_v2_1` ignores
unlabelled/noninteractive decoration in the app-control freshness signature.
Evidence: launcher trial `trial_ContactsAddContact_20261007T164836_344369Z`
stopped at step 6 solely when a noninteractive cursor-handle FrameLayout vanished;
the selected index-7 field was identical. Its official FAIL is preserved.
Replay checks accept that disappearance and reject changed target bounds.
Establish repeatability before expanding task support; launcher execution itself
does not guarantee model/task success.

Independent execution: `run.ps1` is a small optional launcher around the existing
`run_task.py`, using project `.venv` and explicit service/device readiness checks.
Contacts/Wi-Fi can be selected by task name and generated task seed. It requires
no Codex session. A readiness check or normal process exit is not task PASS.
Commands and recommended next stages are in `docs/RUNNING_TASKS.md`.

Latest update, revision 0.8: ContactsAddContact earned one official learning PASS
in `trial_ContactsAddContact_20261007T160201_407078Z` (initial 0, final 1,
10 GUI actions, 11 calls, 157.67 s, tree only, no manual intervention).
General instructions are explicitly loaded from `instructions/agent.md`;
conditional inline contact guidance addresses observed surname loss. Recent
history now includes target labels and observed editable values. TYPE's automatic
Enter is described to the model. A missing device app snapshot is regenerated
through official setup even if a host-side marker exists.
This combined repair is diagnostic progress; a guide-only controlled comparison
remains pending. Tree-first stays selected. A screenshot-plus-tree diagnostic
was prepared but not run after tree success. Read `AGENT_WALKTHROUGH.md` first.
Earlier measurements below remain the historical record.

Updated: 7 October 2026. This version incorporates all answers received during
the initial material review. Open choices will be resolved in the relevant stage.

The complete Day 1/Day 2 design catalogue is in
`docs/AGENT_DESIGN_DECISIONS.md`: 35 decisions with alternatives, source pages,
tradeoffs, recommendations, and revision conditions. The baseline observation,
grounding were initially open; the basic tree-first policy is now selected.
Final inference/recovery settings remain open. The user requested joint
selection and a changeable record of the reasons. No catalogue recommendation
is an agreed or implemented setting until recorded as confirmed.

Latest design answers: compare screenshot/coordinate and tree/index probes
before selecting the interface; send latest observation + recent actions + exact
scratch notes when needed; balance verified success with manageable runtime.
These choices and their reasons are recorded in catalogue revision 0.2. Numeric
budgets and implementation details remain open. Planning, status update, and
invalid-reply correction choices were answered in revision 0.3: one action at
a time (short TODO only when needed), current status in requests with all older
snapshots on disk, and one correction for an invalid reply before stopping.
Recovery from possibly executed actions remains separate. The user added
`ContactsAddContact` as an initial trial task and authorized connecting the
local model to the emulator through our Python harness.
Catalogue revision 0.4 records the authorized GPU experiment and provisional
learning settings. All final baseline choices remain changeable.
Revision 0.5: the user delegated the disappeared prompt question's choice to
course guidance. Select three exact native action examples as the next isolated
experiment; keep inference/parser/observation settings fixed. This is a selected
plan, not a tested improvement. Do not create one skill per task by default;
test short reusable procedural guidance only when a workflow failure warrants it.
The complete staged architecture and evidence gates are in `AGENT_BUILD_PLAN.md`.
Revision 0.6: user selected tree observations and index grounding for basic
tasks, with screenshots used when necessary or that approach fails. This is a
policy choice, not measured proof that GELab handles indices reliably. The next
prompt comparison holds tree input fixed in both conditions. Fallbacks must be
explicit, bounded, and logged; keep raw screenshots on disk for trajectory review.
Revision 0.7: native examples rejected (0/6 intended actions versus base 3/6).
Constrained JSON was a separate interface-package test (6/6) and is the current
learning format. Live Contacts made eight actions without parse errors or image
fallback but failed officially. A partial surname supports the next proposed
workflow/exact-value guide. Evidence is in `GROUNDING_EXPERIMENTS.md`.

## Agreed decisions

| Topic | Decision | Evidence |
| --- | --- | --- |
| Goal | Simple code, verifiable task success, complete understanding for the presentation | User |
| Working style | Group project; design and experiments together in small stages | User |
| Platform | Windows and PowerShell | User/local inspection |
| Model/engine | Local GELab-Zero through Ollama | User |
| Installed model | `gelab-zero-4b-preview:latest`, ID `6f883cb0e9da`, BF16, 4B | Ollama list/show |
| ADB | `emulator-5554` connected | `adb devices -l` |
| Project environment | `.venv` inside project, Python 3.11.17, no system packages | User/local setup |
| Android World | `android_world/`, commit `2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7`, installed in `.venv` | Official GitHub checkout |
| Review environment | `.review/venv`, Python 3.12.14 with bundled reading packages | Material inspection |
| Language | English for explanations, code, documents, and presentation | User |
| Explanation depth | Every function/loop explained; line comments for difficult logic | User |
| Evaluation | Official task verifier, video, trajectory | Course/user |
| Initial scope | One small agent, no training or extra framework | Simplicity preference |
| Extra requirements | None beyond the supplied course materials | User |

Emulator launch command supplied by the user:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554
```

This starts the emulator; it does not alone verify the Python Android World
package, task initialization, or verifier connection.

The model reports `num_ctx=4096`, `num_gpu=0`, `temperature=1`, `top_k=20`,
and `top_p=0.95`. Preserve these before choosing experiment settings. The
architecture's theoretical context length is not the active `num_ctx`.
The user authorized testing partial GPU offload before a trial. With 16 layers,
Ollama reported 4,187,173,682 bytes of GPU residency. A reload request took
67.70 s and the next tree request 12.08 s; this is not a controlled speedup
estimate. Trials retain the same BF16 model and sampling and use 16 layers.
The installed renderer/parser are `qwen3-vl-instruct`; the template field alone
does not imply broken rendering. Real model-selected taps opened Contacts and
its creation form. See `FIRST_TASKS.md` for logs, timings, and limitations.

## Agreed task progression

| Stage | Difficulty | Task | Course approximate steps |
| --- | --- | --- | --- |
| Learn the loop | Easy | `SystemWifiTurnOn` | 3 |
| Learn text entry/saving | Medium | `MarkorCreateNote` | 8 |
| Learn app switching | Hard | `MarkorCreateNoteAndSms` | 9 |
| Presentation target | Medium/real work | `SimpleCalendarAddOneEvent` | 17 |
| Presentation target | Hard/memory | `MarkorMergeNotes` OR `OsmAndTrack` | 39 OR 60 |

The user accepted the initial three, but wants harder presentation tasks. We
will advance after the basic workflow behaves normally and is understood.
The final hard task is intentionally deferred. Do not treat the initial set
as a permanent limit. These step counts are course estimates, not our results.
Check the installed registry and use SMS only in the test emulator.

## Open checks and later decisions

- Configure remaining Markor/calendar/navigation task apps. Contacts official
  initialization and verifier have been exercised; both learning trials failed.
- Observation strategy, action format, parsing and step/time budgets after
  inspecting the installed code and real model output.
- `MarkorMergeNotes` versus `OsmAndTrack` when ready for the harder stage.
- A parser annotation compatibility improvement was tested on the same Contacts
  instance: GUI actions increased from 0 to 4, but task success stayed 0/1.
  A prompt-format improvement is a candidate for the next jointly chosen stage.
- First Wi-Fi verifier PASS is invalid as agent evidence: the goal was already
  satisfied before inference. A diagnostic identified reset-after-initialize as
  the cause. Version 3 follows official ordering and guards the starting state.
- Exact presentation duration/date. The user said Friday; the materials'
  21-25 September 2026 schedule is not assumed to be the current deadline.

## Working stages

1. **Understand the environment:** locate Android World; check compatibility;
   create `.venv`; inspect registry/reset/screenshot/actions/verifier. Explain
   the model, Python harness, and emulator as separate components.
2. **Understand one step:** inspect a screenshot/task request and model reply;
   explain parsing, validation, and action execution.
3. **Build the small loop:** one easy task, bounded steps, immediate logs,
   official verification. Explain results before expanding scope.
4. **Extend the learning tasks:** note creation and note-to-SMS, using the same
   generic agent. Inspect failures and retain reproducible evidence.
5. **Advance to presentation tasks:** calendar event and the selected harder
   task. Keep the implementation simple while adding only justified mechanisms.
6. **Evaluate and improve:** freeze task instances/configuration; three runs
   per task; video and trajectories; one small evidence-backed change and a
   comparable before/after evaluation.
7. **Prepare the presentation:** use case, code flow, success table, failure
   trajectory, improvement evidence, and exact reproduction commands.

For a final three-task selection, at least 9 baseline runs are required.
Repeating those 9 cases for the improved version gives a clear 18-run comparison.
This is a proposal, not an explicit 18-run course requirement. If more tasks are
included in final evaluation, apply the three-runs-per-task rule to each one.

## First explanation for the next stage

The model proposes the next action. Our Python harness validates and executes
it through Android World on the emulator. A fresh screen supplies the next
decision's input. The trajectory records that sequence. The verifier checks
the resulting environment state to establish whether the task succeeded.

Material review, Python installation, registry loading, and a real emulator
observation check have been completed. The screen is 1080 × 2400 and contains
25 UI elements in the saved check. See `docs/SETUP.md` for commands, versions,
evidence, and the narrow Windows temporary-APK adapter. A small agent and recorded
Contacts learning trials now exist; official verification ran and returned FAIL.
The first narrow parser improvement helped progress but not task success. These
learning trials do not replace the course's final repeated evaluations.
The corrected Wi-Fi trial also failed after one action. Current valid learning
results are Contacts 0/2 and Wi-Fi 0/1; the earlier Wi-Fi PASS is excluded because
it was already satisfied before any action. No agent task PASS has been earned.
# Recorded five-task diagnostic findings — 7 October 2026

Keep local GELab/Ollama, GPU22 and sampling settings unchanged while assessing
the five easy warm-ups. The unattended v9 batch completed fifteen failures.
The v10 comparison removes the freshness guard from fixed app/navigation
commands; Wi-Fi additionally uses screenshot input after three tree failures.
Wi-Fi's comparison is consequently confounded by two changes.

One v10 Wi-Fi GUI trial passed the official verifier. Subsequent Wi-Fi trials
showed an AccessibilityForwarder crash modal even with the UIAutomator backend;
not creating its Python wrapper does not disable its Android service. Camera's
saved tree advertises Shutter while the screenshot and video show loading.
Do not attribute those failures solely to model capability.

Contacts also has a clear model `lost_value` error: a correct full name was
later replaced. The later Phone action was blocked by changing Gboard clipboard
suggestions although the Phone target was unchanged. Preserve this harness
false stop separately from the earlier model error. A target-specific guard and
a bounded observation-backend probe are the proposed next repair stage. Neither
has been measured yet. See FIVE_TASK_EVALUATION.md for trace evidence, results
and standalone reproduction commands. These decisions remain editable.
# Full trajectory diagnosis — 7 October 2026

Reviewed all 15 current trials and 78 raw replies without new inference or
emulator actions. Read TRAJECTORY_FAILURE_ANALYSIS.md for per-run evidence.
Wi-Fi seed 44 was a changing Home time widget, not a second proven crash-modal
case; its intended Settings tap points to Messages. Seed 43 has inconsistent
modal-tree/Home-image evidence, with exact modal timing unproven.

Confirmed own-code issues: System UI labels pass the usable-observation test
while grounding excludes them; three step-2 calls therefore have no available
app target. Fresh tree arrival causes fallback to abort rather than recapture.
Whole-tree freshness includes unrelated time/keyboard changes. The field-focus
CLICK ban repeatedly turns focus proposals into destructive TYPE corrections.
The earlier genuine Contacts PASS used normal focus clicks before typing.

Proposed next order: repair the observation gate/fresh-state recovery, then
target-specific freshness, then isolate Camera readiness and simplify the
focus/action contract. Measure one change at a time, on one task before another
broad evaluation. Preserve exact scratch values, videos and official verification.
No runtime defaults changed in this diagnostic turn. No model switch or speed
tuning has been adopted. Evidence does not show missing persistent memory or
token truncation as the cause of the recorded failures.
# 8 October: v21 bounded remaining warm-up repairs

Wi-Fi and Camera v20 each passed three clean trials. Timer still skipped zero
digits despite correctly grounded controls and a literal input/count prompt.
Installed Clock's GUI keyboard support was proved in a separately labeled manual
diagnostic. Adopt native model Type on its observed empty keypad, limited to six
ASCII digits, followed by observation and model finish. No hidden state writes,
next-digit controller or verifier feedback. Add Chrome to the existing checked
GUI supplement after a wrong search-suggestion long press. Contacts gets 16
steps after a real Save at step 12; other budgets and sampling stay frozen.
Run bounded regressions, then three trials per remaining task. Retain failures.
