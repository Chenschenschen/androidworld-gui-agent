# Run the agent yourself

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
