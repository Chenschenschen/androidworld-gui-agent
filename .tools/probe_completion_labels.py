"""Probe recorded ON/OFF screens without dispatching any Android action."""
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
    """Compare compact observed labels and a native conversation on real saved states."""
    endpoint, model, key = api_settings()
    output = ROOT / "runs" / datetime.now(timezone.utc).strftime("autoglm_label_probe_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    source = ROOT / "runs/trial_SystemWifiTurnOn_20261007T203059_038144Z"
    upstream = ROOT / "runs/autoglm_native_context_probe_20261007T202643_127912Z/request_ON.json"
    native = json.loads(upstream.read_text())["messages"][0]["content"] if upstream.exists() else (ROOT / "instructions/autoglm.md").read_text()
    results = []
    # Both states are real captured XML/image pairs; these calls cannot operate the device.
    for mode in ("compact", "native"):
        for name, step in (("ON", 5), ("OFF", 6)):
            folder = source / f"step_{step:03d}/observation_0"
            tree = json.loads((folder / "tree.json").read_text())
            checked = next(e["is_checked"] for e in tree if e["is_checkable"])
            assert checked == (name == "ON")
            text = 'Task: Turn wifi on. Stop as soon as the Wi-Fi switch is ON. Internet connectivity is not required.\n'
            text += '** Screen Info ** {"current_app":"Settings"}\nObserved GUI row: Wi-Fi; switch is ' + ('ON (checked=true).' if checked else 'OFF (checked=false).')
            text += '\nRead this observed switch state. If ON, finish. If OFF, enable it. Return exactly one do(...) or finish(...) action.'
            system = native if mode == "native" else (ROOT / "instructions/autoglm.md").read_text()
            messages = [{"role":"system", "content":system}, {"role":"user", "content":[
                {"type":"image_url", "image_url":{"url":"data:image/png;base64," + base64.b64encode((folder / "model_input.png").read_bytes()).decode()}},
                {"type":"text", "text":text}]}]
            payload = {"model":model,"messages":messages,"stream":False,"temperature":0,"top_p":.85,"frequency_penalty":.2,"max_tokens":1024}
            logged = json.loads(json.dumps(payload))
            logged["messages"][-1]["content"][0]["image_url"]["url"] = str(folder / "model_input.png")
            save_json(output / f"request_{mode}_{name}.json", logged)
            request = urllib.request.Request(endpoint + '/chat/completions', data=json.dumps(payload).encode(), headers={"Content-Type":"application/json","Authorization":"Bearer " + key})
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.load(response)
            save_json(output / f"response_{mode}_{name}.json", json.loads(json.dumps(data).replace(key, '[REDACTED]')))
            raw = data["choices"][0]["message"]["content"]
            result = {"mode":mode,"state":name,"action":parse_action(raw),"raw":raw}
            results.append(result)
            print(json.dumps(result), flush=True)
    save_json(output / 'results.json', results)
    print('Evidence:', output)


if __name__ == '__main__':
    main()
