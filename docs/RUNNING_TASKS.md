# Run the agent yourself

Camera self-run after recorded startup failure:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task CameraTakePhoto --seed 42 --config general_config.json
```

Current v57 includes Camera in existing checked GUI-label capture so its
first-use controls can be distinguished from the launch logo.43 checks and a
read-only actual XML check pass; no new live success yet. Read
CAMERA_SELF_RUN_REPAIR.md before comparing with historical Camera3/3 results.

Latest self-run check,8 October: recipe is now only in project_easy. Run the
forward --params task_inputs/files_easy_to_medium.json command with
--continue-state. Earlier medium-location instructions below describe the
previous state. A user trial's first API request returned HTTP400/provider1210;
the exact saved request then returned200 in an API-only diagnostic. No GUI
action occurred in the failed trial or diagnostic. Current v56 prints redacted
provider errors directly;43 checks pass. The pydub FFmpeg discovery warning
is unrelated to that HTTP rejection; video packaging uses bundled FFmpeg.
If a request fails, inspect *_api_error.json before changing configuration;
the runner does not replay a request or GUI action automatically.

Current self-run command (recipe is in project_medium as checked on8 October):

```powershell
Set-Location "D:\Personal\TUM_MiM\5th_Semester\Agentic_AI_in_Modern_Business_MGTHN0211\project"
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 43 --config general_config.json --params task_inputs/files_medium_to_easy.json --continue-state
```

After clean success, change --params to task_inputs/files_easy_to_medium.json
to move it forward again. The same Python script runs every supported task;
JSON selects the exact file and direction. Keep AndroidWorldAvd running with
gRPC8554 and leave its screen untouched while the agent runs. Existing .env
contains the API settings. Check the printed Evidence folder's summary.json:
clean_agent_success:true requires official PASS plus model finish.

Recording packaging v55 leaves the v54 model/observation policy unchanged.
Android screenrecord is split into roughly three-minute parts; video_001.mp4
is not the complete trial when video_002.mp4 exists. The runner now creates
recording_complete.mp4 after recording and reports complete_video in the
summary. Original parts remain. FFmpeg joins existing frames without re-encoding;
rollover pauses are not recorded time. Packaging errors are reported separately
without discarding original clips or altering the official task result.
imageio-ffmpeg0.6.0 is installed in project .venv and pinned in the dependency
lock.42 checks pass; complete files were decoded and verified against all part
frame counts. No additional agent trial was run for this packaging-only change.

Latest Files results: requested forward/back/forward sequence succeeded after
one failed third attempt and repair (v53/v53/v54, three successes/four attempts).
The recipe now exists only in project_medium. To run again from this state,
start with the reverse command below; the forward precondition intentionally
fails until the recipe is back in easy. Do not delete/recreate the existing file.
Measured model stage used v54;42 offline checks pass. See the complete
results and named videos in FILES_MOVE_TRIAL.md and PRESENTATION_EVIDENCE.md.

FilesMoveFile uses this same runner. Exact file/folder inputs live in
task_inputs/files_easy_to_medium.json and files_medium_to_easy.json. For an
existing source recipe, preserve it:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 42 --config general_config.json --params task_inputs/files_easy_to_medium.json --continue-state
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 43 --config general_config.json --params task_inputs/files_medium_to_easy.json --continue-state
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 44 --config general_config.json --params task_inputs/files_easy_to_medium.json --continue-state
```

Run each command only after the preceding trial's clean PASS. Without
--continue-state, Files prepares only a missing named source file and destination
folder; existing source/destination files are rejected, never overwritten.
Linked moves preserve contents and use the official verifier but are not
independent benchmark resets. Read FILES_MOVE_TRIAL.md for current measured
results. Named successful recordings are indexed in PRESENTATION_EVIDENCE.md.

SimpleSmsSend uses the same runner with screenshots and checked fresh SMS GUI
labels/centres, without a task procedure. Latest v49 seeds43/44 both cleanPASS
with model finish at step7 (two runs, not a three-run gate):

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task SimpleSmsSend --seed 42 --config general_config.json
```

See [SIMPLE_SMS_TRIAL.md](SIMPLE_SMS_TRIAL.md) for results and the preserved setup
failure. Leave the test emulator untouched while the recorded agent runs.

Newest prepared variant: [TASK_GUIDANCE_AND_GROUNDING.md](TASK_GUIDANCE_AND_GROUNDING.md)
describes explicit procedures for all five warm-ups. Use the same Python runner:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task SystemCopyToClipboard --seed 43 --config guided_config.json
```

Change the task/seed arguments for another warm-up; no separate task script is
needed. Guided Clipboard uses Markor, installed/prepared by official Android
World setup on its first run. The selected guide is logged and snapshotted.
28 offline checks pass. No live guided outcome is established; omitting
`--config` still selects the measured v35 baseline.

Latest stage: [UPSTREAM_REFERENCE_COMPARISON.md](UPSTREAM_REFERENCE_COMPARISON.md)
documents the actual original AutoGLM PhoneAgent comparison. Native/project
Timer and Clipboard each failed one valid paired instance. Prerequisite and
invalid-recording attempts are preserved separately.25 offline checks pass.
Default v35 retains the measured Chrome transport and recorder repair, with
the same model policy. One runner supports every task: add `--config reference_config.json` for the
optional pinned native reference, or `--config comparison_config.json` for the
measured project Chrome transport repair. These are known failed task variants,
not new success gates. No task-specific script is needed.

Previous v34 kept the independent entry point and disabled the unsuccessful
before/after assessment by default.20 offline checks pass; standalone readiness
from outside the project passed. The separate assessment_config.json preserves
the failed v33 experiment for inspection, not an improved baseline. Read
[STEP_ASSESSMENT_EXPERIMENT.md](STEP_ASSESSMENT_EXPERIMENT.md) before considering
another trial. Its original source/settings snapshots and videos are preserved.
Earlier v29/v34 descriptions below are historical; no batch is running.

