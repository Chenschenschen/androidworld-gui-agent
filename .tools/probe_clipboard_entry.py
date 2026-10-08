"""Check a revised clipboard instruction on a saved real screen; no GUI actions."""
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

RULE = "The task input is the text TO COPY, not evidence that it is already on the clipboard. Chrome's 'Text you copied' suggestion and Gboard's RESET chip do not contain the target. First focus Chrome's editable address field and Type the entire exact task text WITHOUT Enter. Then Long Press the entered text, Select all if needed, and tap the visible Copy command. Finish only after copying the entire exact target. Do not submit a search or open another app. If the focused field is empty, Type is the next operation needed; repeated taps cannot supply missing text."


def main():
    """Require exact text entry from the actual empty focused Chrome observation."""
    source = ROOT / "runs/trial_SystemCopyToClipboard_20261008T055228_288420Z/step_003/observation_0"
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_clipboard_entry_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    payload = json.loads((source / "request_0.json").read_text())
    payload["messages"][0]["content"] += "\nClipboard clarification: " + RULE
    payload["messages"][-1]["content"][1]["text"] += "\nOriginal clipboard input contract: " + RULE
    save_json(output / "request.json", payload)
    payload["messages"][-1]["content"][0]["image_url"]["url"] = "data:image/png;base64," + base64.b64encode((source / "model_input.png").read_bytes()).decode()
    endpoint, model, key = api_settings()
    request = urllib.request.Request(endpoint + "/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    save_json(output / "response.json", json.loads(json.dumps(data).replace(key, "[REDACTED]")))
    fields = parse_action(data["choices"][0]["message"]["content"])
    save_json(output / "result.json", {"native": fields, "source": str(source), "executed": False})
    print(json.dumps({"native": fields, "evidence": str(output)}), flush=True)
    assert fields == {"command": "do", "action": "Type", "text": "Discount code: SAVE20"}


if __name__ == "__main__":
    main()
