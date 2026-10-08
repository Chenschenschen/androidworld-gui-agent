# Course material review

Camera failure review: read pinned CameraApp.setup (permissions, launch, attempt
NEXT, close) and CameraTakePhoto initializer/verifier (exactly one new photo).
Existing cached snapshot acceptance does not prove onboarding stays completed;
actual trial showed first-use page. Real com.android.camera2 XML exposes NEXT
and checked location option through existing official UIElement parser. Diagnose
too-early/model grounding from concrete frames; do not assume virtual-camera
backend fault without loading/service evidence. See CAMERA_SELF_RUN_REPAIR.md.

8 October HTTP400 source check: Z.ai official api-reference/api-code defines
1210 as generic invalid API parameter; unlike1214 it names no field. Current
Open-AutoGLM README still prescribes api.z.ai/api/paas/v4 and the multilingual
hosted name. The same saved request was accepted by the provider in an API-only
diagnostic. Therefore no particular parameter fault was established; retain
error details rather than guessing or changing policy. Sources:
https://docs.z.ai/api-reference/api-code and
https://github.com/zai-org/Open-AutoGLM/blob/main/README_en.md.

FilesMoveFile source review: pinned single/files.py delegates to MoveFile in
common_validators/file_validators.py; success checks source absent/destination
present. Standard initialization clears shared storage before creating files.
Use official create_file/mkdir only for scoped preparation and TaskEval base
initialization for preserved linked files. app_snapshot.py restores private
/data/data application data, not project_easy/project_medium in shared storage.
FilesApp package is com.google.android.documentsui. Official UIElement parsing
matches raw node counts, but actual UIAutomator captures contain out-of-parent
descendant geometry; validate that geometry rather than trusting derived labels.
The course one-observation/one-action loop and native AutoGLM contract remain.

SMS repair source review: pinned Open-AutoGLM config/prompts_en.py requires exact
Launch pseudo-calls and standalone finish; config/apps.py maps finite multilingual
names to packages and includes SimpleSMSMessenger. Our two Chinese SMS aliases
come from actual failed replies, not the upstream list. Existing Android World
UIElement hint/editable/focus properties supply grounding; no task recipe added.
Measured repair and preserved unsuccessful intermediate changes: SIMPLE_SMS_TRIAL.md.

8 October SMS source review: read the installed pinned Android World SimpleSmsSend
template, SimpleSMSSendSms initialization/verifier, and SimpleSMSMessengerApp
setup. Inputs are number/message; official initialization clears test SMS and
disables airplane mode. Success requires a recent matching sent message and
the SMS app in the foreground. No sent-message database writes are agent actions.

8 October general-guidance implementation: reread pinned M3A GUIDANCE in full,
native AutoGLM prompt/Launch/Type contract and D4 observation/recovery/enforcement
material. Upstream M3A prefers direct app launch over drawer search and exact
text selection before Copy. Its retry suggestion is adapted to our existing
no-uncertain-replay rule: the model chooses recovery from a fresh observation;
the harness never retries an uncertain GUI execution automatically.
android_interactions.md records attribution and omits task routes/coordinates.
The earlier same-model before/after reflection failures remain evidence against
assuming extra calls improve this model. Details: GENERAL_GUIDANCE_EXPERIMENT.md.

8 October task-procedure preparation: revisited D2's step3_skill_status.py
pattern (procedural skill separated from factual status), the D4 coding loop,
pinned M3A visible targeting/full text-selection guidance, and AutoGLM's native
coordinate/Type contract. Read official Android World MarkorApp setup and
SystemCopyToClipboard schema: the actual parameter is clipboard_content.
Markor's own README documents QuickNote and copying support. The five routes
in task_guides.md are our user-authorized adaptations, with Timer buffer and
partial-word selection warnings based on our trajectories. They are not quoted
upstream benchmark policies. Their grounding limits, references and unmeasured
status are explicit in TASK_GUIDANCE_AND_GROUNDING.md.

