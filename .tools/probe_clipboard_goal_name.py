"""Check whether naming a requested value avoids treating it as current state."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings, parse_action, COMPLETION_RULES
from probe_connection import save_json


def main():
    """Change only the model-facing target name on a recorded Home request."""
    after_copy = "--after-copy" in sys.argv
    relative = "trial_SystemCopyToClipboard_20261008T055645_761067Z/step_006" if after_copy else "trial_SystemCopyToClipboard_20261008T055933_026910Z/step_001"
    source = ROOT / "runs" / relative / "observation_0"
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_clipboard_goal_name_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    payload = json.loads((source / "request_0.json").read_text())
    payload["messages"][0]["content"] = payload["messages"][0]["content"].replace('"clipboard_content":', '"text_to_copy":')
    payload["messages"][-1]["content"][1]["text"] = payload["messages"][-1]["content"][1]["text"].replace('"clipboard_content":', '"text_to_copy":')
    if after_copy:
        system = payload["messages"][0]["content"]
        old_rule = system.split("COMPLETION CONDITION for SystemCopyToClipboard:\n")[1].split("\nOriginal task:")[0]
        rule = COMPLETION_RULES["SystemCopyToClipboard"]
        # Replace stale contract copies in this counterfactual probe consistently.
        # The original request and raw executed trajectory remain unchanged on disk.
        for message in payload["messages"]:
            if isinstance(message["content"], str):
                message["content"] = message["content"].replace(old_rule, rule).replace('"clipboard_content":', '"text_to_copy":')
            else:
                for block in message["content"]:
                    if block["type"] == "text":
                        block["text"] = block["text"].replace(old_rule, rule).replace('"clipboard_content":', '"text_to_copy":')
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
    assert fields.get("command") == "finish" if after_copy else fields == {"command": "do", "action": "Launch", "app": "Chrome"}


if __name__ == "__main__":
    main()
