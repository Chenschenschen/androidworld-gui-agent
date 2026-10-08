"""Publish measured trajectory/performance notes after the final learning trial."""

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "runs/trial_ContactsAddContact_20261007T173637_269613Z"


def prepend_note(path, note):
    """Keep earlier evidence under an explicitly historical section."""
    file = ROOT / path
    old = file.read_text(encoding="utf-8")
    title, _, body = old.partition("\n")
    file.write_text(title + "\n\n" + note + "\n\n## Earlier record (historical)\n\n" + body.lstrip(), encoding="utf-8")


def main():
    """Use completed summaries only; keep original run evidence unchanged."""
    summary = json.loads((LATEST / "summary.json").read_text(encoding="utf-8"))
    result = summary["verifier"]
    latest_line = (f"Latest recorded Contacts trial: `{LATEST.name}`, official {result}, "
        f"initial {summary['initial_verifier_score']}/final {summary['verifier_score']}, "
        f"{summary['steps']} steps, {summary['model_calls_attempted']} calls, "
        f"{summary['duration_seconds']:.2f} seconds, no manual intervention.")
    rows = []
    # Preserve every completed diagnostic, including failures, in chronological order.
    for run in sorted((ROOT / "runs").glob("trial_ContactsAddContact_20261007T17*")):
        if not (run / "summary.json").exists():
            continue
        s = json.loads((run / "summary.json").read_text(encoding="utf-8"))
        replies = [json.loads(p.read_text(encoding="utf-8")) for p in run.glob("step_*/*/response_*.json")]
        wall = sum(reply.get("wall_seconds", 0) for reply in replies)
        rows.append(f"| [{s['version']}](../runs/{run.name}/summary.json) | {s['verifier']} | {s['steps']} | {len(replies)} | {s['duration_seconds']:.2f} | {wall:.2f} |")
    report = f"""# Trajectory logs and local performance

{latest_line}
The retained default is `learning_single_name_v7_gpu22`. Earlier official PASS
runs demonstrate contact creation capability; the failures demonstrate that
our adapted prompt/interface is still fragile. Hard-task capability and
repeatability remain unproven. These are learning trials, not a frozen evaluation.

## Read a run

Open `trajectory.txt` to read the events in order. `trajectory.jsonl` has one
structured JSON event per line. Each event is appended and flushed immediately;
a later failure does not erase previous steps. `trajectory.py` adapts the
labelled blocks and flush in the course `minimal_agent_example.py`, lines 30-35.

Each step records the observation and screenshot/tree paths, the actual model
request file, visible raw reply, validation feedback, chosen action, execution
start, observed field values, and timing. A selected action is explicitly marked
not yet executed. The final event separates model completion from official
verification. Complete request JSON lives beside the trace; images are linked
instead of inserting base64. Source/config/task/model identity and videos are
saved with the same run ID. Older reconstructed traces are explicitly labelled
retrospective; their timestamps are reconstruction times.

## What failed, and what changed

- The earlier `165206_708350Z` trial stopped after 12 actions with an unsaved
  form. It tapped a keyboard Dash key and left a leading dash in Phone.
- Targeted TYPE selects, clears and enters an editable field in one checked
  Android World action. v3 entered the number, but tapped the Create contact
  heading instead of Save and declared completion. Official FAIL.
- Named label grounding resolves the model's exact target against the current
  tree. v4/GPU16 correctly selected Save and earned PASS in 110.70 seconds.
  Its original summary has an inaccurate grounding label; `analysis.json`
  records the correction, backed by source/config/action files.
- v4/GPU22 wandered through filters. Prompt wording also changed: this is not
  a controlled hardware-versus-quality comparison. v5 restricted target labels
  to interactive app controls and removed stale coordinates from model history.
  It saved a name without a number and falsely declared completion.
- v6 rejects editable-field CLICKs with explicit TYPE feedback. It entered the
  phone and saved, but the resulting name was `Camila da Silva da Silva`.
  Its prediction of success was false. We retain raw predictions in the trace
  but omit them from factual recent-action history.
- v7 changes only the conditional contact procedure from v6: full task name
  once in First name, Last name blank. Same task seed, sampling, GPU offload,
  action checks and budgets. The model chooses every target/value and Save.
  The official verifier determines whether that change worked. One paired
  comparison cannot establish broad reliability; three repeated evaluations
  per final selected task are still required.

## GPU measurement

The same frozen tree and screenshot requests were sent with 16 and 22 GPU
layers. One warmup per setting was excluded; two cached tree repeats and one
image request were measured. No phone actions were executed by this probe.

| Offloaded layers | Peak device VRAM | Warm tree median | Screenshot request |
| --- | --- | --- | --- |
| 16 | 5,139 MiB / 62.8% | 7.16 s | 21.19 s |
| 22 | 6,393 MiB / 78.1% | 6.61 s | 19.25 s |

Tree time fell about 7.7%, screenshot time about 9.1%. Replies were identical,
including the wrong screenshot target. This measures a small speed improvement,
not an intelligence improvement. The 80% preference is interpreted as approximate
VRAM use; instantaneous GPU compute utilization cannot be fixed to 80%.
Evidence: [probe summary](../runs/gpu_offload_20261007T170529_775400Z/summary.json).

The BF16 engine residency reported by Ollama is about 9.9 GB, exceeding the
4070 Laptop's 8,188 MiB VRAM. Partial offload leaves CPU work. Screenshot prompt
processing alone took about 12.5 seconds in the GPU22 probe. In the older
156.88-second failed run, 13 model requests consumed 114.72 seconds (73%). The
remainder includes capture/stabilization, GUI execution, verification and recording;
we have not separately profiled every component. Repeated incorrect decisions
add requests and make total runtime worse. Warm-run loading was a small share.

## New recorded trials

| Version / evidence | Verifier | Steps incl. stop | Model calls | Total seconds | Model API wall seconds |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

The model is useful enough to have completed Contacts under our harness, but
these mixed-version trials do not establish reliable autonomous performance.
First repeat the same frozen version, then a new task seed, before expanding.
Keep tree-first and the bounded image fallback. Do not switch models, quantize,
or add a framework without discussing that separate decision.

## Run it yourself

From the project folder, with Ollama and AndroidWorldAvd running:

```powershell
.\\run.ps1 -CheckOnly
.\\run.ps1 -Task ContactsAddContact -Seed 42
```

Or use `.venv\\Scripts\\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42`.
Every invocation creates a unique run folder. Watch the TXT log while it runs.
Read `verified_agent_success` in the final summary; process completion is separate.
See [complete launch instructions](RUNNING_TASKS.md).
"""
    (ROOT / "docs/PERFORMANCE_AND_TRAJECTORIES.md").write_text(report, encoding="utf-8")
    decision = f"""Current update, 7 October 2026 (revision 0.10): {latest_line}

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
"""
    prepend_note("docs/PROJECT_DECISIONS.md", decision)
    prepend_note("docs/AGENT_DESIGN_DECISIONS.md", decision)
    prepend_note("docs/GROUNDING_EXPERIMENTS.md", latest_line + "\n\nCurrent experiments and limits: [PERFORMANCE_AND_TRAJECTORIES.md](PERFORMANCE_AND_TRAJECTORIES.md). Preserve earlier failures below.")
    prepend_note("docs/AGENT_BUILD_PLAN.md", latest_line + "\n\nLogging, targeted TYPE and named label grounding are implemented. GPU22 is measured. Next gate remains repeated success on a frozen version, followed by the agreed Wi-Fi/Markor/Calendar/hard tasks and required evaluations. See PERFORMANCE_AND_TRAJECTORIES.md; earlier proposed stages below are historical.")
    material = """Additional implementation review, 7 October 2026:

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
"""
    prepend_note("docs/MATERIAL_REVIEW.md", material)
    agents = ROOT / "AGENTS.md"
    old = agents.read_text(encoding="utf-8")
    start = old.index("This is a simple, explainable")
    old = "# Project working rules\n\n" + latest_line + "\n\nCurrent runnable version: v7/GPU22. TXT/JSONL traces flush each event. Model chooses visible target labels; Python checks grounding and targeted TYPE. Read docs/PERFORMANCE_AND_TRAJECTORIES.md and docs/RUNNING_TASKS.md. Repeatability remains pending.\n\n" + old[start:]
    # Replace the stale Current state section while retaining binding working rules.
    old = old[:old.index("## Current state")] + """## Current state

- Reviewed 6 PDFs / 218 pages and all 3 ZIPs / 24 course files; originals preserved.
- Local GELab-Zero BF16 via Ollama; project Python 3.11.17 `.venv`; Android World
  installed and emulator-5554 connected. Preserve Windows temporary-APK adapter.
- Standalone `run.ps1` and direct `run_task.py` support Contacts/Wi-Fi. Readiness,
  official initialization, logging, video and official verification exercised.
- One agent with bounded step/time/API/correction/image budgets. Tree-first;
  unique visible-label grounding, targeted TYPE, conditional inline contact guide,
  exact per-run scratch and recent observed results. No fixed GUI action replay.
- Current default uses 22 GPU layers: measured peak VRAM 78.1%, modest speed gain.
- Earlier Contact PASS runs and all FAILs are preserved. No reliability claim:
  repeat the frozen current version and then a fresh seed before expanding.
- Remaining scope: agreed Wi-Fi/Markor stages, SimpleCalendarAddOneEvent and
  jointly selected MarkorMergeNotes/OsmAndTrack. Three runs per final task,
  at least easy/medium/hard, before/after evidence, and presentation still required.
"""
    agents.write_text(old, encoding="utf-8")
    running = ROOT / "docs/RUNNING_TASKS.md"
    old = running.read_text(encoding="utf-8")
    begin = old.index("Launcher tested")
    end = old.index("## Start the services")
    old = old[:begin] + latest_line + "\n\nLauncher execution, recording and verification work independently of Codex.\nTask success remains prompt-sensitive; see PERFORMANCE_AND_TRAJECTORIES.md.\nThe current default uses named label grounding, direct targeted TYPE and GPU22.\n\n" + old[end:]
    begin = old.index("Inspect `task.json`")
    old = old[:begin] + """Start with `trajectory.txt` for readable step-by-step events, or
`trajectory.jsonl` for structured events. Both are written during the run.
Request files hold the actual model context; raw replies, actions, before/after
screens and observed field values show what happened. Videos share the run ID.
Read `task.json`, `summary.json` and any `analysis.json` alongside them.
Process exit and launcher completion are separate from official PASS.
Official initialization resets test app data on AndroidWorldAvd.

## Recommended learning order

1. Read the latest successful and failed traces, including the actual Save step.
   Explain the model decision, label-to-index/pixel grounding, targeted TYPE,
   action feedback and separate official verifier.
2. Repeat a frozen version on Contacts, then a fresh task seed. Preserve failures.
   Change one variable per improvement comparison and keep all source/settings.
3. Advance to the agreed Wi-Fi/Markor tasks, then Calendar and the jointly
   selected harder memory/multi-app task after the loop is understood.
4. Freeze final settings and conduct three recorded evaluations per selected
   task, with the required failure analysis and comparable before/after result.
"""
    running.write_text(old, encoding="utf-8")
    walk = ROOT / "docs/AGENT_WALKTHROUGH.md"
    old = walk.read_text(encoding="utf-8")
    old = old.replace("converts an index into pixels.", "resolves a unique visible label to its current index/pixels. Targeted TYPE also checks that the target is editable.")
    walk.write_text(old, encoding="utf-8")
    prepend_note("docs/AGENT_WALKTHROUGH.md", latest_line + "\n\nCurrent input/output flow: tree-first observation → model target label and exact value → checked current grounding → GUI action → observed result → next step. TXT/JSONL log every event. TYPE focuses and replaces the chosen editable field; CLICK is for noneditable controls. Current conditional guide uses the full name once in First name. Read PERFORMANCE_AND_TRAJECTORIES.md for the failures motivating each change; the example below describes the earlier v2 PASS, not current source syntax.")
    print(latest_line)


if __name__ == "__main__":
    main()