8 October native reference implementation: inspected the full pinned
Open-AutoGLM agent, model stream parser/builder, action parser/handler, device
factory, ADB screenshot/input/device helpers, app map and timing/dependencies.
Native screenshots remain full resolution; native Type needs ADB Keyboard,
absent in the current emulator. The integration bundle differs from our
adaptation and is being measured, not presumed superior.

Live comparison completed: original native policy failed Timer padding/field
planning and Clipboard whole-value selection. Our policy failed by repeated
zeros and Chrome menu cycles. Inspected Android Env's execute_command retry
and _restart_server after a recorded timeout/video loss; source shows why
recording can disappear during a retried launch. The bounded transport repair
was measured separately and retained without changing model guidance.

Assessment source adaptation and experiment, 8 October: inspected pinned M3A
SUMMARY_PROMPT_TEMPLATE and its shared PROMPT_PREFIX, compared them with the
new same-model before/after request, then inspected every failed live variant
before a changed check. Short visible assessments were inaccurate; restoring
capability context did not establish a fix. Native placeholder copying and
truncated assessment are preserved separately from semantic task failures.
Report: [STEP_ASSESSMENT_EXPERIMENT.md](STEP_ASSESSMENT_EXPERIMENT.md).

8 October leaderboard research: compared the official community scoreboard,
MobileRun architecture, ARTEMIS README, Minitap and MAI-UI primary papers with
current v29 and preserved Timer/Clipboard failures. Findings and bounded
experiment proposals: [LEADERBOARD_COMPARISON.md](LEADERBOARD_COMPARISON.md).
The locally inspected pinned M3A source includes a separate before/after model
summary call that our adaptation has not implemented. Architecture descriptions
are not causal proof of reported scores; no runtime/prompt changes were adopted.

Repository export, 8 October: retain source hashes in the portable
docs/sources/pinned_upstream.json manifest and preserve upstream prompt license
and NOTICE. Course originals remain excluded; source/slide mapping and design
histories remain available. No course PDFs/ZIPs are redistributed.

8 October source audit: reread all174 pages of D1–D4 and the supplied minimal
example/D2 status script, with relevant rendered diagrams. Reviewed12 official
GitHub files pinned by commit/SHA256 in
../.review/upstream_20261008T075102_892043Z/manifest.json. The implementation
mapping, upstream adaptations and per-failure diagnoses are recorded in
COURSE_AND_UPSTREAM_REVIEW.md. The experimental Clock keypad Type was withdrawn
because it extends upstream focused-field Type. Source-backed guidance and
concise completion criteria replace accumulated recipes. UIAutomator's actual
standard EditText/focused attributes resolve missing parser editability; normal
Type still has no implicit Enter. Clipboard model false_done remains unsolved
after a saved-screen actual-control-feedback probe; no unchanged live retry.
Contacts v28's three frozen-source trials all passed. Timer's v28 regression
still failed sequencing/recovery. The v29 no-progress cycle bound follows D4
pp.26–27; sixteen offline checks pass, with no live v29 success claim.

v20 protocol review: Camera v19 seed 43's step 4 response contains two identical
finish calls identifying the new captured thumbnail. The strict single-line
parser rejected them, and correction selected another shutter action. Therefore
this failure cannot be described solely as the model failing to recognize done.
One unique literal decision can safely collapse exact repeats, while different
calls remain invalid and execution is once at most. The original reply parses
correctly offline; the new bounded Camera trial passed official verification in
four steps with model finish. Original artifacts remain intact.

v18 evidence review: a full six-digit Clock entry ignores appended digit taps.
The observed five-digit prefix 13333 should receive the requested position-six
digit 4; exposing GUI digits/count and numbered goal positions helped the saved
partial case and the new live seed 44. Recovery after an incorrect full entry
remains unestablished. Clipboard's copied-text chip can disappear before the next
observation. The original v17 images show a closed Copy menu and exact unchanged
field while the model loops waiting for that transient cue. Treating the chip
as mandatory caused a truncated-reply failure despite official PASS. It is now
optional. Counterfactual probes and live outcomes are kept separate.

