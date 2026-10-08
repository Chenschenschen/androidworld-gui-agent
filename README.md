# Android World GUI agent with AutoGLM

A small Python agent that controls an Android test emulator using Z.ai's hosted
**AutoGLM-Phone-9B-Multilingual** (`autoglm-phone-multilingual`). The model receives
real screenshots, selects one checked GUI action per step, and decides when to
finish. Android World's official verifier evaluates the result independently.

This is a course project for **Agentic AI in Modern Business**. It is an
experimental implementation with recorded successes and preserved failures.

## Current results

| Warm-up | Recorded clean results | Version |
| --- | --- | --- |
| Turn Wi-Fi on | 3/3 | v20 |
| Take one photo | 3/3 | v20 |
| Add a contact | 3/3 | v28 |
| Enter an unstarted timer | Latest bounded trial failed | v28 |
| Copy exact text | Latest bounded trial falsely finished | v27 |

Clean means valid initialization and recording, model finish, official PASS and
no runtime error. These are task-specific results on different versions, not a
single successful 15-trial batch. The current v29 adds a bounded no-progress
cycle stop and passes 16 offline adapter checks; it has no live success claim.
See [results and limitations](docs/WARMUP_RESULTS.md) and the
[aggregate results](docs/evidence/README.md).

## Requirements

- Windows and PowerShell; Windows is the tested platform.
- Git and Python **3.11**. The recorded environment uses 3.11.17.
- Android Studio / Android SDK at `%LOCALAPPDATA%\Android\Sdk`.
- A **Pixel 6, Android 13 / API 33** AVD named `AndroidWorldAvd`, running as
  `emulator-5554`, with gRPC on port `8554`.
- A Z.ai API key with access to `autoglm-phone-multilingual`.

Screenshots and synthetic task inputs are sent to Z.ai during live runs.
Use a dedicated test emulator. Local Ollama and GPU model weights are unnecessary.

## Install

Run in PowerShell. Android World is a separate pinned dependency, not vendored
into this repository:

```powershell
git clone https://github.com/Chenschenschen/androidworld-gui-agent.git
Set-Location androidworld-gui-agent
git clone https://github.com/google-research/android_world.git android_world
git -C android_world checkout 2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
Copy-Item .env.example .env
```

Edit `.env` and insert your own API key. Never commit that file.
[SETUP.md](docs/SETUP.md) covers the Android Studio steps, optional Python 3.11.17
installation, first-run app setup and troubleshooting.

## Run

Start the emulator from a terminal, using the flags required by this project:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated
```

In another PowerShell terminal, from the project directory:

```powershell
.\run.ps1 -CheckOnly
.\.venv\Scripts\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42
```

The direct Python command is the agent entry point. Its five task choices are
`SystemWifiTurnOn`, `CameraTakePhoto`, `ContactsAddContact`, `ClockTimerEntry`
and `SystemCopyToClipboard`. Leave the emulator untouched during a recorded run.
The runner initializes the official task and prepares required app snapshots.

Every run prints its unique `runs/` folder. Inspect `summary.json`,
`trajectory.txt`, step screenshots/replies and `video_*.mp4`. A finish message
alone is not success. Use `clean_agent_success` for the full completion gate.
See [RUNNING_TASKS.md](docs/RUNNING_TASKS.md) for details.

## Understand and modify

```text
run_task.py: official reset/setup → video → bounded agent loop → verifier
autoglm_agent.py step(): observe → API decision → validate → freshness → execute
                        → observe actual effect → record
```

| File | What to change |
| --- | --- |
| `agent_config.json` | Step/time bounds, sampling and observation settings. |
| `instructions/autoglm.md` | Attributed native action contract; record prompt changes. |
| `autoglm_agent.py` | Observation, checked action adapter and visible completion criteria. |
| `run_task.py` | Official task initialization, app setup, video and verification. |
| `android_compat.py` | Narrow Windows temporary-APK and fresh XML compatibility adapters. |
| `trajectory.py` | Immediately flushed readable and structured logs. |
| `evaluate_tasks.py` | Sequential evaluations with frozen sources; stops at first failed clean trial. |
| `test_autoglm_adapter.py` | Offline parser, grounding, text-input and progress-bound checks. |

`probe_connection.py` supplies the shared JSON writer; its executable probe,
`gelab_agent.py` and `compare_prompts.py` are historical local-model experiments.
They are not the current agent. Do not use them for the hosted-model workflow.

Read the short [walkthrough](docs/AGENT_WALKTHROUGH.md),
[contribution guide](CONTRIBUTING.md) and [documentation index](docs/README.md).
No arbitrary model-generated Python or shell code is executed. Task completion
is not scripted through ADB/database writes or inferred from verifier feedback.

## Check changes offline

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest test_autoglm_adapter -v
```

These checks use neither the emulator nor the API. For an agreed live evaluation:

```powershell
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact --seeds 42 43 44
```

After a failed trial, inspect and record the trajectory cause, make a justified
fix, then run one bounded regression. Do not rerun an unchanged failure or edit
runtime sources/prompts during an active batch.

## Sources and scope

Built on [Android World](https://github.com/google-research/android_world) and
the [Open-AutoGLM native contract](https://github.com/zai-org/Open-AutoGLM).
See [NOTICE](NOTICE) for attribution and [source/slide mapping](docs/COURSE_AND_UPSTREAM_REVIEW.md).
Project code is available under [Apache License 2.0](LICENSE).
The agreed future Markor, Calendar and harder-task stages remain unfinished;
these warm-ups do not satisfy the complete easy/medium/hard course evaluation.

Full recordings, screenshots, task inputs, API trajectories, course PDFs/ZIPs,
dependency checkouts and environments remain local. The published reports contain
only selected outcome fields, including failures; they are not the raw evidence.
