"""Read the frozen five-task trajectories; never call the model or emulator."""

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[1]
BATCH = PROJECT / "runs/easy_batch_20261007T191040_731527Z"
OUTPUT = BATCH / "diagnosis"
SYSTEM_PACKAGES = {"com.android.systemui", "com.google.android.inputmethod.latin"}


def load(path, default=None):
    """Read a saved JSON artifact if it exists."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def app_controls(tree):
    """Keep app labels and values while omitting unrelated keyboard suggestions."""
    return [{key: element.get(key) for key in ("package_name", "text", "hint_text",
        "content_description", "is_enabled", "is_editable", "bbox_pixels")}
        for element in tree if element.get("is_visible")
        and element.get("package_name") not in SYSTEM_PACKAGES
        and any(element.get(key) for key in ("text", "hint_text", "content_description"))]


def inspect_run(record):
    """Collect every step's supplied observations, raw replies and actual effects."""
    run = BATCH.parent / record["run_id"]
    steps = []
    # Inspect all attempts, including those rejected before any GUI execution.
    for folder in sorted(run.glob("step_*")):
        calls = []
        # Tree-first calls precede image fallback; alphabetical paths would put
        # screenshot before tree and misrepresent the actual request sequence.
        for response in sorted(folder.glob("*/response_*.json"),
                key=lambda path: (path.parent.name == "screenshot", path.name)):
            data = load(response)
            request = load(response.with_name(response.name.replace("response", "request")), {})
            calls.append({"path": str(response.relative_to(run)),
                "raw_reply": data["message"]["content"], "done_reason": data.get("done_reason"),
                "prompt_tokens": data.get("prompt_eval_count"), "output_tokens": data.get("eval_count"),
                "model_received_image": bool(request.get("messages", [{}, {}])[1].get("images")),
                "validation_error": load(response.with_name(response.name.replace("response", "validation_error")))})
        tree = load(folder / "tree.json", [])
        fresh = load(folder / "execution_observation.json")
        steps.append({"step": folder.name, "before_controls": app_controls(tree),
            "fresh_controls": app_controls(fresh) if fresh is not None else None,
            "after_controls": app_controls(load(folder / "after_tree.json", [])),
            "parsed_action": load(folder / "action.json"), "execution_result": load(folder / "result.json"),
            "calls": calls, "fallback": load(folder / "fallback.json")})
    return {"run_id": record["run_id"], "task": record["task"], "seed": record["task_seed"],
        "task_input": load(run / "task.json"), "official_outcome": record["verifier"],
        "stop_reason": record["stop_reason"], "error_class": record.get("error_class"), "steps": steps}


def make_sheet(records, task, specifications, filename):
    """Create a labelled inspection sheet from preserved screenshots."""
    selected = {record["task_seed"]: record for record in records if record["task"] == task}
    width, height = 300, 700
    canvas = Image.new("RGB", (width * 3, height * ((len(specifications) + 2) // 3)), "white")
    draw = ImageDraw.Draw(canvas)
    # Each tile links a seed/step to the original file; no original image is changed.
    for index, (seed, step, phase) in enumerate(specifications):
        record = selected[seed]
        relative = f"step_{step:03d}/{phase}.png"
        path = BATCH.parent / record["run_id"] / relative
        x, y = index % 3 * width, index // 3 * height
        draw.text((x + 5, y + 4), f"Seed {seed} / step {step} / {phase}", fill="black")
        if path.exists():
            picture = Image.open(path).convert("RGB")
            picture.thumbnail((width, height - 30))
            canvas.paste(picture, (x, y + 26))
        else:
            draw.text((x + 5, y + 35), "No saved image at this phase", fill="black")
    canvas.save(OUTPUT / filename)


def main():
    """Write separate diagnostic artifacts; leave original summaries unchanged."""
    OUTPUT.mkdir(exist_ok=True)
    records = load(BATCH / "results.json")
    reviews = [inspect_run(record) for record in records]
    (OUTPUT / "all_steps.json").write_text(json.dumps(reviews, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_sheet(records, "SystemWifiTurnOn", [(42, 1, "before"), (43, 1, "before"),
        (44, 1, "before"), (42, 4, "after"), (43, 1, "changed_before_execution"),
        (44, 1, "changed_before_execution")], "wifi.png")
    make_sheet(records, "CameraTakePhoto", [(seed, step, phase) for seed in [42, 43, 44]
        for step, phase in [(2, "before"), (2, "after"), (3, "before")]], "camera.png")
    make_sheet(records, "ClockTimerEntry", [(42, step, phase) for step, phase in
        [(1, "after"), (2, "before"), (2, "after"), (3, "before"), (5, "after"), (12, "before")]], "timer42.png")
    make_sheet(records, "ContactsAddContact", [(42, 3, "after"), (42, 5, "after"),
        (42, 6, "changed_before_execution"), (43, 1, "after"), (43, 2, "before"),
        (44, 2, "before")], "contacts.png")
    make_sheet(records, "SystemCopyToClipboard", [(42, 2, "before"), (43, 2, "before"),
        (44, 2, "before"), (44, 2, "after"), (44, 3, "before"), (44, 3, "model_input")], "clipboard.png")
    # Print compact evidence; detailed original context stays in its request file.
    for review in reviews:
        print(review["task"], review["seed"], review["official_outcome"])
        for step in review["steps"]:
            replies = [call["raw_reply"] for call in step["calls"]]
            print(step["step"], "executed result", bool(step["execution_result"]),
                "labels", [e["text"] or e["content_description"] or e["hint_text"]
                for e in step["before_controls"]][:10], "replies", replies)


if __name__ == "__main__":
    main()
