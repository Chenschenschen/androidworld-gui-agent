"""Check Android World connectivity without running a benchmark task.

Run from PowerShell: .\.venv\Scripts\python.exe check_setup.py
The environment may install its accessibility helper on the test emulator.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import traceback
import tempfile

from android_compat import enable_windows_compat


PROJECT = Path(__file__).resolve().parent
TASK_NAMES = [
    "SystemWifiTurnOn",
    "MarkorCreateNote",
    "MarkorCreateNoteAndSms",
    "SimpleCalendarAddOneEvent",
    "MarkorMergeNotes",
    "OsmAndTrack",
]


def main():
    """Load the registry, connect to the emulator, and save one observation."""
    # Checking the interpreter prevents accidental use of global Python packages.
    if Path(sys.prefix).resolve() != (PROJECT / ".venv").resolve():
        raise RuntimeError("Run this script with .venv\\Scripts\\python.exe")

    # Keep Android World's temporary files inside the project as well.
    temp_root = PROJECT / ".tools" / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(temp_root)
    enable_windows_compat()

    from android_world import registry
    from android_world.env import env_launcher
    from PIL import Image

    # Each check gets a new folder so earlier evidence remains available.
    run_id = datetime.now(timezone.utc).strftime("setup_%Y%m%dT%H%M%S_%fZ")
    output = PROJECT / "runs" / run_id
    output.mkdir(parents=True, exist_ok=False)
    adb_path = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    report = {"kind": "setup_check", "run_id": run_id,
              "python": sys.version, "python_executable": sys.executable,
              "adb_path": str(adb_path), "benchmark_run": False}
    env = None

    try:
        if not adb_path.is_file():
            raise FileNotFoundError(f"ADB not found: {adb_path}")
        tasks = registry.TaskRegistry().get_registry("android_world")
        report["registered_task_count"] = len(tasks)
        report["selected_tasks"] = {}
        # Check every agreed task name against the official task registry.
        for name in TASK_NAMES:
            report["selected_tasks"][name] = name in tasks
            if name not in tasks:
                raise RuntimeError(f"Task missing from registry: {name}")

        # Read the existing emulator; full app setup and date freezing come later.
        env = env_launcher.load_and_setup_env(
            adb_path=str(adb_path), console_port=5554, grpc_port=8554,
            emulator_setup=False, freeze_datetime=False,
        )
        state = env.get_state(wait_to_stabilize=True)
        Image.fromarray(state.pixels).save(output / "screen.png")
        report["screen_shape"] = list(state.pixels.shape)
        report["ui_element_count"] = len(state.ui_elements)
        report["screenshot"] = "screen.png"
        report["connection_ok"] = True
        report["verifier_executed"] = False
    except Exception:
        report["connection_ok"] = False
        report["error"] = traceback.format_exc()
        raise
    finally:
        # Save even a failed check so infrastructure errors remain inspectable.
        (output / "report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(f"Setup evidence: {output}")
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()
