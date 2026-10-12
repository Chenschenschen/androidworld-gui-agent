# Project working rules

Update, 12 October 2026: branch team-agent is the group's final agent, tag team-agent-final-v66. Seven tasks x
three runs, 17/21 official PASS: six tasks from the v65 batches (same code), Markor from the v66 batch after its
Skill was changed to share the note (docs/TEAM_FINAL_EVALUATION.md, docs/MARKOR_SHARE_V66.md, docs/TEAM_AGENT.md). Branches Jia and
hayati and the amber_agent_integration package are left unchanged.

Update, 8 October 2026 (evening): additional OsmAnd-only experiment. v49-v61 use the accessibility
forwarder (UIAutomator fallback) and run the OsmAnd Skill procedure as code (osmand_next_step). Frozen
v61 (tag osmand-extra-v61) on the course slide's instance (Ruggell -> Bendern, seeds 31/314/366): 2/3
with the Skill, 0/3 without (docs/IMPROVEMENT_OSMAND.md). Branch head v62 = two post-evaluation fixes,
not evaluated. The three-task course evaluation stays tag final-eval-v42.

Current state, 8 October 2026 (v42, branch Jia): the course evaluation is complete. Final batch
eval_batch_20261008T133403: Contacts 3/3, Calendar 3/3, OsmAndTrack 0/3, one frozen version, all runs
valid and recorded. Documented improvement: OsmAnd Skill (instructions/skills/osmand_track.md) versus
the same code with --disable-skills. Read docs/FINAL_EVALUATION.md, docs/IMPROVEMENT_OSMAND.md,
docs/FINAL_FAILURE_ANALYSIS.md and docs/MEDIUM_HARD_TRIALS.md (every v30-v42 trial, cause and fix)
before changing anything. The evaluation emulator runs headless on the host GPU (-gpu host -no-window).
Paragraphs below describe earlier stages.

Current continuation, 8 October 2026: the user requires source-backed guidance
from official GitHub and the first four days' slides. On a failed trial, STOP,
inspect its trajectory, record the cause, correct it, then run a bounded
regression. Never rerun an unchanged failed task or another broad batch.
Read docs/COURSE_AND_UPSTREAM_REVIEW.md (174 slide pages reviewed plus original
example code and pinned official source manifest). v29 uses the pinned AutoGLM
English action contract, concise visible completion goals, factual GUI status,
native conversation and upstream3000-token cap. Experimental Clock keypad Type
and accumulated task recipes are withdrawn. Sixteen offline checks pass.
The scheduler always stops at the first failed clean trial. Sources/prompts must
stay frozen during any active batch. v23 stopped before model calls on a delayed
recorder PID; v24 adds bounded readiness and ownership checks, with its original
invalid evaluation and recovered orphan clip preserved.
v20 Wi-Fi and Camera each achieved3/3 clean; Contacts v28 achieved3/3 clean
with identical frozen sources across seeds42/43/44 and eleven steps each.
Timer v20/v21 still skipped zeros; Clipboard v20 failed seed43 on wrong field
grounding after seed42 passed. Remaining gates are not complete. Chrome now has
the existing checked GUI supplement; Contacts budget16 follows actual Saveat12.
v27 fixes actual standard EditText recognition when XML editability is missing;
v28 returns the selected GUI label in action feedback. Clipboard's Clear input
mistaken for Copy caused false_done and persisted in a saved-screen feedback
probe. Do not rerun Clipboard unchanged. The v28 Timer regression also failed:
correctly grounded digits omitted a required zero, then ineffective digit taps
cycled on a full wrong value. Do not rerun Timer unchanged. v29 bounds such
no-progress cycles; it is checked offline, not a proven digit-entry repair.
No batch is running. All failures are preserved; no final15/15 claim. Read
docs/WARMUP_RESULTS.md for the final evidence and remaining limitations.
The user explicitly approved remaining test-emulator screenshots and synthetic
inputs to Z.ai on 8 October. Software camera flags are documented; Ollama is off.
Speed tuning remains paused. No verifier feedback, Python-forced completion,
next-digit controller or fixed GUI task replay. Read docs/RUNNING_TASKS.md,
docs/AUTOGLM_COMPLETION_REPAIR.md and latest RESULTS.md before success claims.
Earlier design/version sections below remain historical.

Latest user decision, 7 October 2026: use AutoGLM-Phone-9B-Multilingual through
Z.ai instead of local GELab for the next implementation stage. This supersedes
the local-only model preference below. Hosted model `autoglm-phone-multilingual`
and base URL `https://api.z.ai/api/paas/v4` in `.env` are correct; one bounded
text request verified access. Migration is now implemented: autoglm_agent.py,
run_task.py and run.ps1 use the API and native screenshot/pseudo-call contract.
Current v2 uses official A11yMethod.NONE with bounded visual settling and visual
target freshness; normal focus taps are allowed. Ollama's app/server are stopped.
Read docs/AUTOGLM_FIRST_TRIAL.md and docs/TRAJECTORY_FAILURE_ANALYSIS.md.
First v1 attempt failed before any model/action on XML idle capture. Corrected
v2 Wi-Fi seed 42 passed the verifier (initial 0/final 1), but used all 12 steps
and did not declare completion; it repeatedly misread the on switch as off.
Preserve both attempts and the remaining model stopping failure. User approved
successive test-emulator Home/Settings screenshots to Z.ai for this Wi-Fi trial.
Other AutoGLM tasks and three-repeat reliability are unestablished. Do not run
a broad batch before the next bounded stopping/observation stage. Details below
about v10/local GELab describe historical implementation and evidence.

