"""Check before/after one real capture with native history; no GUI actions."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from android_world.env.interface import State
from autoglm_agent import AutoGLMAgent
from probe_connection import save_json


def main():
    """Require a shutter action before capture and finish after the first new thumbnail."""
    source = ROOT / 'runs/trial_CameraTakePhoto_20261007T205626_958365Z'
    output = ROOT / 'runs' / datetime.now(timezone.utc).strftime('autoglm_camera_completion_probe_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    config = json.loads((ROOT / 'agent_config.json').read_text())
    config.update(task_name='CameraTakePhoto', allowed_apps=['camera'])
    save_json(output / 'config.json', config)
    results = []
    # Only actually executed saved decisions are supplied; no predicted result is invented.
    for name, number in [('BEFORE', 3), ('AFTER_ONE', 4)]:
        agent = AutoGLMAgent(None, output, config, {})
        for previous in range(1, number):
            step = source / f'step_{previous:03d}'
            request = json.loads((step / 'observation_0/request_0.json').read_text())
            reply = json.loads((step / 'observation_0/response_0.json').read_text())['choices'][0]['message']['content']
            text = 'Task: Take one photo. Exact task inputs: {}' if previous == 1 else 'Latest observation of the original task after the preceding executed action. No GUI tree available; inspect the screenshot.'
            agent.conversation += [{'role':'user','content':text}, {'role':'assistant','content':reply}]
            agent.history.append(json.loads((step / 'result.json').read_text()))
        state = State(np.array(Image.open(source / f'step_{number:03d}/observation_0/screen.png').convert('RGB')), None, [])
        folder = output / name
        agent.capture(state, folder, number)
        fields, action = agent.ask_action(state, folder, 'Take one photo.', number)
        result = {'state':name,'native':fields,'android':action}
        results.append(result)
        save_json(output / 'results.json', results)
        print(json.dumps(result), flush=True)
        assert (action['action_type'] == 'status') == (name == 'AFTER_ONE')
    print('Evidence:', output)


if __name__ == '__main__':
    main()
