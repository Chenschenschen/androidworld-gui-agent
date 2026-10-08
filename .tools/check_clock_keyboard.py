"""Logged GUI transport diagnostic; never counted as an agent evaluation."""
from datetime import datetime, timezone
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_task import load_task_env
from android_compat import enable_windows_compat, enable_fresh_xml
from autoglm_agent import xml_controls
from probe_connection import save_json
from android_world.env import adb_utils, json_action
from PIL import Image


def main():
    """Check normal digit key events on this installed Clock, with saved GUI proof."""
    tempfile.tempdir = str(ROOT / '.tools/tmp')
    enable_windows_compat()
    enable_fresh_xml()
    out = ROOT / 'runs' / datetime.now(timezone.utc).strftime('clock_keyboard_diagnostic_%Y%m%dT%H%M%S_%fZ')
    out.mkdir()
    env = load_task_env(Path('C:/Users/koc/AppData/Local/Android/Sdk/platform-tools/adb.exe'), 'ClockTimerEntry', {'tree_backend':'none'})
    try:
        adb_utils.launch_app('clock', env.controller)
        time.sleep(1)
        elements = xml_controls(adb_utils.uiautomator_dump(env.controller, timeout_sec=8))
        timer = next(e for e in elements if e.is_visible and e.content_description == 'Timer')
        box = timer.bbox_pixels
        env.execute_action(json_action.JSONAction(action_type='click', x=(box.x_min+box.x_max)//2, y=(box.y_min+box.y_max)//2))
        time.sleep(.5)
        elements = xml_controls(adb_utils.uiautomator_dump(env.controller, timeout_sec=8))
        # This diagnostic clears at most six GUI digits; no task or verifier is involved.
        for _ in range(6):
            display = next(e.text for e in elements if e.resource_id.endswith(':id/timer_setup_time'))
            if display == '00h 00m 00s':
                break
            adb_utils.check_ok(adb_utils.press_keyboard_generic('67', env.controller), 'GUI Delete failed')
            elements = xml_controls(adb_utils.uiautomator_dump(env.controller, timeout_sec=8))
        display = next(e.text for e in elements if e.resource_id.endswith(':id/timer_setup_time'))
        assert display == '00h 00m 00s', display
        Image.fromarray(env.get_state(wait_to_stabilize=False).pixels).save(out/'before.png')
        save_json(out/'before_tree.json', [asdict(e) for e in elements])
        adb_utils.type_text('120405', env.controller, timeout_sec=10)
        time.sleep(.5)
        elements = xml_controls(adb_utils.uiautomator_dump(env.controller, timeout_sec=8))
        Image.fromarray(env.get_state(wait_to_stabilize=False).pixels).save(out/'after.png')
        save_json(out/'after_tree.json', [asdict(e) for e in elements])
        display = next(e.text for e in elements if e.resource_id.endswith(':id/timer_setup_time'))
        result = {'diagnostic_only':True, 'manual_intervention':True, 'gui_input_text':'120405', 'display':display, 'supported':display=='12h 04m 05s', 'benchmark_success_claim':False}
        save_json(out/'result.json', result)
        print(json.dumps({'evidence':str(out), **result}), flush=True)
    finally:
        env.close()


if __name__ == '__main__':
    main()
