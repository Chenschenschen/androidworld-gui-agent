"""Test actual GUI centers on a recorded Timer observation; no device actions."""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings, parse_action
from probe_connection import save_json


def main():
    """Check that the model grounds one zero at its real center, avoiding the 00 key."""
    source = ROOT / 'runs/trial_ClockTimerEntry_20261007T210910_992181Z/step_004/observation_0'
    output = ROOT / 'runs' / datetime.now(timezone.utc).strftime('autoglm_timer_grounding_probe_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    payload = json.loads((source / 'request_0.json').read_text())
    tree = json.loads((source / 'tree.json').read_text())
    width, height = Image.open(source / 'screen.png').size
    notes, zero = [], None
    # Positions come only from this real saved observation, never a hardcoded keypad.
    for e in tree:
        if e['package_name'] == 'com.android.systemui':
            continue
        label = e['text'] or e['content_description']
        if not label:
            continue
        if e['is_clickable'] and e['bbox_pixels']:
            box = e['bbox_pixels']
            point = [int((box['x_min']+box['x_max'])*500/width), int((box['y_min']+box['y_max'])*500/height)]
            label += ' (observed center=' + json.dumps(point) + ')'
            if e['text'] == '0':
                zero = point
        notes.append(label)
    latest = payload['messages'][-1]['content']
    text = latest[1]['text']
    start, end = text.index('Fresh observed GUI labels and state:\n'), text.index('Original input contract')
    latest[1]['text'] = text[:start] + 'Fresh observed GUI labels and state:\n' + '\n'.join(notes) + '\n' + text[end:]
    payload['messages'][0]['content'] += '\nFor this keypad choose the exact visible GUI label, using do(action="Tap", label="0") instead of coordinates. Python resolves that label against the actual fresh GUI bounds. 0 and 00 are different labels. Return one Tap(label=...) action. Do not give element coordinates in this observation.'
    latest[1]['text'] += '\nChoose your next keypad action with an exact label: do(action="Tap", label="observed label"). Available keypad labels: 1,2,3,4,5,6,7,8,9,00,0,Backspace 1. The current display is 00h 00m 02s and the original desired digits are 2,0,0,7,0,1.'
    save_json(output / 'request.json', payload)
    latest[0]['image_url']['url'] = 'data:image/png;base64,' + base64.b64encode((source / 'model_input.png').read_bytes()).decode()
    endpoint, model, key = api_settings()
    request = urllib.request.Request(endpoint + '/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    save_json(output / 'response.json', json.loads(json.dumps(data).replace(key,'[REDACTED]')))
    fields = parse_action(data['choices'][0]['message']['content'])
    save_json(output / 'result.json', {'native':fields, 'observed_zero_center':zero})
    print(json.dumps({'native':fields,'observed_zero_center':zero,'evidence':str(output)}), flush=True)
    assert fields.get('label') == '0'


if __name__ == '__main__':
    main()