Completed v10 stage: five easy tasks, three unattended trials each. Speed tuning is paused.
All five task entry points and GUI LONGPRESS are implemented. Current v10 uses
screenshot model input for Wi-Fi with the official UIAutomator backend after a
recorded stale-tree mismatch. The other tasks remain tree-first. An
interrupted batch contained user-confirmed manual interaction and is excluded
from repeatability claims. Keep original evidence and evaluation reviews.
Read docs/RUNNING_TASKS.md and the latest batch RESULTS.md before claiming success.
Read docs/FIVE_TASK_EVALUATION.md for crash, camera loading, lost-value and
keyboard-suggestion freshness failures. Standalone execution is verified;
three successful repeats per task are not established. Speed tuning is paused.
Completed v10 batch: easy_batch_20261007T191040_731527Z, 15 official outcomes,
Wi-Fi 1/3 and Camera/Timer/Contacts/Clipboard 0/3. All recorded artifacts audited.
Keep infrastructure and model failures distinct; do not run another broad batch
before a bounded observation/target-freshness repair stage.
Full read-only diagnosis: docs/TRAJECTORY_FAILURE_ANALYSIS.md, all 15 trials and
78 model replies. Own-code faults include status-bar-only observation acceptance,
aborting on fresh fallback evidence, whole-scene false stops, and a brittle
focus-CLICK ban. Proposals are documented; runtime defaults have not changed.

This is a simple, explainable Android GUI agent for the Agentic AI in Modern
Business course. The user's instructions take precedence over this file.
Keep decisions in `docs/PROJECT_DECISIONS.md`, detailed agent design choices in
`docs/AGENT_DESIGN_DECISIONS.md`, and source review notes in
`docs/MATERIAL_REVIEW.md`. Update these documents as decisions change.

## User preferences

- Use English for explanations, code, documents, and the presentation.
- Stay close to the course examples in simplicity: few files, short functions,
  clear names, and visible inputs, outputs, and control flow.
- Explain more than the examples. Give every function a concise docstring,
  explain the purpose of every loop, and add line comments for difficult logic.
  Avoid comments that only repeat obvious syntax.
- The user must understand the whole project well enough to present it on Friday.
  Work in small stages: explain purpose and inputs/outputs, show a small change,
  run a real experiment, and explain evidence before expanding the implementation.
- Select tasks and design the logic together with the user. Continue routine
  inspections and implementation within an agreed stage without repeated approvals.
- Use Windows and PowerShell. Use local GELab-Zero through Ollama. Do not switch
  models or introduce paid/cloud inference unless the user requests it.
- Install packages and run project Python through project-root `.venv`.
  Use `.venv\Scripts\python.exe -m pip`, not global pip. Check Python compatibility
  before creating the environment. Do not use system packages in project `.venv`.
- `.review/venv` is separate material-reading tooling, using bundled Python 3.12
  packages through `--system-site-packages`. It is not the project environment.
- A venv isolates dependencies, not filesystem/network permissions. Direct Android
  actions to the test emulator and keep generated files inside the project.
- Preserve original PDFs/ZIPs. Attribute adapted examples and explain changes.

## Task progression and scope

- Begin with `SystemWifiTurnOn`, `MarkorCreateNote`, and `MarkorCreateNoteAndSms`
  as agreed learning tasks. Establish the loop, logging, and verification first.
- The initial set is not the final presentation scope. The user wants
  `SimpleCalendarAddOneEvent` from real work and either `MarkorMergeNotes` or
  `OsmAndTrack` from multi-app/memory. Progress to these after the basic workflow
  is understood. Choose the final hard task together at that stage.
- Do not promise successful completion before running the official verifier.
  Preserve the harder-task objective rather than silently limiting the project
  to the easiest tasks.
- Start with one agent class and a `step()` method: receive task/observation,
  call the model, parse and validate its action, execute through the environment,
  and record the next observation. Follow the installed Android World contract.
- Let the model decide from real observations. Do not complete benchmark tasks
  with direct ADB/database/file changes and report that as GUI-agent success.
  Official task initialization/reset is a separate environment operation.
- Prefer the standard library when sufficient. Reuse required Android World
  dependencies rather than rebuilding them just to reduce file count.
- Do not add broad frameworks, multiple agents, RAG/vector DB, a custom dashboard,
  fine-tuning, or RL training to the first version. Add only a small mechanism
  justified by real experimental evidence, and explain it to the user.
