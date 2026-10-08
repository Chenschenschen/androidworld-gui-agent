"""Audit immutable Files trial artifacts and name successful presentation copies."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
import cv2

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    """Return the SHA256 of an artifact without printing its contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(run_id, label):
    """Copy one clean run and verify every file against the preserved original."""
    source = ROOT / "runs" / run_id
    summary = json.loads((source / "summary.json").read_text())
    if not summary["clean_agent_success"]:
        raise ValueError("Only clean successes can receive presentation labels")
    destination = ROOT / "runs/presentation" / label
    if not destination.exists():
        shutil.copytree(source, destination)
    files = list(path for path in source.rglob("*") if path.is_file())
    # Verify all source/settings/log/image files, including original videos.
    for path in files:
        assert digest(path) == digest(destination / path.relative_to(source)), path
    videos = []
    # Decode every frame; a nonempty MP4 alone does not establish usable recording.
    for name in summary["videos"]:
        original = source / name
        capture = cv2.VideoCapture(str(original))
        expected = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0
        while capture.read()[0]:
            count += 1
        capture.release()
        assert count > 0 and count == expected, (name, count, expected)
        named = ROOT / "runs/presentation" / f"{label}_{name}"
        if not named.exists():
            shutil.copy2(original, named)
        assert digest(named) == digest(original)
        videos.append({"named_video": str(named.relative_to(ROOT)),
                       "sha256": digest(named), "decoded_frames": count})
    index_path = ROOT / "runs/presentation/index.json"
    index = json.loads(index_path.read_text())
    entry = {"label": label, "original_run_id": run_id,
             "files_verified_identical": len(files), "videos": videos}
    index = [item for item in index if item["label"] != label] + [entry]
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    archive(sys.argv[1], sys.argv[2])
