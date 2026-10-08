"""Prepare a small public evidence/source export without changing original runs."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "docs/evidence"
BATCHES = (
    "easy_batch_20261008T064328_366877Z",
    "easy_batch_20261008T081652_065024Z",
    "easy_batch_20261008T082214_015428Z",
    "easy_batch_20261008T081108_236581Z",
)


def copy_record(source, destination, manifest):
    """Copy one original file and record its unchanged bytes by SHA256."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    manifest.append({"original": source.relative_to(ROOT).as_posix(),
                     "export": destination.relative_to(ROOT).as_posix(),
                     "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                     "bytes": source.stat().st_size})


def main():
    """Export named batches including failures, metadata and two diagnostic traces."""
    manifest, trial_names = [], set()
    # Keep entire selected batch result tables, including their failed attempts.
    for batch_name in BATCHES:
        batch = ROOT / "runs" / batch_name
        for name in ("RESULTS.md", "results.json", "batch.json", "config.json"):
            copy_record(batch / name, EXPORT / "runs" / batch_name / name, manifest)
        records = json.loads((batch / "results.json").read_text(encoding="utf-8"))
        trial_names.update(record["run_id"] for record in records)
    # Only metadata is exported for successful trials; full videos remain local.
    for run_id in sorted(trial_names):
        source = ROOT / "runs" / run_id
        for name in ("summary.json", "task.json", "config.json", "versions.json"):
            copy_record(source / name, EXPORT / "runs" / run_id / name, manifest)
    failures = ("trial_ClockTimerEntry_20261008T081804_857919Z",
                "trial_SystemCopyToClipboard_20261008T081108_888681Z")
    # Preserve causal before/after evidence for the two unresolved model errors.
    for run_id in failures:
        source = ROOT / "runs" / run_id
        for name in ("trajectory.txt", "trajectory.jsonl"):
            copy_record(source / name, EXPORT / "runs" / run_id / name, manifest)
        for step in sorted(source.glob("step_*")):
            for name in ("action.json", "execution_start.json", "result.json", "after.png"):
                if (step / name).is_file():
                    copy_record(step / name, EXPORT / "runs" / run_id / step.name / name, manifest)
            for observation in sorted(step.glob("observation_*")):
                if (observation / "screen.png").is_file():
                    destination = EXPORT / "runs" / run_id / step.name / observation.name / "screen.png"
                    copy_record(observation / "screen.png", destination, manifest)
    probe = "actual_control_feedback_probe_20261008T081535_861953Z"
    copy_record(ROOT / "runs" / probe / "result.json", EXPORT / "runs" / probe / "result.json", manifest)
    copy_record(ROOT / ".tools/final_evidence_20261008.json", EXPORT / "offline_verification.json", manifest)
    source_manifest = ROOT / ".review/upstream_20261008T075102_892043Z/manifest.json"
    copy_record(source_manifest, ROOT / "docs/sources/pinned_upstream.json", manifest)
    (EXPORT / "export_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    license_text = (ROOT / "instructions/LICENSE_AutoGLM.txt").read_text(encoding="utf-8")
    (ROOT / "LICENSE").write_text(license_text.replace("Copyright 2025 Zhipu AI", "Copyright 2026 Android World GUI agent contributors"), encoding="utf-8")
    print(json.dumps({"exported_files": len(manifest), "trial_count": len(trial_names),
                      "bytes": sum(item["bytes"] for item in manifest)}))


if __name__ == "__main__":
    main()
