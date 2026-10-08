"""Test readable observed digit counts on actual Timer failure screens."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings, parse_action
from probe_connection import save_json


def main():
    """Check partial-entry and full-entry decisions without prescribing a next key."""
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_timer_buffer_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    endpoint, model, key = api_settings()
    # Use two genuine observations: five correct digits, then six incorrect digits.
    for step, expected in ((8, [245, 455]), (9, [755, 685])):
        source = ROOT / f"runs/trial_ClockTimerEntry_20261008T060634_132162Z/step_{step:03d}/observation_0"
        payload = json.loads((source / "request_0.json").read_text())
        tree = json.loads((source / "tree.json").read_text())
        display = next(e["text"] for e in tree if e["resource_id"] == "com.google.android.deskclock:id/timer_setup_time")
        groups = re.fullmatch(r"(\d{2})h (\d{2})m (\d{2})s", display).groups()
        buffer = "".join(groups).lstrip("0")
        note = f"Observed keypad buffer from the GUI display (padding removed): {buffer!r}; observed non-padding digit count: {len(buffer)}."
        target = "Requested input positions: " + "; ".join(f"position {i} = {digit}" for i, digit in enumerate("133334", 1)) + "."
        guide = "Read the observed digit count and the numbered target positions. Choose the next key yourself. Six digits fills this keypad: if the full entry differs from the target, use the delete key before replacing a digit; another digit tap cannot change a full entry."
        payload["messages"][0]["content"] += "\n" + target + "\n" + guide
        payload["messages"][-1]["content"][1]["text"] += "\n" + note + "\n" + target + "\n" + guide
        save_json(output / f"request_{step}.json", payload)
        payload["messages"][-1]["content"][0]["image_url"]["url"] = "data:image/png;base64," + base64.b64encode((source / "model_input.png").read_bytes()).decode()
        request = urllib.request.Request(endpoint + "/chat/completions", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        save_json(output / f"response_{step}.json", json.loads(json.dumps(data).replace(key, "[REDACTED]")))
        fields = parse_action(data["choices"][0]["message"]["content"])
        save_json(output / f"result_{step}.json", {"native": fields, "buffer": buffer, "executed": False})
        print(json.dumps({"step": step, "native": fields, "evidence": str(output)}), flush=True)
        assert fields.get("action") == "Tap" and all(abs(a-b) <= 5 for a,b in zip(fields.get("element", []), expected)) and len(fields.get("element", [])) == 2


if __name__ == "__main__":
    main()
