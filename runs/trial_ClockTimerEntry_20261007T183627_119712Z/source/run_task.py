"""Run one recorded learning trial with local GELab and the official verifier.

Examples: .\.venv\Scripts\python.exe run_task.py --task ContactsAddContact
          .\.venv\Scripts\python.exe run_task.py --task SystemWifiTurnOn
"""

import argparse
from functools import partial
from datetime import datetime, timezone
import json
import importlib.metadata
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
import time
import urllib.error
import urllib.request

from android_compat import enable_windows_compat
from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent
TASKS = ["SystemWifiTurnOn", "CameraTakePhoto", "ClockTimerEntry",
         "ContactsAddContact", "SystemCopyToClipboard"]


def load_task_env(adb, task_name, config):
    """Use official UIAutomator for Wi-Fi, avoiding a network-dependent tree stream.

    Android World's controller supports both methods, but its launcher omits
    the selector. Temporarily supply that constructor argument while loading;
    restore the class immediately. The returned object is the official class.
    """
    from android_world.env import android_world_controller, env_launcher
    if task_name != "SystemWifiTurnOn" or config.get("wifi_tree_backend") != "uiautomator":
        return env_launcher.load_and_setup_env(adb_path=str(adb), freeze_datetime=False)
    constructor = android_world_controller.AndroidWorldController
    android_world_controller.AndroidWorldController = partial(constructor,
        a11y_method=android_world_controller.A11yMethod.UIAUTOMATOR,
        install_a11y_forwarding_app=False)
    try:
        return env_launcher.load_and_setup_env(adb_path=str(adb), freeze_datetime=False)
    finally:
        android_world_controller.AndroidWorldController = constructor


def record_video(adb, output, stop, ready, errors):
    """Record consecutive emulator clips, because Android screenrecord has a limit."""
    prefix = [str(adb), "-s", "emulator-5554"]
    number = 0
    try:
        if subprocess.check_output(prefix + ["shell", "pidof", "screenrecord"]).strip():
            raise RuntimeError("Another screen recording is already running")
    except subprocess.CalledProcessError:
        pass  # pidof returns a nonzero code when no recording exists.
    except Exception:
        errors.append(traceback.format_exc())
        stop.set()
        ready.set()
        return
    try:
        # Roll over recordings until the trial ends; this is recording, not agent logic.
        while not stop.is_set():
            number += 1
            remote = f"/sdcard/gelab_{output.name}_{number}.mp4"
            with (output / f"video_{number:03d}.stderr.txt").open("wb") as log:
                process = subprocess.Popen(prefix + ["shell", "screenrecord", "--size", "540x1200",
                    "--time-limit", "180", remote], stdout=subprocess.DEVNULL, stderr=log)
                # Wait briefly for the recorder PID before declaring recording ready.
                stop.wait(1)
                pid = subprocess.check_output(prefix + ["shell", "pidof", "screenrecord"]).decode().strip()
                if not pid.isdigit():
                    raise RuntimeError("Could not identify our screen recorder")
                ready.set()
                stop.wait(174)
                ready.clear()  # Pause GUI execution during rollover/pulling.
                subprocess.run(prefix + ["shell", "kill", "-2", pid], check=True, capture_output=True)
                process.wait(timeout=15)
            local = output / f"video_{number:03d}.mp4"
            subprocess.run(prefix + ["pull", remote, str(local)], check=True, capture_output=True)
            if not local.is_file() or local.stat().st_size < 1000:
                raise RuntimeError("Recording file missing or empty")
            # Remove only this already-pulled generated clip from the emulator.
            subprocess.run(prefix + ["shell", "rm", remote], check=True, capture_output=True)
    except Exception:
        errors.append(traceback.format_exc())
        stop.set()
        ready.set()


