"""Run the five agreed easy tasks sequentially, with three recorded trials each.

Use project Python: .venv\Scripts\python.exe -X utf8 evaluate_tasks.py
Every trial uses official initialization/verifiers through run_task.py. This
file schedules trials and summarizes evidence; it does not choose GUI actions.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from probe_connection import save_json
from run_task import TASKS

PROJECT = Path(__file__).resolve().parent


def source_hashes():
    """Fingerprint the agent contract so a batch cannot silently mix versions."""
    names = ("run_task.py", "autoglm_agent.py", "instructions/autoglm.md", "instructions/assessment.md", "trajectory.py", "android_compat.py")
    return {name: hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() for name in names}


def write_results(output, records):
    """Update the readable table after every trial, preserving partial batches."""
    lines = ["# Five easy tasks: recorded results", "", "Success requires valid initialization, video and official verifier PASS.",
        "One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.", "",
        "Clean finish also requires the model's finish reply, with no runtime error.", "",
        "| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |", "| --- | --- | --- | --- |"]
    # Group evidence by task; keep invalid trials visible rather than counting PASS.
    for task in TASKS:
        selected = [record for record in records if record["task"] == task]
        passed = sum(bool(record.get("verified_agent_success")) for record in selected)
        invalid = sum(not record.get("evaluation_valid", False) for record in selected)
        clean = sum(bool(record.get("clean_agent_success")) for record in selected)
        lines.append(f"| {task} | {passed}/{len(selected)} | {clean}/{len(selected)} | {invalid} |")
    lines += ["", "| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |", "| --- | --- | --- | --- | --- | --- | --- |"]
    # Each row links the actual summary; full traces and video are alongside it.
    for record in records:
        link = f"[summary](../{record['run_id']}/summary.json)" if record.get("run_id") else "runner error"
        outcome = record.get("verifier", "ERROR")
        if not record.get("evaluation_valid", False):
            outcome += " (invalid)"
        lines.append(f"| {record['task']} | {record['task_seed']} | {outcome} | {record.get('agent_done', False)} | {record.get('steps', 0)} | {record.get('duration_seconds', 0):.2f} | {link} |")
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_json(output / "results.json", records)


def main():
    """Freeze settings, schedule trials on one emulator, and retain all results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", nargs="+", choices=TASKS, default=TASKS)
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--observation", choices=["tree_first", "tree", "screenshot"])
    parser.add_argument("--require-model-finish", action="store_true", help="Compatibility flag: all batches now stop at the first failed clean-completion gate")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (PROJECT / ".venv").resolve():
        raise RuntimeError("Use project .venv Python")
    output = PROJECT / "runs" / datetime.now(timezone.utc).strftime("easy_batch_%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True)
    config = json.loads((PROJECT / "agent_config.json").read_text(encoding="utf-8"))
    if args.observation:
        config["observation"] = args.observation
        # An explicit batch-wide choice must override per-task defaults too.
        config["task_observations"] = {}
    save_json(output / "config.json", config)
    fingerprints = source_hashes()
    save_json(output / "batch.json", {"tasks": args.tasks, "task_seeds": args.seeds,
        "source_hashes": fingerprints, "purpose": "Three-case learning evaluation; failures are not discarded."})
    print(f"Batch evidence: {output}", flush=True)
    records = []
    write_results(output, records)
    # Trials are sequential because all agents would otherwise share one device.
    for task in args.tasks:
        # Different task seeds exercise different parameters; model seed stays frozen.
        for seed in args.seeds:
            if source_hashes() != fingerprints:
                raise RuntimeError("Source changed during the batch; stop rather than mix versions")
            before = set((PROJECT / "runs").glob(f"trial_{task}_*"))
            command = [sys.executable, "-X", "utf8", str(PROJECT / "run_task.py"),
                "--task", task, "--seed", str(seed), "--config", str(output / "config.json")]
            print(f"Starting {task}, task seed {seed}", flush=True)
            with (output / f"{task}_seed{seed}.console.txt").open("w", encoding="utf-8") as console:
                process = subprocess.run(command, cwd=PROJECT, stdout=console, stderr=subprocess.STDOUT)
            created = set((PROJECT / "runs").glob(f"trial_{task}_*")) - before
            if len(created) == 1 and (next(iter(created)) / "summary.json").exists():
                record = json.loads((next(iter(created)) / "summary.json").read_text(encoding="utf-8"))
            else:
                record = {"task": task, "verifier": "ERROR", "evaluation_valid": False,
                    "error": "Runner did not leave a unique final summary; inspect batch console."}
            record.update(task_seed=seed, process_exit_code=process.returncode)
            records.append(record)
            write_results(output, records)
            print(f"Finished {task}, seed {seed}: {record['verifier']}; valid={record['evaluation_valid']}; steps={record.get('steps', 0)}", flush=True)
            if not record.get("clean_agent_success"):
                print("Completion gate failed; preserve this attempt and repair before more trials.", flush=True)
                raise SystemExit(1)
    print(f"Completed {len(records)} trials. Read {output / 'RESULTS.md'}", flush=True)


if __name__ == "__main__":
    main()
