"""Export a small reproducible audit of completed Files trials, without secrets."""
import hashlib
import json
from pathlib import Path
import cv2

ROOT = Path(__file__).resolve().parents[1]
entries = []
# Visit every preserved completed trial; active folders have no final summary.
for folder in sorted((ROOT / "runs").glob("trial_FilesMoveFile_*")):
    if not (folder / "summary.json").exists():
        continue
    summary = json.loads((folder / "summary.json").read_text())
    task = json.loads((folder / "task.json").read_text())
    json_files = list(folder.rglob("*.json"))
    # Parse complete JSON files and append-only trajectory records without printing inputs.
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (folder / "trajectory.jsonl").read_text().splitlines()]
    videos = []
    for name in summary["videos"]:
        capture = cv2.VideoCapture(str(folder / name))
        expected = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0
        while capture.read()[0]:
            count += 1
        capture.release()
        assert count > 0 and count == expected, (folder.name, name)
        videos.append({"file": name, "decoded_frames": count,
                       "sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest()})
    entry = {key: summary.get(key) for key in ("run_id", "version", "agent_done", "verifier",
        "steps", "gui_actions_dispatched", "model_calls_attempted", "evaluation_valid",
        "clean_agent_success", "error_class", "stop_reason", "duration_seconds")}
    entry.update(parameters=task["parameters"], seed=task["seed"],
        initialization_mode=task["initialization_mode"], json_files_parsed=len(json_files),
        trajectory_events_parsed=len(events), videos=videos,
        source_sha256={str(path.relative_to(folder / "source")):
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (folder / "source").rglob("*") if path.is_file()})
    config = json.loads((folder / "config.json").read_text())
    config.pop("task_seed", None)
    entry["config_sha256_without_seed"] = hashlib.sha256(
        json.dumps(config, sort_keys=True).encode()).hexdigest()
    entries.append(entry)
v53 = [entry for entry in entries if entry["version"] == "autoglm_api_v53_checked_container_labels"]
assert all(entry["source_sha256"] == v53[0]["source_sha256"] for entry in v53)
clean_v53 = [entry for entry in v53 if entry["clean_agent_success"]]
assert all(entry["config_sha256_without_seed"] == clean_v53[0]["config_sha256_without_seed"]
           for entry in clean_v53)
output = {"scope": "Scoped linked GUI trials; official verifier; not independent benchmark resets",
    "manual_preparation": "User confirmed returning recipe to easy before the fresh v53 sequence",
    "unchanged_recipe_sha256": "82287c26534ac3697a68f703d49d49e00594c123ea5801d6ad164986759d4416",
    "v53_source_snapshots_identical": True,
    "clean_v53_settings_identical_except_seed": True, "runs": entries}
(ROOT / "docs/evidence/files_move_audit.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({"runs_audited": len(entries), "json_files_parsed": sum(e["json_files_parsed"] for e in entries),
    "videos_decoded": sum(len(e["videos"]) for e in entries), "v53_sources_identical": True}))
