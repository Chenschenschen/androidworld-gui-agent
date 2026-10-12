# Android World GUI agent with AutoGLM

A small Python agent that controls an Android test emulator using Z.ai's hosted
**AutoGLM-Phone-9B-Multilingual** (`autoglm-phone-multilingual`). The model receives
real screenshots, selects one checked GUI action per step, and decides when to
finish. Android World's official verifier evaluates the result independently.

This is a course project for **Agentic AI in Modern Business**. It is an
experimental implementation with recorded successes and preserved failures.

## Team final evaluation (final agent v66): one agent, seven tasks

Branch `team-agent` combines the group's work into one agent (the
`AutoGLMAgent` class and its `step()` method) for all seven chosen tasks; the
original branches `Jia` and `hayati` and the integration package stay
unchanged. Final agent: tag **`team-agent-final-v66`** (six tasks evaluated with
v65, whose code is identical for them; Markor with v66 after its Skill fix), three
runs per task, every run screen-recorded and judged by the official Android World verifier:

| Course row | Task | Official PASS |
| --- | --- | --- |
| Warm-up (easy) | SystemWifiTurnOn | **3/3** |
| Warm-up (easy) | ContactsAddContact | **2/3** |
| Real work (medium) | SimpleSmsSend | **3/3** |
| Real work (medium) | FilesMoveFile | **2/3** (one false completion) |
| Real work (medium) | SimpleCalendarAddOneEvent | **3/3** |
| Multi-app (hard) | MarkorCreateNoteAndSms | **2/3** |
| Multi-app (hard) | OsmAndTrack (the slide's Ruggell, Bendern instance) | **2/3** |

**17/21.** Run log (D1 p.49 fields, observation per task), the four failures
and how to reproduce: [TEAM_FINAL_EVALUATION.md](docs/TEAM_FINAL_EVALUATION.md).
How the agent was assembled and what came from each contribution:
[TEAM_AGENT.md](docs/TEAM_AGENT.md). The sections below are the earlier
history of Jia's branch.

## Earlier evaluation (v42, one frozen version, 8 October 2026)

The evaluated code is tagged **`final-eval-v42`**. Later work on the hard task
alone is reported separately below and does not change this table.

| Task (course difficulty) | Official PASS | Notes |
| --- | --- | --- |
| ContactsAddContact (easy) | **3/3** | 11-13 steps, model finished every run |
| SimpleCalendarAddOneEvent (medium) | **3/3** | 17-21 steps, model finished every run |
| OsmAndTrack (hard, 60 reference steps) | **0/3** | Stopped by the no-progress rule after 14-22 steps; no false completion |

Nine runs, task seeds 42/43/44, every run screen-recorded and checked by the
official Android World verifier. Details and run log:
[FINAL_EVALUATION.md](docs/FINAL_EVALUATION.md). Failure analysis:
[FINAL_FAILURE_ANALYSIS.md](docs/FINAL_FAILURE_ANALYSIS.md).

**Documented improvement** ([IMPROVEMENT_OSMAND.md](docs/IMPROVEMENT_OSMAND.md)):
an OsmAnd Skill (app knowledge plus per-step search terms), compared on the
same frozen code with only `task_skills` changed. Verifier 0/3 before and after;
with the Skill all three runs searched by place name (1/3 before) and one
started a route (0/3 before). All learning trials, infrastructure faults and
fixes from v30 to v42: [MEDIUM_HARD_TRIALS.md](docs/MEDIUM_HARD_TRIALS.md).

## Additional experiment: OsmAndTrack on the course slide's instance (v61)

After the evaluation we continued on the hard task only. v49-v61 read OsmAnd's
GUI tree (Android World's accessibility forwarder, UIAutomator as a fallback)
and run the Skill's procedure as code: each step the program recognises the
OsmAnd screen and states the next action with its tap centre, and refuses
actions the screen shows to be wrong. The model still performs every action.

Frozen v61 (tag **`osmand-extra-v61`**), the exact task on the course slide
("Save a track with waypoints Ruggell, Liechtenstein and Bendern,
Liechtenstein"; Android World seeds 31, 314 and 366 all produce it), same code
with and without the Skill:

| OsmAndTrack, slide instance | Official PASS | Notes |
| --- | --- | --- |
| Without the Skill (`--disable-skills`) | 0/3 | Searched "Ruggell, Liechtenstein" (finds only the country); two runs used navigation, which saves no track |
| With the Skill | **2/3** | 22 and 23 steps, model finished both; the failure followed a crash of the forwarder app |

The first passes on this task came in practice runs (seeds 8 and 7, 2 and 3
waypoints) before the freeze. Every run is recorded. Details:
[IMPROVEMENT_OSMAND.md](docs/IMPROVEMENT_OSMAND.md#additional-experiment-v61-on-the-slide-instance),
the failed run in [FINAL_FAILURE_ANALYSIS.md](docs/FINAL_FAILURE_ANALYSIS.md#additional-experiment-the-one-failure-of-v61-on-the-slide-task),
all 14 practice runs in [MEDIUM_HARD_TRIALS.md](docs/MEDIUM_HARD_TRIALS.md#osmand-only-extra-experiment-v49-v61-practice-runs).
The branch head is v62, two fixes for that failure made after the evaluation.

Earlier warm-up results (Wi-Fi and Camera 3/3 on v20, Contacts 3/3 on v28,
Timer and Clipboard unresolved) remain in [WARMUP_RESULTS.md](docs/WARMUP_RESULTS.md);
they are task-specific results on different versions.

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
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd AndroidWorldAvd -no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated -gpu host -no-window
```

The final evaluation used the headless host-GPU emulator (`-gpu host -no-window`);
see [SETUP.md](docs/SETUP.md) troubleshooting for why. Keep Windows from sleeping
during long batches. To reproduce the final evaluation and the improvement:

```powershell
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 42 43 44 --run-all-seeds --disable-skills
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact SimpleCalendarAddOneEvent OsmAndTrack --seeds 42 43 44 --run-all-seeds
# Additional OsmAnd experiment (after: git checkout osmand-extra-v61)
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 31 314 366 --run-all-seeds --disable-skills
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 31 314 366 --run-all-seeds
```

In another PowerShell terminal, from the project directory:

```powershell
.\run.ps1 -CheckOnly
.\.venv\Scripts\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42
```

The direct Python command is the agent entry point. Its seven task choices are
`SystemWifiTurnOn`, `CameraTakePhoto`, `ContactsAddContact`, `ClockTimerEntry`,
`SystemCopyToClipboard`, `SimpleCalendarAddOneEvent` and `OsmAndTrack`. Leave the emulator untouched during a recorded run.
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
| `agent_config.json` | Step/time bounds per task, sampling, history window and the per-task Skill map. |
| `instructions/autoglm.md` | Attributed native action contract; record prompt changes. |
| `instructions/skills/` | Optional per-task Skills (OsmAnd), loaded only for their task. |
| `autoglm_agent.py` | Observation, checked action adapter and visible completion criteria. |
| `run_task.py` | Official task initialization, app setup, video and verification. |
| `android_compat.py` | Narrow adapters: Windows temporary APK, fresh XML (with a bounded retry), keep the ADB server on retries. |
| `trajectory.py` | Immediately flushed readable and structured logs. |
| `evaluate_tasks.py` | Sequential evaluations with frozen sources; stops at the first failed clean trial unless `--run-all-seeds` (final evaluation); `--disable-skills` for the baseline. |
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
The course evaluation (easy/medium/hard, three runs each) is complete on v42;
see [FINAL_EVALUATION.md](docs/FINAL_EVALUATION.md).

The [approved evidence subset](docs/evidence/README.md) includes original trial
metadata and selected Timer/Clipboard trajectories and screenshots alongside
aggregate reports, and the final evaluation's batch tables, run summaries,
trajectories and key screenshots under `docs/evidence/final/`. Full recordings, the remaining archive, course PDFs/ZIPs,
credentials, dependency checkouts and environments remain local. The export
manifest identifies exactly which original files are published.
