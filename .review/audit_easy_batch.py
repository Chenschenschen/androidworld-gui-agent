"""Audit completed recorded trials without executing model or Android actions."""

import json
from pathlib import Path
import sys

import cv2


def inspect_run(run):
    """Check the trace, requests and videos; retain original runtime summaries."""
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (run / "trajectory.jsonl").read_text(encoding="utf-8").splitlines()]
    issues = []
    if events[-1]["event"] != "STOP AND OFFICIAL VERIFICATION":
        issues.append("Missing final verification event")
    # Each compact request event must reference the full context saved on disk.
    for event in events:
        if event["event"] == "MODEL REQUEST":
            path = event["data"].get("context_and_settings")
            if path and not (run / path).is_file():
                issues.append("Missing request: " + path)
    videos = []
    # Decode each clip to EOF. Variable frame timing alone is not coverage proof.
    for path in sorted(run.glob("video_*.mp4")):
        cap = cv2.VideoCapture(str(path))
        frames, last, dimensions = 0, 0, None
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames += 1
            last = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            dimensions = [frame.shape[1], frame.shape[0]]
        cap.release()
        if frames == 0:
            issues.append("Unreadable video: " + path.name)
        videos.append({"path": path.name, "frames_decoded": frames,
            "last_timestamp_seconds": round(last, 3), "dimensions": dimensions})
    if summary.get("evaluation_valid") and not videos:
        issues.append("Valid evaluation claims no video")
    actions = []
    start_actions = []
    # Show model-selected targets and exact values, separate from model predictions.
    for path in sorted(run.glob("step_*/action.json")):
        action = json.loads(path.read_text(encoding="utf-8"))
        native = action["native"]
        executed = (path.parent / "execution_start.json").exists() and (path.parent / "result.json").exists()
        actions.append({"step": path.parent.name, "action": native, "executed_result_recorded": executed})
        if summary["task"] == "ClockTimerEntry" and executed and native["action"] in {"CLICK", "LONGPRESS"}:
            tree = json.loads((path.parent / "tree.json").read_text(encoding="utf-8"))
            dispatch = action["android"]
            # Identify a Start control under the actual dispatched point, including
            # screenshot actions; never infer execution from a proposed target alone.
            for element in tree:
                bounds = element.get("bbox_pixels")
                labels = [element.get("text"), element.get("content_description")]
                if bounds and any(label and label.casefold() == "start" for label in labels):
                    if bounds["x_min"] <= dispatch["x"] < bounds["x_max"] and bounds["y_min"] <= dispatch["y"] < bounds["y_max"]:
                        start_actions.append(path.parent.name)
    return {"run_id": run.name, "task": summary["task"], "issues": issues,
        "trace_events": len(events), "video_decode_checks": videos, "actions": actions,
        "timer_start_actions": start_actions,
        "limits": "Video decoding checks readability, not complete temporal coverage. Start-action checks use saved GUI labels; inspect video for ambiguous cases."}


def main():
    """Audit the chosen batch and write a separate review artifact."""
    batch = Path(sys.argv[1]).resolve()
    records = json.loads((batch / "results.json").read_text(encoding="utf-8"))
    reviews = []
    # The audit reads each completed run once; it never changes its summary.
    for record in records:
        if record.get("run_id"):
            review = inspect_run(batch.parent / record["run_id"])
            reviews.append(review)
            print(review["task"], review["run_id"], "issues:", review["issues"], flush=True)
    (batch / "artifact_review.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
