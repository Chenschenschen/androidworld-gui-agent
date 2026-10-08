"""Exercise the real agent request on two saved UI states without GUI dispatch."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from android_world.env.interface import State
from autoglm_agent import AutoGLMAgent, xml_controls
from probe_connection import save_json


def main():
    """Require a model finish on genuine ON and a GUI action on genuine OFF."""
    source = ROOT / 'runs/trial_SystemWifiTurnOn_20261007T203059_038144Z'
    output = ROOT / 'runs' / datetime.now(timezone.utc).strftime('autoglm_current_completion_probe_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    config = json.loads((ROOT / 'agent_config.json').read_text())
    config.update(task_name='SystemWifiTurnOn', allowed_apps=['settings'])
    save_json(output / 'config.json', config)
    results = []
    # The assertions distinguish correct completion from falsely finishing on OFF.
    for name, step, capture in [('ON', 5, 13), ('OFF', 6, 16)]:
        agent = AutoGLMAgent(None, output, config, {'on_or_off':'on'})
        elements = xml_controls((source / f'ui_capture_{capture:03d}.xml').read_text())
        assert next(e.is_checked for e in elements if e.is_checkable) == (name == 'ON')
        state = State(np.array(Image.open(source / f'step_{step:03d}/observation_0/screen.png').convert('RGB')), None, elements)
        folder = output / name
        agent.capture(state, folder, 1)
        fields, action = agent.ask_action(state, folder, 'Turn wifi on.', 1)
        result = {'state':name,'native':fields,'android':action}
        results.append(result)
        save_json(output / 'results.json', results)
        print(json.dumps(result), flush=True)
        assert (action['action_type'] == 'status') == (name == 'ON')
    print('Evidence:', output)


if __name__ == '__main__':
    main()
