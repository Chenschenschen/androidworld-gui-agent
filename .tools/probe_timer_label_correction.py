"""Test the checked Timer label contract on a real saved screen; no device actions."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import urllib.request
import numpy as np
from android_world.env.representation_utils import UIElement, BoundingBox

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings, parse_action, convert_action
from probe_connection import save_json


def main():
    """Allow one format correction, then require the model's single-zero label."""
    source = ROOT / "runs/trial_ClockTimerEntry_20261007T210910_992181Z/step_004/observation_0"
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_timer_label_correction_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    payload = json.loads((source / "request_0.json").read_text())
    payload["messages"][0]["content"] += '\nFor the fresh Timer keypad, choose an exact visible label using do(action="Tap", label="observed label"). Python resolves its actual GUI bounds; coordinate taps on this keypad are invalid. 0 and 00 are different controls.'
    image_message = len(payload["messages"]) - 1
    payload["messages"][-1]["content"][1]["text"] += '\nThis observed keypad requires Tap(label=...), choosing the intended visible digit yourself. The original requested digit value remains unchanged.'
    elements = []
    # Rebuild only observed UI data, retaining the saved actual bounds.
    for item in json.loads((source / "tree.json").read_text()):
        item["bbox_pixels"] = BoundingBox(**item["bbox_pixels"]) if item["bbox_pixels"] else None
        elements.append(UIElement(**item))
    state = SimpleNamespace(pixels=np.zeros((2400, 1080, 3), dtype=np.uint8), ui_elements=elements)
    endpoint, model, key = api_settings()
    # At most two API requests: the ordinary choice plus one unexecuted correction.
    for attempt in range(2):
        logged = json.loads(json.dumps(payload))
        logged["messages"][image_message]["content"][0]["image_url"]["url"] = "model_input.png (base64 encoded for API)"
        save_json(output / f"request_{attempt}.json", logged)
        payload["messages"][image_message]["content"][0]["image_url"]["url"] = "data:image/png;base64," + base64.b64encode((source / "model_input.png").read_bytes()).decode()
        request = urllib.request.Request(endpoint + "/chat/completions", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        save_json(output / f"response_{attempt}.json", json.loads(json.dumps(data).replace(key, "[REDACTED]")))
        raw = data["choices"][0]["message"]["content"]
        try:
            fields = parse_action(raw)
            action = convert_action(fields, state, ["clock"])
            save_json(output / "result.json", {"native": fields, "android": action, "executed": False})
            print(json.dumps({"native": fields, "evidence": str(output)}), flush=True)
            assert fields.get("label") == "0"
            return
        except ValueError as error:
            save_json(output / f"validation_{attempt}.json", {"error": str(error), "executed": False})
            if attempt:
                raise
            payload["messages"] += [{"role": "assistant", "content": raw}, {"role": "user", "content": f"Invalid action: {error}. Return one corrected action. No action executed."}]


if __name__ == "__main__":
    main()
