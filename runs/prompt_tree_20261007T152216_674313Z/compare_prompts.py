"""Compare two prompts on saved indexed observations; execute no Android actions.

Adapted experiment pattern: course D2 step2_prefix_cache.py and lab_support.py.
Only the three examples differ within each pair. Fixed saved contexts make
this an interface experiment, not an official task evaluation.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import statistics
import sys
import time
from types import SimpleNamespace
import urllib.request

import numpy as np
from PIL import Image
from android_world.env.representation_utils import BoundingBox, UIElement
from gelab_agent import parse_reply, prompt_for, tree_text, validate_action
from probe_connection import save_json

PROJECT = Path(__file__).resolve().parent
CASES = [
    ("contacts", "trial_ContactsAddContact_20261007T144105_002848Z", "step_005",
     "Interface probe: enter the first name Camila into the already selected First name field. The keyboard is open. Choose TYPE with the exact first name. Do not complete the task."),
    ("settings", "trial_SystemWifiTurnOn_20261007T145351_459076Z", "step_002",
     "Interface probe: open Settings from this launcher. Choose AWAKE settings or CLICK its listed index. Do not report task completion."),
]


def load_case(run, step, instruction):
    """Reconstruct one immutable saved observation and its exact probe context."""
    folder = PROJECT / "runs" / run / step
    elements = json.loads((folder / "tree.json").read_text(encoding="utf-8"))
    controls = []
    # Rebuild only the official dataclasses needed for argument/index validation.
    for element in elements:
        item = dict(element)
        for key in ("bbox", "bbox_pixels"):
            if item[key] is not None:
                item[key] = BoundingBox(**item[key])
        controls.append(UIElement(**item))
    state = SimpleNamespace(pixels=np.array(Image.open(folder / "before.png")), ui_elements=controls)
    original = json.loads((folder / "request_0.json").read_text(encoding="utf-8"))
    context = original["messages"][1]["content"].split("Current screenshot attached.")[0]
    context += "Current indexed tree:\n" + tree_text(elements) + "\n" + instruction
    return state, context


def call(payload, folder, timeout):
    """Save request before sending and preserve raw local response and elapsed time."""
    save_json(folder / "request.json", payload)
    start = time.monotonic()
    request = urllib.request.Request("http://localhost:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
        data["wall_seconds"] = time.monotonic() - start
        save_json(folder / "response.json", data)
        return data
    except Exception as error:
        save_json(folder / "error.json", {"error": str(error), "wall_seconds": time.monotonic() - start})
        raise


def intended_action(case, fields):
    """Assess correctness against the explicitly stated saved-screen probe goal."""
    if case == "contacts":
        return fields["action"] == "TYPE" and fields.get("value") == "Camila"
    return (fields["action"] == "AWAKE" and fields.get("value", "").lower() == "settings") or (
        fields["action"] == "CLICK" and fields.get("index") == "19")


def main():
    """Alternate paired conditions, with three repetitions and one correction each."""
    if Path(sys.prefix).resolve() != (PROJECT / ".venv").resolve():
        raise RuntimeError("Use .venv\\Scripts\\python.exe")
    config = json.loads((PROJECT / "agent_config.json").read_text(encoding="utf-8"))
    output = PROJECT / "runs" / datetime.now(timezone.utc).strftime("prompt_tree_%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True)
    print("Evidence:", output, flush=True)
    save_json(output / "config.json", {**config, "kind": "saved_tree_prompt_comparison", "repeats": 3,
        "changed_variable": "three syntax examples", "executed_actions": 0})
    shutil.copyfile(__file__, output / "compare_prompts.py")
    shutil.copyfile(PROJECT / "gelab_agent.py", output / "gelab_agent.py")
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10) as response:
        save_json(output / "model_tags.json", json.load(response))
    records = []
    deadline = time.monotonic() + config["max_seconds"]
    try:
        # Each case holds task, observation, hardware, sampling, and history fixed.
        for case, run, step, instruction in CASES:
            state, context = load_case(run, step, instruction)
            save_json(output / f"{case}_source.json", {"run": run, "step": step, "instruction": instruction})
            # Alternate A/B order to reduce systematic warm-cache/order bias.
            for repeat in range(3):
                for examples in ((False, True) if repeat % 2 == 0 else (True, False)):
                    condition = "examples" if examples else "base"
                    folder = output / f"{case}_{repeat + 1}_{condition}"
                    folder.mkdir()
                    messages = [{"role": "system", "content": prompt_for("tree", examples)},
                                {"role": "user", "content": context}]
                    record = {"case": case, "repeat": repeat + 1, "condition": condition,
                        "first_valid": False, "first_correct": False, "final_valid": False,
                        "final_correct": False, "executed": False, "calls": []}
                    # Original reply and at most one invalid-format correction; no action executes.
                    for attempt in range(2):
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise RuntimeError("Comparison time budget exhausted")
                        request_folder = folder / f"attempt_{attempt}"
                        request_folder.mkdir()
                        payload = {"model": config["model"], "messages": messages, "stream": False,
                            "keep_alive": "10m", "options": config["options"]}
                        print(case, repeat + 1, condition, "attempt", attempt, flush=True)
                        data = call(payload, request_folder, min(remaining, config["request_timeout"]))
                        record["calls"].append(data["wall_seconds"])
                        raw = data["message"]["content"]
                        try:
                            if data.get("done_reason") == "length":
                                raise ValueError("Truncated reply")
                            fields = parse_reply(raw)
                            action = validate_action(fields, state, "tree")
                            correct = intended_action(case, fields)
                            record.update(final_valid=True, final_correct=correct)
                            if attempt == 0:
                                record.update(first_valid=True, first_correct=correct)
                            save_json(request_folder / "assessment.json", {"valid": True, "correct": correct,
                                "fields": fields, "action": action, "executed": False})
                            print("Valid:", correct, fields, flush=True)
                            break
                        except ValueError as error:
                            save_json(request_folder / "assessment.json", {"valid": False, "error": str(error), "executed": False})
                            messages += [{"role": "assistant", "content": raw}, {"role": "user",
                                "content": f"Invalid reply: {error}. Correct the single action; no action executed."}]
                    records.append(record)
                    save_json(output / "progress.json", records)
    finally:
        summary = []
        # Aggregate counts separately from timing; the first request may include cold loading.
        for condition in ("base", "examples"):
            rows = [row for row in records if row["condition"] == condition]
            times = [seconds for row in rows for seconds in row["calls"]]
            summary.append({"condition": condition, "cases": len(rows),
                "first_valid": sum(row["first_valid"] for row in rows),
                "first_correct": sum(row["first_correct"] for row in rows),
                "final_valid": sum(row["final_valid"] for row in rows),
                "final_correct": sum(row["final_correct"] for row in rows),
                "median_wall_seconds_including_load_and_corrections": statistics.median(times) if times else None})
        save_json(output / "summary.json", {"kind": "interface_probe", "executed_actions": 0,
            "records": records, "summary": summary, "note": "Fixed seed, two saved screens, no official task outcomes. Timings include cold/cache effects; inspect raw metrics."})
        print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