Continuation observation review: Timer GUI bounds distinguish the one-digit
`0` and two-digit `00` controls. A model correction still returned coordinates,
so a label-only request was incompatible with the observed native behavior.
Supplying observed centers alongside native coordinate Tap passed the zero-rich
seed 42. Clipboard v15's actual image shows the entire target selected, then a
disappearing Copy menu and a new Gboard clipboard chip. Clicking the chip pastes
it back. Its official PASS with no model finish demonstrates a stopping failure,
not a copy failure. A saved request naming the requested text `text_to_copy`
avoided treating `clipboard_content` as existing state. Keep original parameters
and distinguish counterfactual saved-state probes from live evaluations.

Live setup review, 8 October: the recorded v13 Contacts permission UI uses
`Don’t allow` (U+2019) while installed ContactsApp.setup searches ASCII
`Don't allow`. Thus the earlier absent-dialog diagnosis was wrong; the saved
setup screenshot and official parsed XML prove the label mismatch. v14 handles
that observed notification dialog and validates the ready main GUI.

Continuation review, 8 October 2026: installed Android World actuation.execute_adb_action(input_text) clears/types and then presses Enter; native Open-AutoGLM Type does not add that submission. ContactsApp.setup always requests Skip and then Don't allow, but the notification dialog can be absent after permission has persisted. AddContact officially clears contacts at initialization and generates random benchmark names/numbers. SystemCopyToClipboard officially resets its clipboard and draws task text from synthetic benchmark examples. Actual Clock XML exposes distinct clickable labels 0 and 00 and the timer_setup_time display; v10 images/replies prove incorrect coordinate grounding. Preserve the original summaries and classify setup errors separately in the review.

Completion repair review, 7 October 2026: reread TRAJECTORY_FAILURE_ANALYSIS.md,
RUNNING_TASKS.md, FIVE_TASK_EVALUATION.md and the latest completed v10 RESULTS.md.
Reviewed official T3A's goal-already-satisfied completion instruction; Open-AutoGLM's
English prompt, conversation history and image-first message builder; installed
Android World State/UIElement/XML parser, get_current_activity, controller
observation methods and ClockTimerEntry verifier. The Clock verifier reads the
exact displayed duration and needs actual GUI elements. XML Switch nodes may
have blank text while their row contains the visible label. Our supplement
associates those observed values, without using a task oracle. See
[AUTOGLM_COMPLETION_REPAIR.md](AUTOGLM_COMPLETION_REPAIR.md) for source links,
failed probes and measured results. Prior material-review notes remain below.

Subsequent review: native Open-AutoGLM's action parser extracts finish messages
as plain text, while GUI calls use AST literals. Its assistant/user conversation
identifies the previous operation; compact `Tap` alone does not. Android World
`setup.setup_app` catches ValueError and then saves a snapshot, so a screenshot-only
controller can cache incomplete Camera/Chrome onboarding. Use the official app
setup with its GUI labels available, then restore the model observation backend.
Android's emulator command-line reference supports software camera overrides.
Actual diagnostics show non-increasing camera timestamps with virtualscene;
software-camera trial shows a real preview. Do not infer the underlying platform
bug or general reliability from that symptom repair.

Five easy tasks are listed together on D1 p.7 (the extracted task table).
Read official CameraTakePhoto (exactly one new photo filename), ClockTimerEntry
(formatted duration in DeskClock), SystemCopyToClipboard (fuzzy clipboard match),
and SystemWifiTurnOn (wifi_on state). Timer's verifier is a UI duration check;
also inspect action/video evidence for the explicit do-not-start instruction.

Read AndroidWorldController: it supports A11yMethod.UIAUTOMATOR and the a11y
forwarder. Read android-env A11yGrpcWrapper: networking is required; recovery
calls svc wifi enable. Captured a stale launcher tree while Settings was visible
with Wi-Fi off. That is infrastructure evidence, not clean model capability.
UIAutomator XML collection is the existing Android World implementation; the
factory omits its selector, so load_task_env temporarily supplies that constructor
argument and immediately restores the constructor. XML labels inside clickable
rows are valid tap positions; headings without clickable containment remain
excluded. The capture-only probe keeps Wi-Fi off and is not a task-success run.

