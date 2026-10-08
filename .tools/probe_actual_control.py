"""Check actual GUI control feedback on a saved false-finish screen; no actions."""
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
    """Return the saved real Clear input label and ask for one unexecuted choice."""
    run = ROOT / 'runs/trial_SystemCopyToClipboard_20261008T081108_888681Z'
    source = run / 'step_005/observation_0'
    output = ROOT / 'runs' / datetime.now(timezone.utc).strftime('actual_control_feedback_probe_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    payload = json.loads((source/'request_0.json').read_text())
    tree = json.loads((run/'step_004/freshness_0/tree.json').read_text())
    control = next(e for e in tree if e['content_description'] == 'Clear input')
    addition = {'label':control['content_description'], 'resource_id':control['resource_id']}
    payload['messages'][-1]['content'][1]['text'] += '\nActual fresh GUI control selected by the previous Tap: '+json.dumps(addition)
    save_json(output/'request.json', payload)
    payload['messages'][-1]['content'][0]['image_url']['url'] = 'data:image/png;base64,'+base64.b64encode((source/'model_input.png').read_bytes()).decode()
    endpoint, model, key = api_settings()
    request = urllib.request.Request(endpoint+'/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    save_json(output/'response.json', json.loads(json.dumps(data).replace(key,'[REDACTED]')))
    fields = parse_action(data['choices'][0]['message']['content'])
    result = {'native':fields,'executed':False,'source':str(source),'rejects_previous_false_finish':fields['command']!='finish'}
    save_json(output/'result.json', result)
    print(json.dumps({'evidence':str(output), **result}), flush=True)


if __name__ == '__main__':
    main()
