# Five-task learning evaluation — 7 October 2026

The complete subsequent review is in
[TRAJECTORY_FAILURE_ANALYSIS.md](TRAJECTORY_FAILURE_ANALYSIS.md): all 15 trials
and 78 responses inspected. It corrects the Wi-Fi seed 44 diagnosis (a changing
time widget, plus a wrong Messages tap), identifies status-bar-only model input
and blocked fresh-observation recovery, and compares the earlier Contacts PASS.
Use that per-run analysis when explaining causes; the raw measurements below
remain unchanged.

This is an honest capability check, not the final course evaluation. These five
tasks are easy warm-ups. The agreed Calendar and harder multi-app/memory task
remain in scope. The official verifier decides success; model COMPLETE does not.

## Experimental conditions

Local `gelab-zero-4b-preview:latest` through Ollama; GPU22, BF16, fixed model
sampling seed 42. Task seeds 42, 43 and 44 generate separate instances. Each run
has a 12-step/900-second limit, official initialization and verification, source
and configuration snapshots, trajectory TXT/JSONL, actual request/reply files,
before/after screenshots and video. Speed tuning was paused.

Leave the emulator untouched during every evaluation. The user confirmed manual
interaction during batch `easy_batch_20261007T182934_895562Z`; its separate review
excludes that entire batch from unattended repeatability claims. Originals are
preserved. The exact interaction interval is unknown.

## Baseline and small improvement

The unattended v9 batch `easy_batch_20261007T184229_043036Z` completed all fifteen
attempts: every task scored 0/3. Wi-Fi chose unrelated Settings pages. The other
twelve trials were blocked before opening their apps by a freshness check that
also applied to fixed app launches. All videos decode and trace references
exist; see that batch's `artifact_review.json`.

Version v10 limits that check to pointing/typing actions. For Camera, Timer,
Contacts and Clipboard this changes the launch guard while retaining tree-first
input. Wi-Fi also changes to screenshot input after three tree-first failures;
its comparison therefore changes two variables and cannot isolate either one's
effect. Same model, GPU, sampling, seeds and budgets.

The completed v10 batch is `easy_batch_20261007T191040_731527Z`. All fifteen
attempts finished and received an official verifier result. These are the raw
GUI-agent outcomes; infrastructure and harness failures remain in the counts.

| Task | Official PASS / attempts | Success rate |
| --- | --- | --- |
| SystemWifiTurnOn | 1/3 | 33.3% |
| CameraTakePhoto | 0/3 | 0% |
| ClockTimerEntry | 0/3 | 0% |
| ContactsAddContact | 0/3 | 0% |
| SystemCopyToClipboard | 0/3 | 0% |

Therefore **none currently demonstrates three successful repeats**. Every run
has initial verifier 0, recorded trajectory, request references and decodable
video. The completed artifact audit reports no missing/unreadable evidence;
decoding alone does not prove gap-free temporal coverage. The runtime's
`evaluation_valid` field checks initialization and recording, and must not be
read as proof that observation infrastructure was healthy. The separate
`evaluation_review.json` and this analysis record those limitations without
rewriting original summaries. This is not a clean model-only capability score.

Compare v9 0/15 to v10 1/15 only as a diagnostic before/after result. It does not
establish statistical reliability or isolate the Wi-Fi improvement's cause.
Earlier individual Contacts successes used other versions and cannot replace
these three-seed results. Read the batch's `RESULTS.md` for links to every run.

## Specific failure evidence

- Wi-Fi seed 42 in v10 passed: initial verifier 0, final verifier 1. The five-step
  trace opens Settings, Network & internet, Internet, toggles Wi-Fi, then stops.
  The saved Switch state changes from unchecked to checked. This is GUI-agent
  success, with no host command enabling Wi-Fi in that trial.
- Wi-Fi seed 43's initial tree contains the modal
  `com.google.androidenv.accessibilityforwarder keeps stopping`, while its
  saved screenshot already shows Home. The fresh tree shows Home too. This is
  inconsistent observation evidence; the exact modal timing is unproven. The
  proposed tap points to Messages on Home, despite its claimed Settings intent.
  Seed 44 instead stops on an unrelated time-widget change, with another wrong
  Messages tap. Both observation/harness and model grounding issues are present.