The default agent now uses Z.ai's hosted `autoglm-phone-multilingual`, with
screenshots and native AutoGLM actions. Ollama is not required. Project Python
remains `.venv`, with the existing Android World installation and Windows APK
adapter. No new packages were needed for the migration.

Implemented entry points: SystemWifiTurnOn, CameraTakePhoto, ClockTimerEntry,
ContactsAddContact and SystemCopyToClipboard. Markor, Calendar and a jointly
selected harder task remain in scope. Wi-Fi and Camera v20 each passed three
clean trials; Contacts v28 passed three on identical frozen sources. Timer and Clipboard do not yet have
three clean repeats on the current version. These task-specific results do not
establish a single frozen15/15 batch. Entry points alone do not establish success.
The current stopping-repair stage and its live results are documented in
[AUTOGLM_COMPLETION_REPAIR.md](AUTOGLM_COMPLETION_REPAIR.md).
The final evidence table is [WARMUP_RESULTS.md](WARMUP_RESULTS.md). Current v29
has sixteen offline checks and a bounded no-progress cycle stop; its safety
change has no live success claim. No evaluation batch is currently running.

## Start and configure

Keep the API credentials in project-root `.env`, which is gitignored:

```dotenv
ZAI_API_KEY=<your key>
PHONE_AGENT_BASE_URL=https://api.z.ai/api/paas/v4
PHONE_AGENT_MODEL=autoglm-phone-multilingual
```

The agent explicitly reads these entries. Keys are not included in request logs
or source snapshots. `agent_config.json` contains model identity, prompt version,
sampling, observation and numeric budgets. See [AUTOGLM_API.md](AUTOGLM_API.md).
Screenshots and task inputs are sent to Z.ai. The user explicitly approved this
for Home/Settings screenshots in the recorded Wi-Fi trial, and on 8 October
explicitly approved Contacts, Clock and clipboard test-emulator screenshots and
synthetic task inputs for the remaining recorded warm-ups. The local Ollama app
and server were stopped at the user's request.

Start AndroidWorldAvd with the agreed configuration, or reuse it if running:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated
```

The software camera flags override launch settings without changing AVD files.
They repair the recorded virtual-scene loading symptom; see the completion report
for camera-service diagnostics and before/after trials.

## Run one task

From this project folder:

```powershell
.\run.ps1 -CheckOnly
.\run.ps1 -Task SystemWifiTurnOn -Seed 42
```

`-CheckOnly` checks Python imports, .env settings, emulator boot and port 8554.
It makes no model request, initializes no task and does not establish task success.
The launcher also works by absolute path and restores the original working folder.

Direct Python is equivalent:

```powershell
& .venv\Scripts\python.exe -X utf8 run_task.py --task SystemWifiTurnOn --seed 42
```

Leave the emulator untouched throughout recording. Official initialization/reset
prepares the task; only checked GUI actions are used for agent task execution.
The base screenshot backend avoids the forwarder and Home's UIAutomator idle
dependency. Settings and Clock receive a bounded, checked fresh XML supplement with
observed labels and ON/OFF switch state; changing or unavailable XML is logged
and falls back to the fresh screenshot. The model chooses finish from these
observations. Python does not give it the official verifier outcome.
Chrome now receives the same checked supplement to distinguish its editable
address field from search suggestions. The source-backed v29 protocol and slide
requirements are mapped in [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md).
The runner disables only the crashing test forwarder accessibility service and
records that infrastructure change. It does not uninstall the app.

## Understand the evidence

The printed `Evidence:` folder is unique. Read `summary.json`, `trajectory.txt`,
`task.json`, `config.json`, `versions.json`, `observation_setup.json` and videos.
Each step has distinct observation IDs, screenshots, actual API messages without
base64 dumps, provider replies/usage, parsed actions, freshness checks and results.

`agent_done` is the model's declaration. `verifier` is the official PASS/FAIL/
ERROR result. `verified_agent_success` also requires valid initialization and
recording. `clean_agent_success` additionally requires model finish and no
runtime error; use it for the current three-success stopping gate.
An infrastructure failure can still have an official FAIL; inspect
its error and review rather than attributing it to the model. No effect means
little screenshot change, not proof that an app ignored an action.

The bounded loop allows one invalid-reply correction and one fresh decision
when an unexecuted target changes. It never replays an uncertain dispatch.
Ordinary field-focus taps are allowed. Native Type replaces focused text without
appending Enter. A visible Clock keypad supplies actual observed tap centers for
native coordinate actions. With no tree, focus is selected from the screenshot
and is not independently established by XML. The verifier remains authoritative.

Run the offline adapter checks with:

```powershell
& .venv\Scripts\python.exe -X utf8 -m unittest test_autoglm_adapter -v
```

For the requested three-run gate, use:

```powershell
& .venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks SystemWifiTurnOn --require-model-finish
```

The clean-completion gate is mandatory even when --require-model-finish is
omitted. Stop, read the trajectory, record the cause and fix it before rerunning
a failed task. Continue other warm-ups after three clean Wi-Fi completions.
Preserve the GELab v10 batch
(Wi-Fi 1/3, others 0/3),
[FIVE_TASK_EVALUATION.md](FIVE_TASK_EVALUATION.md) and
[TRAJECTORY_FAILURE_ANALYSIS.md](TRAJECTORY_FAILURE_ANALYSIS.md). This migration
changes model, interface and observation infrastructure, so it is not an isolated
model-effect comparison. Only the task/version-specific live counts in the
completion report establish measured repeats.
