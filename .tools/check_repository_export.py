"""Check the publication file set, credential exclusion and evidence integrity."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Inspect only tracked files and report checks without exposing any credential."""
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().rstrip("\0").split("\0")
    assignments = dict(line.partition("=")[::2] for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines() if "=" in line and not line.lstrip().startswith("#"))
    keys = [value.strip().strip("\"'").encode() for name, value in assignments.items() if "KEY" in name and value.strip()]
    excluded = (".env", ".venv/", ".tools/", ".review/", "android_world/", "course_content/", "runs/")
    manifest = json.loads((ROOT / "docs/evidence/export_manifest.json").read_text(encoding="utf-8"))
    approved_files = {item["export"] for item in manifest}
    # Check the exact publication set, never print the searched key values.
    for name in tracked:
        assert name == ".env.example" or not any(name == prefix or name.startswith(prefix) for prefix in excluded), name
        data = (ROOT / name).read_bytes()
        assert not any(key in data for key in keys), "Credential found in " + name
        assert b"-----BEGIN PRIVATE KEY-----" not in data, name
        assert len(data) < 5_000_000, "Unexpected large file " + name
        if Path(name).suffix in {".png", ".jpg", ".mp4", ".xml", ".jsonl"}:
            assert name in approved_files, "Artifact outside approved subset: " + name
    # The user approved this exact original export; verify working and staged bytes.
    for item in manifest:
        assert item["export"] in tracked, item["export"]
        for name in (item["original"], item["export"]):
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == item["sha256"], name
        staged = subprocess.check_output(["git", "show", ":" + item["export"]], cwd=ROOT)
        assert hashlib.sha256(staged).hexdigest() == item["sha256"], item["export"]
    from prepare_aggregate_results import BATCHES, FIELDS
    count = 0
    # Verify only status/numeric/version fields are exported and match originals.
    for batch_name in BATCHES:
        original = json.loads((ROOT / "runs" / batch_name / "results.json").read_text(encoding="utf-8"))
        expected = [{name: record.get(name) for name in FIELDS} for record in original]
        name = f"docs/evidence/batches/{batch_name}/results.json"
        assert name in tracked, name
        staged = subprocess.check_output(["git", "show", ":" + name], cwd=ROOT)
        assert json.loads(staged) == expected, name
        count += len(expected)
    broken = []
    pages = ("README.md", "CONTRIBUTING.md", "docs/README.md", "docs/SETUP.md",
             "docs/WARMUP_RESULTS.md", "docs/evidence/README.md", "instructions/AUTOGLM_SOURCE.md")
    # Validate the reader's current navigation, excluding explicitly historical references.
    for name in pages:
        page = ROOT / name
        for link in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if not re.match(r"https?://|#", link) and not (page.parent / link.split("#")[0]).exists():
                broken.append({"page": name, "link": link})
    assert not broken, broken
    result = {"tracked_files": len(tracked), "credential_in_tracked_files": False,
              "excluded_local_folders": True, "aggregate_outcomes_verified": count,
              "approved_export_hashes_verified": len(manifest),
              "raw_artifacts_tracked": sum(Path(name).suffix in {".png", ".jpg", ".mp4", ".xml", ".jsonl"} for name in tracked),
              "current_navigation_broken_links": broken,
              "tracked_bytes": sum((ROOT / name).stat().st_size for name in tracked)}
    (ROOT / ".tools/repository_export_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
