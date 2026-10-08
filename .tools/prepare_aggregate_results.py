"""Export only non-sensitive result fields; preserve all original local evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCHES = (
    "easy_batch_20261008T064328_366877Z",
    "easy_batch_20261008T081652_065024Z",
    "easy_batch_20261008T082214_015428Z",
    "easy_batch_20261008T081108_236581Z",
)
FIELDS = ("task", "task_seed", "run_id", "version", "prompt_version", "verifier",
          "agent_done", "steps", "duration_seconds", "evaluation_valid",
          "clean_agent_success", "stop_reason")


def main():
    """Write aggregate outcome reports with no screenshots, inputs, replies or paths."""
    count = 0
    # Whitelist numeric/status fields rather than trying to redact arbitrary logs.
    for batch_name in BATCHES:
        originals = json.loads((ROOT / "runs" / batch_name / "results.json").read_text(encoding="utf-8"))
        records = [{name: record.get(name) for name in FIELDS} for record in originals]
        destination = ROOT / "docs/evidence/batches" / batch_name
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "results.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
        lines = ["# Aggregate recorded results", "", "Derived from original local summaries. No raw task inputs, screenshots, replies or videos are published.", "",
                 "Clean requires valid recording/initialization, model finish, official PASS and no runtime error.", "",
                 "| Task | Seed | Verifier | Model finish | Steps | Seconds | Clean | Original run ID |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for record in records:
            lines.append(f"| {record['task']} | {record['task_seed']} | {record['verifier']} | {record['agent_done']} | {record['steps']} | {record['duration_seconds']:.2f} | {record['clean_agent_success']} | {record['run_id']} |")
        (destination / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        count += len(records)
    (ROOT / "docs/evidence/clipboard_probe.json").write_text(json.dumps({"executed": False, "rejects_previous_false_finish": False,
        "kind": "aggregate saved-screen probe outcome", "benchmark_run": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"aggregate_trial_count": count, "raw_evidence_exported": False}))


if __name__ == "__main__":
    main()
