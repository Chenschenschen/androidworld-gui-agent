"""Inspect a real editor control without performing or evaluating a clipboard task."""

from dataclasses import asdict
from pathlib import Path
import json
import os
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from android_compat import enable_fresh_xml, enable_windows_compat
from run_task import load_task_env
from probe_connection import save_json
from PIL import Image
from android_world.env import adb_utils, android_world_controller, tools


def main():
    """Open the observed QuickNote tab and save actual editor properties as diagnostics."""
    output = PROJECT / '.tools/markor_editor_diagnostic'
    output.mkdir(exist_ok=False)
    enable_windows_compat()
    enable_fresh_xml()
    adb = Path(os.environ['LOCALAPPDATA']) / 'Android/Sdk/platform-tools/adb.exe'
    env = load_task_env(adb,'SystemCopyToClipboard',{'tree_backend':'none'})
    try:
        env.controller._a11y_method = android_world_controller.A11yMethod.UIAUTOMATOR
        adb_utils.launch_app('markor',env.controller)
        time.sleep(1)
        before = env.get_state(wait_to_stabilize=False)
        Image.fromarray(before.pixels).save(output/'before.png')
        save_json(output/'before_tree.json',[asdict(e) for e in before.ui_elements])
        tools.AndroidToolController(env=env.controller).click_element('QuickNote')
        time.sleep(1)
        after = env.get_state(wait_to_stabilize=False)
        Image.fromarray(after.pixels).save(output/'after.png')
        save_json(output/'after_tree.json',[asdict(e) for e in after.ui_elements])
        fields = [asdict(e) for e in after.ui_elements if e.class_name == 'android.widget.EditText']
        save_json(output/'diagnostic.json',{'kind':'app_capability_diagnostic','benchmark':False,
            'actions':['Launch markor','Tap actual QuickNote label'],'typed_or_copied':False,'editable_controls':fields})
        print(json.dumps({'output':str(output),'edit_text_controls':len(fields)}))
    finally:
        env.close()


if __name__ == '__main__':
    main()
