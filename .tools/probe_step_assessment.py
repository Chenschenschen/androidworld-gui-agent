"""Assess two preserved failures with the new method; never dispatch an action."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import AutoGLMAgent, target_at
from android_world.env.representation_utils import BoundingBox, UIElement
from probe_connection import save_json


def saved_state(screen, tree):
    """Reconstruct original pixels and actual recorded controls without a device."""
    elements = json.loads(tree.read_text())
    for element in elements:
        for name in ('bbox', 'bbox_pixels'):
            if element.get(name):
                element[name] = BoundingBox(**element[name])
    return SimpleNamespace(pixels=np.array(Image.open(screen).convert('RGB')),
        ui_elements=[UIElement(**element) for element in elements])


def main():
    """Send only the approved saved before/after evidence, retaining original failures."""
    output = ROOT/'runs'/datetime.now(timezone.utc).strftime('step_assessment_probe_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    config = json.loads((ROOT/'agent_config.json').read_text())
    save_json(output/'config.json', config)
    shutil.copyfile(ROOT/'instructions/assessment.md', output/'assessment_prompt.md')
    cases = (('trial_ClockTimerEntry_20261008T081804_857919Z', 5),
        ('trial_SystemCopyToClipboard_20261008T081108_888681Z', 4))
    # Each case is a different already diagnosed failure, not another task run.
    for run_id, number in cases:
        original = ROOT/'runs'/run_id
        source = original/f'step_{number:03d}'
        task = json.loads((original/'task.json').read_text())
        folder = output/task['name']
        folder.mkdir()
        before = saved_state(source/'freshness_0/screen.png', source/'freshness_0/tree.json')
        after = saved_state(source/'after.png', source/'after_tree.json')
        action = json.loads((source/'action.json').read_text())['android']
        result = json.loads((source/'result.json').read_text())
        selected = target_at(before, action)
        if selected:
            result['selected_gui_control'] = {'label':selected.get('text') or selected.get('content_description'),
                'resource_id':selected.get('resource_id')}
        agent = AutoGLMAgent(None, output, {**config, 'task_name':task['name'],
            'allowed_apps':['clock'] if task['name']=='ClockTimerEntry' else ['chrome']}, task['parameters'])
        agent.pending_reply = json.loads((source/'observation_0/response_0.json').read_text())['choices'][0]['message']['content']
        save_json(folder/'source.json', {'run_id':run_id, 'step':number, 'executed':False, 'actual_result':result})
        summary = agent.assess_step(before, after, folder, task['goal'], action, result, number)
        print(json.dumps({'task':task['name'], 'summary':summary, 'evidence':str(folder), 'executed':False}), flush=True)


if __name__ == '__main__':
    main()
