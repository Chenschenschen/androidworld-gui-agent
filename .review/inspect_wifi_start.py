"""Diagnose official Wi-Fi initialization/reset; never run a benchmark agent."""

import os
from pathlib import Path
import sys
import tempfile
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from android_compat import enable_windows_compat
from probe_connection import save_json


def main():
    """Record Wi-Fi verifier scores before and after official environment reset."""
    tempfile.tempdir = str(PROJECT / ".tools/tmp")
    enable_windows_compat()
    from android_world import registry
    from android_world.env import adb_utils, env_launcher
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    env = env_launcher.load_and_setup_env(adb_path=str(adb), freeze_datetime=False)
    evidence = []
    try:
        env.reset(go_home=True)
        task = registry.TaskRegistry().get_registry("android_world")["SystemWifiTurnOn"]({"on_or_off": "on"})
        task.initialize_task(env)
        # Sample the official verifier while asynchronous service changes settle.
        for delay in (0, 1, 2):
            time.sleep(delay)
            score = task.is_successful(env)
            evidence.append({"stage": "after_initialize", "delay_seconds": delay, "score": score})
        env.reset(go_home=True)
        evidence.append({"stage": "after_reset", "score": task.is_successful(env)})
        result = adb_utils.issue_generic_request(["shell", "settings", "get", "global", "wifi_on"], env.controller)
        evidence.append({"wifi_on": result.generic.output.decode().strip()})
        save_json(PROJECT / ".review/wifi_start_diagnostic.json", evidence)
        print(evidence)
    finally:
        env.close()


if __name__ == "__main__":
    main()