- Camera seed 42 opens Camera, targets Shutter and declares COMPLETE. The
  accessibility tree advertises Shutter while both the captured screenshot and
  a frame extracted from the original video show the camera loading screen.
  No photo passes the verifier. The exact cause of the camera loading problem
  remains unproven. The emulator configuration specifies a virtualscene rear
  camera and emulated front camera. Do not infer successful capture from the
  tree or dispatch returning.
- Contacts seed 42 (`trial_ContactsAddContact_20261007T192819_171100Z`) correctly
  types `Camila da Silva` into First name at step 3, then puts `Camila` into
  Last name at step 4 and replaces First name with `da Silva` at step 5.
  The actual observed fields confirm those changes. This is a `lost_value`
  model error despite the inline instruction to retain the full name once.
  The proposed phone action at step 6 was blocked by a changed tree, so it did
  not enter the number or save the contact. The final runtime summary records
  the environment exception; this analysis also records the earlier model error.
  The before/fresh Phone target has identical bounds and state. The meaningful
  tree difference is in Gboard clipboard suggestions. The whole-scene guard
  therefore also has a false-stop case: unrelated keyboard suggestions can
  block an unchanged target. Repair this with target-specific freshness checking
  in a separate measured stage; do not disable checking actual screen changes.
- Timer seed 42 requests `20h 07m 01s`, unstarted. The trace leaves the Timer
  route and selects Alarm, edits alarm-hour/minute controls, then declares timer
  completion at step 12. The verifier returns 0. This is wrong-task navigation
  followed by `false_done`; its source observation transitions still require
  inspection. Seeds 43 and 44 also encounter action-format/target validation
  errors. A syntactically accepted action is not proof of correct task intent.
- Clipboard seed 42 opens Clipper, then produces invalid target/coordinate
  arguments at step 2, including after the bounded screenshot fallback. Only
  the launch executes. The official clipboard verifier returns 0. Clipper is
  verifier infrastructure; launching it does not copy the task text. The GUI
  route through an editable app needs to be checked in the next small stage.

## What the delays mean

In the earlier 156.875-second Contacts trial, recorded model API waits totalled
114.72 seconds (about 73%). Local inference was the largest measured component
there. These waits include request overhead, prompt processing and generation.
They are not the entire delay between GUI actions: capture, stabilization,
argument validation, dispatch and recording coordination also take time.

With repeated UIAutomator captures, observation overhead can dominate: one v9
Wi-Fi trial took about 320 seconds with about 90 seconds of model API waits.
Therefore the delay is not always primarily inference. Read per-step model and
execute-and-observe timings rather than attributing every pause to GPU speed.
In the v10 successful Wi-Fi trial, logged API waits total 91.891 seconds of a
212.219-second whole run (about 43%). This denominator includes setup and
verification as well as the agent loop. It is not an isolated inference-speed
benchmark or an exact measurement of every inter-action interval.

## Next bounded repair stage

First isolate the crash/stale-observation problem in a connection probe before
another large batch. Use Android World's supported UIAutomator backend as an
alternative, disable only its unused forwarder service on the test emulator,
and check that screenshot and labels describe the same screen. XML accessibility
does not expose every attribute of the streamed tree; editable fields need the
generic EditText-class mapping. This is a proposal pending its probe, not an
already measured improvement or a successful task result.

Then run one task from an officially reset state, inspect its trace together,
and repeat three cases only after that small test provides useful evidence.
Keep every failure. No task-specific direct database, file or clipboard writes
may be counted as GUI-agent success.

## Reproduction

From the project folder, with Ollama and AndroidWorldAvd running:

```powershell
.\run.ps1 -CheckOnly
.\run.ps1 -Task ContactsAddContact -Seed 42
& .venv\Scripts\python.exe -X utf8 evaluate_tasks.py
```

These programs run independently of Codex. Every invocation creates new evidence
folders. Normal program exit means the trial was recorded, not that it passed.