Official Clipper initialization clears the clipboard through its broadcast,
and its verifier launches Clipper to read it. Our agent has no direct clipboard
write action; copying must be performed by checked GUI selection/copy. Chrome
is a supporting GUI input app and is reset via its official snapshot each run.

Additional implementation review, 7 October 2026:

- Reread extracted `minimal_agent_example.py`, lines 30-35: exclusive trace file,
  labelled blocks, JSON formatting and immediate `file.flush()`. Adapted in
  `trajectory.py` with GUI observations, actions/results, and a JSONL companion.
- Installed Android World actuation supports targeted `input_text` and
  `clear_text=True`: focus, select/clear, type, then Enter. Our model chooses the
  field and value; no model-generated code executes.
- `contacts_validators.AddContact` compares an exact saved display name and
  normalized phone. Actual v6 profile showed a duplicated surname, motivating
  the conditional single-full-name procedure; this does not change the verifier.
- The pinned GELab reference strips old coordinates from action history. Our
  v5 context follows that principle while preserving full source trajectories.
- Reviewed [official Ollama FAQ](https://docs.ollama.com/faq) for partial CPU/GPU
  residency and keeping models loaded. Hardware numbers and quality outcomes
  are our measurements in PERFORMANCE_AND_TRAJECTORIES.md, not course scores.


## Earlier record (historical)

Implementation evidence, independent execution: the current Android World tree
contains a temporary unlabelled/noninteractive Contacts FrameLayout representing
the text-cursor handle. Launcher trial `20261007T164836_344369Z`, step 6,
captured its disappearance while the intended field was unchanged. This supports
excluding decoration, not semantic/interactive controls, from freshness checks.
Readiness checks and parameterized launching follow the simple explicit input/
output/control-flow preference; no new agent framework or model was introduced.

## Additional references reviewed, 7 October 2026

Read the user's [AndroidWorld leaderboard](https://docs.google.com/spreadsheets/d/1cchzP9dlTZ3WXQTfYNhh3avxoLipqHN75v1Tb86uhHo/edit?gid=0).
The public sheet exported successfully through the browser. Snapshot and cell
links are saved in `.review/leaderboard/`. The sheet explicitly labels its scores
community submitted and independently unverified; no listed score is ours.

Selected primary references, chosen for relevant mechanisms rather than rank:

- [Droidrun method](https://droidrun.ai/benchmark/method/): hybrid current state,
  single-action feedback, previous/current tree comparison and targeted text
  operations. Its manager/executor architecture is beyond our initial scope;
  reuse the feedback principle with one agent, not the entire framework.
- [Finalrun benchmark description](https://github.com/final-run/finalrun-android-world-benchmark):
  repeated observation, exact-value memory and optional app knowledge. These
  are author descriptions, not independently verified guarantees.
- [Finalrun implementation](https://github.com/droid-ash/finalrun-agent/blob/main/packages/goal-executor/src/TestExecutor.ts):
  `_runPlanningPhase` supplies screenshot, hierarchy, history, remembered data
  and app knowledge; `_runActionPhase` executes then captures and records the
  result. Read the relevant implementation sections, not the whole repository.
- [GELab reference](https://github.com/stepfun-ai/gelab-zero/blob/7b619f6f67d2b1101021fc453cb27bd48a29e4f2/copilot_tools/parser_0920_summary_adv.py):
  screenshot-centered native protocol retains note, verify, explanation and
  progress in action history. Our tree/JSON route is an adaptation, so failures
  there alone cannot establish native model inadequacy.

Reread D2 `step1_tool_context.py`: actual calls and tool results/errors enter
the next context. `step3_skill_status.py` explicitly reads and injects procedural
text; a skill filename alone is insufficient. Android World `actuation.py`
presses Enter after input_text. `contacts_validators.AddContact` checks saved
name and normalized phone, not a compulsory first/last-name field split.
These findings motivated the small context repair described in the walkthrough.

Reviewed on 7 October 2026. Initially the project contained only
`course_content/`, with no project implementation or AGENTS.md. Originals
are unchanged. Reading tools/extracted copies/rendered pages are in `.review/`.

## Coverage and method

Read extracted text from all 218 pages of 6 PDFs and inspected rendered page
contact sheets. Day2 p.36 has no extracted text and was also inspected individually.
Inventoried all 64 ZIP entries and opened every file: 24 course files and
33 macOS metadata files, plus 7 directory entries. There are no nested ZIPs.

The 24 course files comprise 14 Python files, 3 READMEs, 1 example skill,
1 CSV, 4 JSONs, and 1 TXT trace. `__MACOSX`, `._*`, `.DS_Store` entries are
metadata, not additional lessons/code. Names, sizes, and SHA-256 hashes are
recorded in `.review/materials/inventory.json`.

Each of D2 `step2.json`'s 12 requests contains the same 48-line reference
template. Every repeated block was checked for exact equality programmatically
and shortened in a reading copy; all remaining request/response/measurement
fields were read. Original JSON remains intact. No example program or model
task was executed during source inspection.

## PDF contents

| File | Pages | Contents | Project implication |
| --- | --- | --- | --- |
| Agentic-AI-Block-Week-Syllabus.pdf | 2 | Schedule, goals, assessment, deliverables | Implementation, evaluation, logs, failure, improvement |
| D1-Intro.pdf | 51 | LLMs, context, ReAct, GUI tasks, engines, logs, failures | One step() agent, three difficulties, three runs/task, video |
| AI-Agent-Context-Engineering-Day2.pdf | 52 | Context, caching, skills, status, memory, RAG | Harness maintains context; code maintains counters |
| Day3_Tools.pdf | 32 | Harness, action/observation space, tools, ACI, MCP | Model proposes; runtime checks/executes; feedback guides next action |
| D4-Coding.pdf | 39 | Coding feedback, verification, recovery, constraints | Bound recovery; verify real output; keep project instructions |
| D5-RL-slides.pdf | 42 | Training, RL algorithms, rewards, reward hacking | Try context/instructions/program changes first; training not required |

Key sources for requirements:

- Syllabus p.1: individual work 40%, agent project 40%, presentation 20%.
- Syllabus p.1: working implementation, evaluation results, trajectories,
  at least one failure analysis, and documented before/after improvement.
- D1 pp.6-7: GUI agent with `step()`; at least one task from each difficulty;
  three runs per task; video for every evaluation.
- D1 p.8/syllabus p.1: 10-30 minute presentation and 5-10 minute Q&A.
- D1 pp.49-50: run-summary fields and five GUI failure classes.

## All course task options

| Difficulty | Task | Objective | Course steps |
| --- | --- | --- | --- |
| Easy | SystemWifiTurnOn | Turn Wi-Fi on | 3 |
| Easy | CameraTakePhoto | Take one photo | 2 |
| Easy | ClockTimerEntry | Enter a timer without starting it | 3 |
| Easy | ContactsAddContact | Create a contact with name/number | 5 |
| Easy | SystemCopyToClipboard | Copy supplied text to clipboard | 2 |
| Medium | SimpleSmsSend | Send a supplied message to a number | 6 |
| Medium | MarkorCreateNote | Create a named note with supplied text | 8 |
| Medium | FilesMoveFile | Move a file between supplied folders | 10 |
| Medium | SimpleCalendarAddOneEvent | Create an event with date/time/duration | 17 |
| Medium | ExpenseAddMultiple | Add multiple expenses | 20 |
| Hard | MarkorCreateNoteAndSms | Create a note and share its entire text by SMS | 9 |
| Hard | BrowserMultiply | Remember five numbers and enter their product | 11 |
| Hard | ExpenseAddMultipleFromMarkor | Transfer reimbursable expenses from a note | 15 |
| Hard | MarkorMergeNotes | Merge three notes in order | 39 |
| Hard | OsmAndTrack | Save a track with two ordered waypoints | 60 |

Counts are course examples. Categories also reflect memory/app switching, not
only length. Check selected task names/parameters/verifiers in the installed registry.

## Every course file in the ZIPs

### code example.zip

- `minimal_agent_example.py`: short hosted web-search request, configuration,
  visible response items, errors, TXT logging, immediate flush.
- `README.md`: hosted tool loop and limits of the visible trace.
- `agent_trace_20260921_104721_841063.txt`: initial request, metadata, two reasoning
  items, one search item, final message, sources, output. Reasoning items do not
  expose internal thoughts; encrypted fields are not readable reasoning evidence.
  This is not our Android experiment.

Reuse simplicity, visible configuration, raw output logging, and preserved errors.
For Android we still need local image/model input, action parsing/execution,
task initialization, and official verification.

### D1.zip

- `README.md`: four terminal exercises and Ollama configuration.
- `common.py`: standard-library HTTP GET/POST, chat/stream, preload,
  model/capability selection, statistics, waiting indicator.
- `check_setup.py`: server/model/context/capability checks and short answer probe.
- `step1_chat.py`: manual user/reply history resent each turn.
- `step2_temperature.py`: five temperatures; three repeats with/without seed.
- `step3_context_growth.py`: five turns, prompt counters, history/no-history test.
- `step4_chat_template.py`: marker tokens, manual raw rendering, injection example.

Reuse explicit message lists/HTTP payloads, small experiments, repeated runs,
and sampling records. Manual chat-marker rendering is a teaching experiment,
not a default requirement for our agent.

### D2.zip

- `README.md`: tool, cache, skill/status, memory experiments.
- `common.py`: D1 client with clearer HTTP errors/cache-counter caveats.
- `check_setup.py`: separates tool support from ordinary chat support.
- `lab_support.py`: deep-copy snapshots, timings, request/response/error records.
- `step1_tool_context.py`: model tool call, argument validation, Python multiply,
  appended feedback, bounded loop and explicit stop reasons.
- `step2_prefix_cache.py`: early/late changing fields, warm/measured pairs,
  alternating order, three repeats, median prompt-processing comparison.
- `step3_skill_status.py`: simple trigger, skill loading, status snapshot,
  code-maintained attempted request counters including errors.
- `step4_memory.py`: displays extraction; writes hard-coded preferences;
  reloads them into a fresh request; compares with/without memory.
- `skills/three-bullet-summary/SKILL.md`: three-bullet summary procedure.
- `artifacts/step1.json`: two requests, one tool call, `30*23=690`, final answer.
- `artifacts/step2.json`: twelve warm/measured calls, six measured rows.
- `artifacts/step2_measurements.csv`: the same six measured rows.
- `artifacts/memory.json` and `artifacts/artifacts/memory.json`: identical preferences.

Archived cache medians: early 629.059 ms, late 53.736 ms. These are examples,
not measurements on our machine/GUI agent. Missing metrics mean unavailable,
not zero. Reuse transparent bounded loops, input checks, snapshot logging,
failure preservation, and controlled comparisons.

## Source inconsistencies

1. Minimal code uses `API_KEY == "..."` instead of assignment. Execution raises
   NameError for undefined API_KEY. Syntax compilation alone would not detect it.
2. Its README names a different script and mentions an absent mock/sample trace.
3. D1 calls `prompt_eval_count` total tokens sent, whereas its README and D2
   warn about cache/version-dependent semantics. Keep raw names/verify meaning.
4. D2 memory saves a hard-coded dictionary, not parsed extraction from the model.
   Do not describe it as automatic memory extraction.
5. Its `Path("D2/artifacts/memory.json")` depends on working directory and conflicts
   with README's run-inside-D2 instruction. HOST also bypasses shared configuration.
6. Syllabus says groups of 2-4, D1 says 3-5. Individual assessment days also differ.
   The user confirmed group work, not a resolution of those number discrepancies.

## Local state and technical references

Confirmed installed GELab-Zero BF16 4B and connected ADB emulator. Identity and
settings are in the decision record. Android World is now installed in project
`.venv`; registry and screenshot/accessibility capture are verified. Official
Contacts task initialization/verification and model-driven GUI actions are now
tested through the small agent. Both learning runs failed; preserve this result
separately from successful connection checks. See `FIRST_TASKS.md`.

Day 1 and Day 2 were reread for the design catalogue in
`docs/AGENT_DESIGN_DECISIONS.md`, including rendered Day 2 pages 21, 27, 32,
36, 44, and 47. The catalogue distinguishes explicit lecture tradeoffs from our
implementation choices and optional mechanisms. All slide references use PDF
page numbers; model-specific interface compatibility still needs a real probe.

Checked the primary repositories for the component boundary:
[Android World](https://github.com/google-research/android_world) separates emulator
setup, Python installation, and minimal task runner.
[GELab-Zero](https://github.com/stepfun-ai/gelab-zero) separates inference engine,
Android/ADB execution, and agent runtime. Check the Python connection while
preserving the user's existing model and emulator.

The project need not implement every lecture topic. Its core is a small working
loop, independent verification, understandable code, and documented experiments.

Read the GELab reference at commit `7b619f6f67d2b1101021fc453cb27bd48a29e4f2`:
the base/advanced/state-compress parsers, local server variants, prompt tools,
inference helper, model config, and published Ollama Modelfile/tokenizer metadata.
Saved source text is under `.review/gelab_reference/`; none was executed. Its
native tab-separated actions and 0..1000 coordinates informed our adapter. The
upstream parser skips unkeyed annotations, which explained the first adapter
failure. Our prompt is a shorter English adaptation, not a reproduction of the
complete upstream agent. Source link and changed behavior are in `FIRST_TASKS.md`.

Reread for the agent build plan: D1 requirements, format drift, loop, observations,
grounding and failure pages; D2 prompting/skills/status/memory; D3 action/result
interfaces; D4 reliability/harness/recovery; D5 fix-layer choices. Inspected D2
rendered pages 32 and 36, including explicit skill loading and status insertion.
Reread the actual D1 sampling/history/template examples and D2 tool loop,
skill/status, memory, snapshot logging and cache comparison examples. Compared
them with our Contacts step 5 screenshot/request and Wi-Fi claims.
`AGENT_BUILD_PLAN.md` maps every planned mechanism to specific pages/examples.
It distinguishes selected experiments from implemented behavior and skills from
tools. No requirement for one skill per benchmark task was found in the project
requirements; the course example needs an explicit read-and-inject loader.

Checked official Ollama structured-output documentation and verified local schema
acceptance experimentally, following D1 p.27. Native examples worsened the small
comparison; JSON was a separate interface-package experiment and cannot be called
a prompt-only improvement. Detailed results and limitations, including the
missing app snapshot and uncaptured fresh-state mismatch, are recorded in
`GROUNDING_EXPERIMENTS.md`.
# AutoGLM source review — 7 October 2026

Implementation follow-up: read TRAJECTORY_FAILURE_ANALYSIS.md in full. The new
agent avoids incomplete-tree requests and focus-tap bans. A checked unique XML
dump exposed `could not get idle state` before any model/action. The installed
official controller supports `A11yMethod.NONE`; use that for native screenshots,
with bounded visual settling and visual target freshness. No upstream source or
original course archive was modified. Windows temporary-APK compatibility stays.

The corrected Wi-Fi trial passed official verification, but its step 9 actual
screenshot shows Wi-Fi on while the model claims off and taps it again. This
is evidence of a new model visual-state/stopping error, not proof of stale input.
Both recorded outcomes, video checks and source snapshots are linked in
[AUTOGLM_FIRST_TRIAL.md](AUTOGLM_FIRST_TRIAL.md). Original read-only trajectory
diagnosis and all GELab batch results remain unchanged.

Reviewed the official [Open-AutoGLM README](https://github.com/zai-org/Open-AutoGLM/blob/main/README_en.md),
[model client](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/model/client.py),
[English system prompt](https://github.com/zai-org/Open-AutoGLM/blob/main/phone_agent/config/prompts_en.py)
and [CLI entry point](https://github.com/zai-org/Open-AutoGLM/blob/main/main.py),
plus [Z.ai's API introduction](https://docs.z.ai/api-reference/introduction).
These are external interface references, not our benchmark results.

The README maps multilingual weights to hosted model
`autoglm-phone-multilingual`, general base URL `https://api.z.ai/api/paas/v4`.
The model client uses chat completions with screenshots supplied as data-URL
image content. The prompt's single-action pseudo-calls differ from our existing
GELab JSON actions. The CLI reads `PHONE_AGENT_API_KEY` from the process
environment; our `.env` uses `ZAI_API_KEY`, so explicit loading/mapping is needed.
Upstream requests can be used to understand the protocol, but model-generated
text must remain data for our checked Android World action adapter.

Our bounded text probe received HTTP 200 and the requested model identity.
It supplied no screen yet received a camera-screen description; do not treat
this as an observation or as GUI compatibility. The reply hit the 64-token cap.
Both the first sandbox DNS failure and the separate authenticated response are
preserved in [AUTOGLM_API.md](AUTOGLM_API.md). No task evaluation occurred.

# Observation findings from our recorded experiments — 7 October 2026

These are our observations, not results copied from course archives. Wi-Fi's
UIAutomator tree captured an Android AccessibilityForwarder crash dialog; this
service can remain enabled on the device after a Python environment closes.
The official controller's UIAUTOMATOR selector prevents constructing the gRPC
wrapper but does not disable an existing Android accessibility service.

Camera's tree advertised a Shutter control while screenshot and video retained
the loading screen. The official AsyncAndroidEnv stability check compares UI
elements; matching elements alone cannot prove visual readiness. A stale tree
or a loading camera must be diagnosed before evaluating model navigation.

The current whole-tree freshness signature also includes Gboard suggestions.
Our contact Phone target remained unchanged while those suggestions changed,
causing a false stop. Keep the source/API behavior separate from our guard's
implementation error and the model's earlier incorrect name edits. Details
and exact run references are in FIVE_TASK_EVALUATION.md.
# Source checks during the full trajectory diagnosis — 7 October 2026

All 15 current trajectories / 78 replies reviewed alongside frozen requests,
actions and screenshots; report: TRAJECTORY_FAILURE_ANALYSIS.md. The compact
tree drops Timer's actual is_selected=True flag. Our observation gate counts
System UI labels although our grounding schema excludes them. Our fallback
aborts on arrival of a changed observation. These are implementation choices,
not course requirements or proven limitations of GELab-Zero.

Official adb_utils.py uiautomator_dump (1772–1780) ignores the dump request's
response, then reads reused /sdcard/window_dump.xml. issue_generic_request
(548–586) logs non-OK status and returns instead of raising. A failed dump can
therefore leave stale XML as a source-backed risk; our traces lack individual
dump status/timestamps, so this is not a proven cause of a particular mismatch.
AsyncAndroidEnv stability compares elements rather than visual readiness.
Keep confirmed screenshots/tree differences separate from unproven causes.
# Clock GUI keyboard source review, 8 October 2026

Primary AOSP TimerSetupView source maps KEYCODE_0 through KEYCODE_9 and Delete
to the visible keypad's performClick handlers:
https://android.googlesource.com/platform/packages/apps/DeskClock/+/6ac43d8368e8b09c4d683d6d993e1862b4f09464/src/com/android/deskclock/timer/TimerSetupView.java
This source is not proof of our Google Clock APK's behavior; the separately
logged GUI diagnostic established that the installed app accepts Android World's
normal Type input. Diagnostic `120405` produced `12h 04m 05s` with no Start.
The agent still chooses the string and finish; this transport is not a direct
timer state write or a task-dependent next-key controller.