def main():
    """Initialize one official task, run bounded steps, verify, and preserve evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=TASKS, default="ContactsAddContact")
    parser.add_argument("--observation", choices=["screenshot", "tree", "tree_first"], default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--config", type=Path, default=PROJECT / "agent_config.json")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (PROJECT / ".venv").resolve():
        raise RuntimeError("Use .venv\\Scripts\\python.exe")
    temp_root = PROJECT / ".tools/tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(temp_root)
    enable_windows_compat()
    from android_world import registry
    from android_world.env import env_launcher
    from android_world.env.setup_device import apps, setup
    from gelab_agent import GelabAgent

    output = PROJECT / "runs" / datetime.now(timezone.utc).strftime(f"trial_{args.task}_%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True)
    print(f"Evidence: {output}", flush=True)
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    config = json.loads(args.config.read_text(encoding="utf-8"))
    config.update(observation=args.observation or config["observation"], task_seed=args.seed)
    save_json(output / "config.json", config)
    print(f"Readable trajectory: {output / 'trajectory.txt'}", flush=True)
    log_event(output, "RUN START", {"task": args.task, "config": config})
    summary = {"kind": "learning_trial", "task": args.task, "run_id": output.name,
               "agent_done": False, "verifier": "NOT_RUN", "steps": 0, "manual_intervention": False,
               "evaluation_valid": False, "version": config["version"], "model": config["model"],
               "prompt_version": config["prompt_version"], "observation": config["observation"],
               "grounding": "unique_visible_labels_with_conditional_coordinates" if config.get("label_grounding") and config["observation"] == "tree_first"
                   else "unique_visible_labels" if config.get("label_grounding") and config["observation"] == "tree"
                   else "indices_with_conditional_coordinates" if config["observation"] == "tree_first"
                   else "coordinates" if config["observation"] == "screenshot" else "indices",
               "step_budget": config["max_steps"], "time_budget_seconds": config["max_seconds"]}
    env, task, recorder, agent = None, None, None, None
    stop, ready = threading.Event(), threading.Event()
    video_errors = []
    start = time.monotonic()
    try:
        # Preserve the exact small program and dependency/model identities per run.
        source = output / "source"
        source.mkdir()
        for filename in ("run_task.py", "gelab_agent.py", "probe_connection.py", "android_compat.py", "run.ps1", "trajectory.py"):
            shutil.copyfile(PROJECT / filename, source / filename)
        (source / "instructions").mkdir()
        shutil.copyfile(PROJECT / "instructions/agent.md", source / "instructions/agent.md")
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10) as response:
            tags = json.load(response)
        models = [model for model in tags["models"] if model["name"] == config["model"]]
        if len(models) != 1:
            raise RuntimeError("Configured local model is missing or ambiguous")
        with urllib.request.urlopen("http://localhost:11434/api/version", timeout=10) as response:
            ollama_version = json.load(response)
        save_json(output / "versions.json", {"model": models[0], "ollama": ollama_version,
            "python": sys.version, "android_world": importlib.metadata.version("android-world"),
            "android_env": importlib.metadata.version("android-env")})
        env = load_task_env(adb, args.task, config)
        config["tree_backend"] = "uiautomator" if args.task == "SystemWifiTurnOn" and config.get("wifi_tree_backend") == "uiautomator" else "a11y_forwarder_grpc"
        save_json(output / "config.json", config)
        # Install only infrastructure and the app needed by this learning task.
        task_apps = {
            "ContactsAddContact": (apps.ContactsApp,),
            "SystemWifiTurnOn": (apps.SettingsApp,),
            "CameraTakePhoto": (apps.CameraApp,),
            "ClockTimerEntry": (apps.ClockApp,),
            # Clipper supports the official verifier; Chrome provides a GUI text
            # field for selecting/copying. No direct clipboard write is an action.
            "SystemCopyToClipboard": (apps.ClipperApp, apps.ChromeApp),
        }
        required = (apps.AndroidWorldApp,) + task_apps[args.task]
        from android_world.utils import app_snapshot, file_utils
        # Check each app separately, including clipboard verifier infrastructure.
        for app in required:
            marker = PROJECT / ".tools" / f"setup_app_{app.app_name}.json"
            snapshot_exists = file_utils.check_directory_exists(
                app_snapshot._snapshot_path(app.app_name), env.controller)
            if not snapshot_exists:
                setup.setup_apps(env, app_list=(app,))
            save_json(marker, {"app": app.app_name, "snapshot_exists_or_setup_attempted": True})
        random.seed(args.seed)
        task_class = registry.TaskRegistry().get_registry("android_world")[args.task]
        params = task_class.generate_random_params()
        task = task_class(params)
        config["allowed_apps"] = [app.app_name for app in task_apps[args.task]]
        save_json(output / "config.json", config)
        save_json(output / "task.json", {"name": args.task, "goal": task.goal, "parameters": params,
                  "seed": args.seed, "source_commit": "2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7"})
        log_event(output, "OFFICIAL TASK INPUT", {"goal": task.goal, "parameters": params,
                  "task_seed": args.seed, "model_metadata": "versions.json"})
        # Match the official runner: reset BEFORE task-specific initialization.
        # A reset after initialization was measured to turn Wi-Fi back on.
        env.reset(go_home=True)
        # Official task initialization resets its own apps. Also restore the
        # extra GUI app used for clipboard entry, avoiding cross-run Chrome state.
        for app in task_apps[args.task]:
            if app.app_name not in task.app_names and app.app_name != "clipper":
                app_snapshot.restore_snapshot(app.app_name, env.controller)
        env.reset(go_home=True)
        # Official initialization clears test contacts/sets Wi-Fi state and device time.
        task.initialize_task(env)
        summary["initial_verifier_score"] = task.is_successful(env)
        log_event(output, "INITIAL VERIFIER", {"score": summary["initial_verifier_score"]})
        if summary["initial_verifier_score"] != 0.0:
            raise RuntimeError("Invalid starting state: task already satisfies the verifier")
        summary["evaluation_valid"] = True
        recorder = threading.Thread(target=record_video, args=(adb, output, stop, ready, video_errors))
        recorder.start()
        if not ready.wait(timeout=15) or video_errors:
            raise RuntimeError("Recording failed to start: " + str(video_errors))
        agent = GelabAgent(env, output, config, params)
        agent.recording_ready = ready
        agent.recording_errors = video_errors
        start = time.monotonic()
        # Each iteration is one observe → model → validate → execute → observe step.
        for step in range(config["max_steps"]):
            if time.monotonic() - start >= config["max_seconds"] or video_errors:
                summary["stop_reason"] = "time_budget_or_recording_error"
                break
            summary["steps_attempted"] = step + 1
            result = agent.step(task.goal)
            summary["steps"] = step + 1
            save_json(output / "progress.json", summary)
            if result.done:
                summary["agent_done"] = result.data["action"]["goal_status"] == "complete"
                summary["stop_reason"] = result.data["action"]["goal_status"]
                break
        else:
            summary["stop_reason"] = "step_budget"
        summary["model_calls_attempted"] = agent.calls
    except KeyboardInterrupt:
        summary["stop_reason"] = "user_interrupted"
        log_event(output, "USER INTERRUPTED", {"note": "No automatic action replay; official verification follows."}, summary.get("steps_attempted"))
    except Exception as error:
        summary["error"] = traceback.format_exc()
        summary["error_class"] = "validation_error" if isinstance(error, ValueError) else "api_error" if isinstance(error, urllib.error.URLError) else "environment_or_execution_error"
        summary["stop_reason"] = "error"
        log_event(output, "RUN ERROR", {"error": summary["error"], "class": summary["error_class"]}, summary.get("steps_attempted"))
        print(summary["error"], flush=True)
    finally:
        # Verification is independent of agent completion, including after errors.
        if task is not None and task.initialized and env is not None:
            try:
                score = task.is_successful(env)
                summary["verifier_score"] = score
                summary["verifier"] = "PASS" if score == 1.0 else "FAIL"
                summary["failure_class"] = "false_done" if summary["agent_done"] and score != 1.0 else None
            except Exception:
                summary["verifier"] = "ERROR"
                summary["verifier_error"] = traceback.format_exc()
        stop.set()
        if agent is not None:
            summary["model_calls_attempted"] = agent.calls
            summary["screenshot_fallbacks"] = agent.fallback_events
        if recorder is not None:
            recorder.join(timeout=30)
        summary["video_errors"] = video_errors
        if video_errors or (recorder is not None and recorder.is_alive()):
            summary["evaluation_valid"] = False
            summary["recording_error"] = "Recording failed or did not finish within its join budget"
        summary["verified_agent_success"] = summary["evaluation_valid"] and summary["verifier"] == "PASS"
        summary["videos"] = [path.name for path in sorted(output.glob("video_*.mp4"))]
        summary["duration_seconds"] = time.monotonic() - start
        save_json(output / "summary.json", summary)
        log_event(output, "STOP AND OFFICIAL VERIFICATION", summary)
        print(json.dumps(summary, indent=2), flush=True)
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()
