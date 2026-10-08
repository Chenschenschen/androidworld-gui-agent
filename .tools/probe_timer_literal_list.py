"""Check retaining literal digits alongside numbered positions on a saved failure."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings, parse_action
from probe_connection import save_json


def main():
    """Require the single zero on the actual observed buffer '20'; no GUI actions."""
    source = ROOT / "runs/trial_ClockTimerEntry_20261008T064806_804154Z/step_005/observation_0"
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_timer_literal_list_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    payload = json.loads((source / "request_0.json").read_text())
    if "--literal-goal" in sys.argv:
        original = "Create a timer with 20 hours, 7 minutes, and 1 seconds. Do not start the timer."
        literal = "In Clock Timer, enter the literal keypad text 200701, keeping all six characters including zeros. Do not start it. The final display must be 20h 07m 01s."
        original_inputs = json.dumps({"hours":20,"minutes":7,"seconds":1})
        literal_inputs = json.dumps({"keypad_input_text":"200701","target_display":"20h 07m 01s","leave_unstarted":True})
        for message in payload["messages"]:
            if isinstance(message["content"], str):
                message["content"] = message["content"].replace(original, literal).replace(original_inputs, literal_inputs)
            else:
                for block in message["content"]:
                    if block["type"] == "text":
                        block["text"] = block["text"].replace(original, literal).replace(original_inputs, literal_inputs)
    addition = " Requested literal keypad digits in order: ['2', '0', '0', '7', '0', '1']."
    guide = "Treat the keypad value as literal text, never a number or separate time fields. Before choosing a key, write a short TODO containing the remaining literal suffix after the observed buffer. Example: target digits 120405, observed buffer 12 => remaining literal suffix 0405, so the next GUI key is 0, not 4. Example: target digits 122223, observed buffer 12222 => remaining suffix 3. Keep every zero and repeated digit. Choose the first character of your own remaining suffix; use the observed GUI center for that key."
    for message in payload["messages"]:
        if isinstance(message["content"], str):
            message["content"] = message["content"].replace("Requested input positions:", addition + " Requested input positions:")
        else:
            for block in message["content"]:
                if block["type"] == "text":
                    block["text"] = block["text"].replace("Requested input positions:", addition + " Requested input positions:")
    if "--literal-goal" not in sys.argv:
        payload["messages"][0]["content"] += "\n" + guide
        payload["messages"][-1]["content"][1]["text"] += "\n" + guide
    save_json(output / "request.json", payload)
    payload["messages"][-1]["content"][0]["image_url"]["url"] = "data:image/png;base64," + base64.b64encode((source / "model_input.png").read_bytes()).decode()
    endpoint, model, key = api_settings()
    request = urllib.request.Request(endpoint + "/chat/completions", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    save_json(output / "response.json", json.loads(json.dumps(data).replace(key, "[REDACTED]")))
    fields = parse_action(data["choices"][0]["message"]["content"])
    save_json(output / "result.json", {"native": fields, "source": str(source), "executed": False})
    print(json.dumps({"native": fields, "evidence": str(output)}), flush=True)
    point = fields.get("element", [])
    assert fields.get("action") == "Tap" and len(point) == 2 and abs(point[0]-500) <= 5 and abs(point[1]-685) <= 5


if __name__ == "__main__":
    main()