- Select Day 1/Day 2 design choices jointly. Keep alternatives, reasons,
  accepted downsides, revision conditions, and a history; proposals are not
  adopted defaults. Snapshot actual implemented settings in every run.
- Agreed design direction: basic tasks now use tree/index first, with screenshots
  as a bounded logged fallback when needed or that approach fails; use latest observation +
  recent actions + exact scratch notes when needed; balance verified success
  with manageable runtime. Numeric budgets are still open.
- Confirmed loop choices: one action at a time; a short TODO only when needed;
  current status in requests with all snapshots on disk; one invalid-reply
  correction before stopping. Do not replay uncertain execution automatically.
- The user authorized partial GPU offload testing with the same BF16 model.
  Learning trials currently use 22 GPU layers; this is a reversible experiment,
  not a finalized observation/grounding or sampling baseline.
- Verify GELab-Zero's expected input/output. A normal chat prompt or Ollama's
  capability list alone does not establish GUI-action compatibility.
- Bound steps, elapsed time, model output, and retries. Choose numeric budgets
  from initial measurements. Never repeat actions indefinitely without progress.
- Never execute arbitrary Python/shell text generated by the model. Execute only
  allowed Android actions with checked arguments and coordinate/index conversion.

## Course requirements

- D1 pp.6-8: at least three tasks, including at least one from each of the easy,
  medium, and hard categories; three evaluation runs per task.
- Record every evaluation on video, associated with its trajectory run ID.
- Syllabus p.1: working implementation, evaluation results, trajectory logs,
  at least one failure analysis, and improvement backed by before/after results.
- Presentation: 10-30 minutes with 5-10 minutes Q&A in the documents. The exact
  group allocation remains unknown.
- Group-size/individual-assessment-day details conflict between source documents.
  Keep the discrepancy visible and update decisions if the user resolves it.

## Evaluation and logging

- The official Android World task verifier determines success. Model `done`,
  no exception, or a plausible screenshot does not establish success.
- Record agent completion and verifier outcome separately. If verification
  cannot run, record an evaluation error instead of inventing PASS/FAIL.
- Use official initialization/reset per run. Record task parameters, task seed,
  model identity/version, prompt version, observation type, grounding method,
  sampling settings, and budgets. Avoid memory leakage between runs.
- Compare baseline/improvement on comparable task instances. Change one variable
  at a time. Keep all failures and mark any manual intervention explicitly.
- Report success counts with rates. Three runs are a small sample, not broad
  reliability evidence. Distinguish infrastructure errors from task outcomes.
- Course GUI failure classes: `grounding`, `too_early`, `lost_value`, `wrong_app`,
  `false_done`. Record API/parse/environment/verifier errors separately.
- Analyze at least one real failure from specific trajectory steps. Select a
  small improvement from evidence and report honestly if it does not help.
- Create unique run folders; do not overwrite runs. Write each step immediately
  so interruptions/errors preserve evidence.
- Log initial settings/task goal, observation/screenshot paths, actual model
  context, visible raw reply, parsed action, execution result, timing, errors,
  and stop reason. Link image files instead of dumping base64 in readable logs.
- Compress context for the model only if needed; preserve full original logs
  on disk. Log visible explanations if supplied; do not invent internal reasoning.
- Run summary: task, run ID, version, model, observation, grounding, steps/budget,
  duration, agent done, verifier outcome, failure class, video/log paths, notes.
- Course archive outputs are examples, not our own measurements. Document
  dependency versions and exact reproduction commands for group members.

## Historical v10 state

- Reviewed 6 PDFs / 218 pages and all 3 ZIPs / 24 course files; originals preserved.
- Local GELab-Zero BF16 via Ollama; project Python 3.11.17 `.venv`; Android World
  installed and emulator-5554 connected. Preserve Windows temporary-APK adapter.
- Standalone `run.ps1` and direct `run_task.py` support all five easy tasks.
  `evaluate_tasks.py` schedules three task seeds per task sequentially with frozen settings. Readiness,
  official initialization, logging, video and official verification exercised.
- One agent with bounded step/time/API/correction/image budgets. Tree-first;
  unique visible-label grounding, targeted TYPE, conditional inline contact guide,
  exact per-run scratch and recent observed results. No fixed GUI action replay.
- Leave the emulator untouched during recorded trials. If manual input is later
  reported, preserve original summaries and add an explicit evaluation review;
  do not present affected runs as unattended capability evidence.
- Current default uses 22 GPU layers: measured peak VRAM 78.1%, modest speed gain.
- Earlier Contact PASS runs and all FAILs are preserved. No reliability claim:
  repeat the frozen current version and then a fresh seed before expanding.
- Remaining scope: agreed Wi-Fi/Markor stages, SimpleCalendarAddOneEvent and
  jointly selected MarkorMergeNotes/OsmAndTrack. Three runs per final task,
  at least easy/medium/hard, before/after evidence, and presentation still required.
