"""Decode recorded learning clips and add retrospective evidence without changing raw logs."""

import json
from pathlib import Path
import sys

import cv2

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from probe_connection import save_json


def main():
    """Inspect each existing clip and retain frame counts/timestamps for review."""
    # Review only completed learning trials; original run files remain unchanged.
    for folder in sorted((PROJECT / "runs").glob("trial_*")):
        if not (folder / "summary.json").exists():
            continue
        report = []
        # Decode every frame to detect corrupt/empty files, not just their existence.
        for path in sorted(folder.glob("video_*.mp4")):
            capture = cv2.VideoCapture(str(path))
            count, last_timestamp, last_frame = 0, None, None
            # Read to EOF so a valid header alone does not pass video inspection.
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                count += 1
                last_timestamp = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
                last_frame = frame
            report.append({"file": path.name, "decoded_frames": count,
                "last_frame_seconds": last_timestamp,
                "dimensions": list(last_frame.shape[:2]) if last_frame is not None else None,
                "note": "Variable frame timing; static intervals can have few frames. Decoding is not a full coverage guarantee."})
            capture.release()
        target = folder / "video_validation.json"
        if not target.exists():
            save_json(target, report)
        summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
        print(folder.name, summary["verifier"], report)


if __name__ == "__main__":
    main()
