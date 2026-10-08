"""Readable and structured trajectory events, adapted from the course TXT trace.

The course minimal_agent_example.py writes labelled blocks and flushes each one.
Here we also record GUI observations/actions/results and a JSONL event stream.
Only visible model replies are logged; no internal reasoning is invented.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys


def log_event(output, event, data, step=None):
    """Append and flush one event immediately, preserving evidence on interruption."""
    output = Path(output)
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {"recorded_at_utc": timestamp, "step": step, "event": event, "data": data}
    with (output / "trajectory.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
        file.flush()
    label = f"STEP {step:03d}" if step is not None else "RUN"
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2)
    with (output / "trajectory.txt").open("a", encoding="utf-8") as file:
        file.write(f"\n--- {timestamp} | {label} | {event} ---\n{text}\n")
        file.flush()


def rebuild_trajectory(output):
    """Reconstruct a clearly labelled readable trace from an older run's evidence."""
    output = Path(output).resolve()
    if any((output / name).exists() for name in ("trajectory.txt", "trajectory.jsonl")):
        raise FileExistsError("Preserve existing trajectory files; do not overwrite")
    log_event(output, "RETROSPECTIVE TRACE", {
        "source": str(output), "note": "Rebuilt from saved files; recorded_at is reconstruction time, not original event time."})
    # Saved metadata describes the actual old run; current config is irrelevant.
    for name in ("config.json", "versions.json", "task.json"):
        if (output / name).exists():
            log_event(output, name, json.loads((output / name).read_text(encoding="utf-8")))
    # Replay file contents for explanation only; no environment/model calls occur.
    for folder in sorted(output.glob("step_*")):
        step = int(folder.name.split("_")[-1])
        log_event(output, "OBSERVATION", {"screenshot": f"{folder.name}/before.png", "tree": f"{folder.name}/tree.json"}, step)
        # The runtime tries tree before screenshot; keep that actual call ordering.
        for mode in ("tree", "screenshot"):
            for request in sorted((folder / mode).glob("request_*.json")):
                log_event(output, "MODEL REQUEST", json.loads(request.read_text(encoding="utf-8")), step)
                response = request.with_name(request.name.replace("request_", "response_"))
                if response.exists():
                    data = json.loads(response.read_text(encoding="utf-8"))
                    log_event(output, "MODEL REPLY", data["message"]["content"], step)
                    log_event(output, "MODEL TIMING", {"mode": mode, "wall_seconds": data.get("wall_seconds")}, step)
                invalid = request.with_name(request.name.replace("request_", "validation_error_"))
                if invalid.exists():
                    log_event(output, "VALIDATION ERROR", json.loads(invalid.read_text(encoding="utf-8")), step)
        # A selected action alone does not confirm that it executed.
        for name in ("fallback.json", "action.json", "execution_start.json", "result.json"):
            if (folder / name).exists():
                log_event(output, name, json.loads((folder / name).read_text(encoding="utf-8")), step)
        if (folder / "after_tree.json").exists():
            elements = json.loads((folder / "after_tree.json").read_text(encoding="utf-8"))
            log_event(output, "OBSERVED FIELDS AFTER", {"screenshot": f"{folder.name}/after.png",
                "fields": [{"hint": e["hint_text"], "text": e["text"]} for e in elements if e["is_editable"]]}, step)
    log_event(output, "STOP AND OFFICIAL VERIFICATION", json.loads((output / "summary.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    # Each supplied path is an old run to explain; never execute its GUI actions.
    for run_path in sys.argv[1:]:
        rebuild_trajectory(run_path)
