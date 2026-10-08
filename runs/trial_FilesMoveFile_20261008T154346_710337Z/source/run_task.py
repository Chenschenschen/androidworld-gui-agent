"""Run one recorded learning trial with AutoGLM API and the official verifier.

Examples: .\.venv\Scripts\python.exe run_task.py --task ContactsAddContact
          .\.venv\Scripts\python.exe run_task.py --task SystemWifiTurnOn
"""

import argparse
from dataclasses import asdict
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
from PIL import Image

from android_compat import enable_windows_compat, enable_fresh_xml, enable_single_attempt_adb
from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent
TASKS = ["SystemWifiTurnOn", "CameraTakePhoto", "ClockTimerEntry",
         "ContactsAddContact", "SystemCopyToClipboard", "SimpleSmsSend", "FilesMoveFile"]
# Keep external/manual emulator interaction visible in evaluation review notes.


def load_task_env(adb, task_name, config):
    """Select the official screenshot-only or UIAutomator observation backend.

    Android World's controller supports both methods, but its launcher omits
    the selector. Temporarily supply that constructor argument while loading;
    restore the class immediately. The returned object is the official class.
    """
    from android_world.env import android_world_controller, env_launcher
    backend = config.get("tree_backend")
    if backend not in {"none", "uiautomator"}:
        return env_launcher.load_and_setup_env(adb_path=str(adb), freeze_datetime=False)
    constructor = android_world_controller.AndroidWorldController
    android_world_controller.AndroidWorldController = partial(constructor,
        a11y_method=android_world_controller.A11yMethod(backend),
        install_a11y_forwarding_app=False)
    try:
        return env_launcher.load_and_setup_env(adb_path=str(adb), freeze_datetime=False)
    finally:
        android_world_controller.AndroidWorldController = constructor


def prepare_observations(adb, output, config):
    """Disable only the crashing test forwarder service before screenshot capture."""
    prefix = [str(adb), "-s", "emulator-5554", "shell"]
    before = subprocess.check_output(prefix + ["settings", "get", "secure", "enabled_accessibility_services"], timeout=10).decode().strip()
    services = [] if before == "null" else before.split(":")
    retained = [service for service in services if not service.startswith("com.google.androidenv.accessibilityforwarder/")]
    if retained != services:
        if retained:
            subprocess.run(prefix + ["settings", "put", "secure", "enabled_accessibility_services", ":".join(retained)], check=True, timeout=10)
        else:
            subprocess.run(prefix + ["settings", "delete", "secure", "enabled_accessibility_services"], check=True, timeout=10)
        subprocess.run(prefix + ["am", "force-stop", "com.google.androidenv.accessibilityforwarder"], check=True, timeout=10)
    after = subprocess.check_output(prefix + ["settings", "get", "secure", "enabled_accessibility_services"], timeout=10).decode().strip()
    record = {"backend": config["tree_backend"], "accessibility_services_before": before, "accessibility_services_after": after,
              "tree_used_for_model": False, "task_state_modified": False}
    save_json(output / "observation_setup.json", record)
    log_event(output, "OBSERVATION INFRASTRUCTURE", record)
    if config["tree_backend"] == "uiautomator" or config.get("supplemental_tree_packages"):
        enable_fresh_xml()


def verify_task(task, env, output):
    """Give the unmodified Clock verifier its required official GUI observation."""
    from android_world.env import adb_utils, android_world_controller
    original = env.controller._a11y_method
    try:
        if type(task).__name__ == "ClockTimerEntry":
            activity, response = adb_utils.get_current_activity(env.controller)
            adb_utils.check_ok(response, "Verifier activity unavailable")
            # Clock checks the displayed duration; screenshot-only state lacks it.
            # Home has an animated widget, so request XML only inside DeskClock.
            if activity and "DeskClock" in activity:
                enable_fresh_xml()
                env.controller._a11y_method = android_world_controller.A11yMethod.UIAUTOMATOR
            log_event(output, "VERIFIER OBSERVATION", {"activity": activity,
                "backend": env.controller._a11y_method.value, "model_receives_verifier": False})
        return task.is_successful(env)
    finally:
        env.controller._a11y_method = original


def setup_required_app(app, env, output):
    """Run official app setup with GUI labels, saving only a successful snapshot."""
    from android_world.env import adb_utils, android_world_controller
    from android_world.env.setup_device import setup
    from android_world.utils import app_snapshot
    original = env.controller._a11y_method
    try:
        enable_fresh_xml()
        env.controller._a11y_method = android_world_controller.A11yMethod.UIAUTOMATOR
        adb_utils.press_home_button(env.controller)
        adb_utils.set_root_if_needed(env.controller)
        setup.maybe_install_app(app, env)
        try:
            app.setup(env)
        except ValueError as error:
            # The emulator uses a curly apostrophe while upstream expects ASCII.
            # Handle only this observed notification dialog, then prove readiness.
            if app.app_name != "contacts" or str(error) != 'Target text "Don\'t allow" not found.':
                raise
            adb_utils.launch_app(app.app_name, env.controller)
            time.sleep(1)
            state = env.get_state(wait_to_stabilize=False)
            save_json(output / "contacts_setup_tree.json", [asdict(e) for e in state.ui_elements])
            Image.fromarray(state.pixels).save(output / "contacts_setup.png")
            notifications = any(e.text == "Allow Contacts to send you notifications?" for e in state.ui_elements)
            deny = [e for e in state.ui_elements if e.is_visible and e.is_clickable and e.bbox_pixels
                and e.package_name == "com.google.android.permissioncontroller" and e.text.replace("’", "'") == "Don't allow"]
            if notifications and len(deny) == 1:
                from android_world.env import json_action
                box = deny[0].bbox_pixels
                env.execute_action(json_action.JSONAction(action_type="click",
                    x=int((box.x_min + box.x_max) / 2), y=int((box.y_min + box.y_max) / 2)))
                time.sleep(1)
                state = env.get_state(wait_to_stabilize=False)
                save_json(output / "contacts_setup_after_tree.json", [asdict(e) for e in state.ui_elements])
                Image.fromarray(state.pixels).save(output / "contacts_setup_after.png")
                log_event(output, "SETUP LABEL COMPATIBILITY", {"app": "contacts", "observed_label": deny[0].text})
            ready = any(e.is_visible and e.is_clickable and e.package_name == "com.google.android.contacts"
                and (e.text == "Create contact" or e.content_description == "Create contact") for e in state.ui_elements)
            adb_utils.close_app(app.app_name, env.controller)
            if not ready:
                raise RuntimeError("Contacts main screen unavailable after optional dialog") from error
            log_event(output, "CONTACTS SETUP READY", {"app": "contacts", "ready_control": "Create contact"})
        # Official setup_apps catches failed GUI setup and still saves a snapshot.
        # Let that error propagate here so incomplete onboarding is not cached.
        app_snapshot.save_snapshot(app.app_name, env.controller)
        log_event(output, "OFFICIAL APP SETUP", {"app": app.app_name, "complete": True, "backend": "uiautomator"})
    finally:
        env.controller._a11y_method = original


def ensure_required_app(app, env, output):
    """Require an installed package and successful snapshot before task initialization."""
    from android_world.env.setup_device import setup
    from android_world.utils import app_snapshot, file_utils
    installed = setup.is_package_installed(app.package_name(), env)
    snapshot = file_utils.check_directory_exists(app_snapshot._snapshot_path(app.app_name), env.controller)
    log_event(output, "APP PREREQUISITES", {"app": app.app_name, "installed": installed, "snapshot": snapshot})
    # Data snapshots can survive an APK removal; neither check alone proves readiness.
    if not installed or not snapshot:
        setup_required_app(app, env, output)
        if not setup.is_package_installed(app.package_name(), env) or not file_utils.check_directory_exists(
                app_snapshot._snapshot_path(app.app_name), env.controller):
            raise RuntimeError(f"Official preparation did not establish {app.app_name} readiness")
    save_json(PROJECT / ".tools" / f"setup_app_{app.app_name}.json",
              {"app": app.app_name, "package_installed": True, "snapshot_exists": True})


def reset_clipboard_editor(env, output):
    """Reset only our synthetic external note using the official file-reset utility."""
    from android_world.env import adb_utils
    from android_world.utils import file_utils
    base = "/storage/emulated/0/Documents/markor"
    name = "QuickNote.md"  # Verified backing file of this installed test app, not a task input.
    adb_utils.close_app("markor", env.controller)
    file_utils.remove_single_file(name, base, env.controller)
    if file_utils.check_file_exists(base + "/" + name, env.controller):
        raise RuntimeError("Synthetic QuickNote reset did not remove the old note")
    log_event(output, "EDITOR RESET", {"kind":"environment_preparation", "app":"markor",
        "method":"official remove_single_file", "target":base + "/" + name,
        "task_value_written":False, "copied":False, "old_note_absent":True})


def watch_recording(process, stop, ready, seconds=174):
    """Stop GUI readiness promptly if the owned recorder exits before rollover."""
    deadline = time.monotonic() + seconds
    # Poll the process while waiting: a set ready flag must mean a live recorder.
    while not stop.is_set() and time.monotonic() < deadline:
        if process.poll() is not None:
            ready.clear()
            raise RuntimeError("Our screen recorder exited before the trial/rollover ended")
        stop.wait(.25)


def finish_recording(prefix, process, pid, remote, local):
    """Bound recorder shutdown/transfer and preserve the phase of any failure."""
    started = time.monotonic()

    def checkpoint(phase):
        """Save shutdown progress separately from the concurrently written trajectory."""
        save_json(local.with_suffix(".shutdown.json"), {"phase": phase, "elapsed_seconds": time.monotonic() - started})

    checkpoint("signal")
    subprocess.run(prefix + ["shell", "kill", "-2", pid], check=True, capture_output=True, timeout=5)
    checkpoint("wait")
    process.wait(timeout=15)
    checkpoint("pull")
    subprocess.run(prefix + ["pull", remote, str(local)], check=True, capture_output=True, timeout=20)
    if not local.is_file() or local.stat().st_size < 1000:
        raise RuntimeError("Recording file missing or empty")
    checkpoint("remove_pulled_remote")
    # Remove only this already-pulled generated clip, retaining it if transfer fails.
    subprocess.run(prefix + ["shell", "rm", remote], check=True, capture_output=True, timeout=5)
    checkpoint("complete")


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
                # A delayed PID is not failure after one second. Bound readiness
                # and prove ownership before releasing any GUI action or killing it.
                pid = ""
                for _ in range(20):
                    candidate = subprocess.run(prefix + ["shell", "pidof", "screenrecord"], capture_output=True, timeout=5).stdout.decode().strip()
                    if candidate.isdigit():
                        command = subprocess.check_output(prefix + ["shell", "cat", f"/proc/{candidate}/cmdline"], timeout=5)
                        if remote.encode() not in command:
                            raise RuntimeError("Recorder belongs to another run")
                        pid = candidate
                        break
                    if process.poll() is not None or stop.wait(.5):
                        break
                if not pid:
                    process.terminate()
                    process.wait(timeout=5)
                    raise RuntimeError("Our screen recorder did not become ready within its bounded wait")
                ready.set()
                watch_recording(process, stop, ready)
                ready.clear()  # Pause GUI execution during rollover/pulling.
                finish_recording(prefix, process, pid, remote, output / f"video_{number:03d}.mp4")
    except Exception:
        errors.append(traceback.format_exc())
        stop.set()
        ready.set()


def initialize_existing_move(task, env, prepare_source=False):
    """Prepare one new test file or preserve the previous move, without clearing storage."""
    from android_world.task_evals import task_eval
    from android_world.utils import file_utils
    if task.name != "FilesMoveFile":
        raise ValueError("--continue-state is only supported for FilesMoveFile")
    # Linked trials accept simple storage names, never arbitrary paths or traversal.
    for key in ("file_name", "source_folder", "destination_folder"):
        value = task.params[key]
        if not isinstance(value, str) or value in {"", ".", ".."} or "/" in value or "\\" in value:
            raise ValueError("Linked move requires simple file/folder names")
    move = task.move_file_task
    exists = file_utils.check_file_or_folder_exists
    if exists(task.params["file_name"], move.dest_directory, env.controller):
        raise RuntimeError("Linked move destination already contains the file")
    source_exists = exists(task.params["file_name"], move.source_directory, env.controller)
    if prepare_source:
        if source_exists:
            raise RuntimeError("Source already exists; use --continue-state to preserve it")
        file_utils.create_file(task.params["file_name"], move.source_directory, env.controller)
        file_utils.mkdir(move.dest_directory, env.controller)
    elif not source_exists:
        raise RuntimeError("Linked move source file is missing")
    # Official base initialization restores app state/time and marks both evaluators
    # initialized. Skip MoveFile's storage clear/create so the actual file carries over.
    task_eval.TaskEval.initialize_task(task, env)
    task_eval.TaskEval.initialize_task(move, env)


def main():
    """Initialize one official task, run bounded steps, verify, and preserve evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=TASKS, default="ContactsAddContact")
    parser.add_argument("--observation", choices=["screenshot", "tree", "tree_first"], default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--config", type=Path, default=PROJECT / "agent_config.json")
    parser.add_argument("--params", type=Path, help="JSON file containing exact official task parameters")
    parser.add_argument("--continue-state", action="store_true", help="Preserve the previous FilesMoveFile result for a linked reverse move")
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
    from autoglm_agent import AutoGLMAgent, api_settings

    output = PROJECT / "runs" / datetime.now(timezone.utc).strftime(f"trial_{args.task}_%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True)
    print(f"Evidence: {output}", flush=True)
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("single_attempt_adb"):
        enable_single_attempt_adb()
    if args.task == "SystemCopyToClipboard" and config.get("task_guidance") and config.get("clipboard_input_app") != "markor":
        raise ValueError("The guided Clipboard procedure requires clipboard_input_app=markor")
    agent_class = AutoGLMAgent
    if config.get("text_input_backend") == "adb_keyboard":
        enabled = subprocess.check_output([str(adb), "-s", "emulator-5554", "shell", "ime", "list", "-s"], timeout=5).decode()
        if "com.android.adbkeyboard/.AdbIME" not in enabled.splitlines():
            raise RuntimeError("Enable ADB Keyboard before this variant; see docs/UPSTREAM_REFERENCE_COMPARISON.md")
    if config.get("agent_backend") == "upstream":
        from upstream_reference import UpstreamReference, reference_preflight
        reference_preflight(adb)
        agent_class = UpstreamReference
    # Contacts' observed Save at step 12 needs a subsequent model inspection.
    config["max_steps"] = config.get("task_step_budgets", {}).get(args.task, config["max_steps"])
    if config.get("provider") != "zai" or config["observation"] != "screenshot" or args.observation not in {None, "screenshot"}:
        raise ValueError("AutoGLM migration uses Z.ai and screenshot observations")
    endpoint, model, _ = api_settings()
    if config["model"] != model:
        raise ValueError("Config and .env model differ")
    config["api_base_url"] = endpoint
    config.update(observation=args.observation or config.get("task_observations", {}).get(args.task, config["observation"]), task_seed=args.seed, task_name=args.task)
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
    run_start, agent_start = start, None
    try:
        # Preserve the exact small program and dependency/model identities per run.
        source = output / "source"
        source.mkdir()
        for filename in ("run_task.py", "autoglm_agent.py", "upstream_reference.py", "probe_connection.py", "android_compat.py", "run.ps1", "trajectory.py"):
            shutil.copyfile(PROJECT / filename, source / filename)
        (source / "instructions").mkdir()
        shutil.copyfile(PROJECT / "instructions/autoglm.md", source / "instructions/autoglm.md")
        shutil.copyfile(PROJECT / "instructions/assessment.md", source / "instructions/assessment.md")
        shutil.copyfile(PROJECT / "instructions/task_guides.md", source / "instructions/task_guides.md")
        shutil.copyfile(PROJECT / "instructions/android_interactions.md", source / "instructions/android_interactions.md")
        save_json(output / "versions.json", {"model": model, "provider": "zai", "endpoint": endpoint,
            "provider_revision": "not exposed by API; response model/request IDs saved per call",
            "python": sys.version, "android_world": importlib.metadata.version("android-world"),
            "android_env": importlib.metadata.version("android-env")})
        if config.get("tree_backend") in {"uiautomator", "none"}:
            prepare_observations(adb, output, config)
        env = load_task_env(adb, args.task, config)
        save_json(output / "config.json", config)
        # Install only infrastructure and the app needed by this learning task.
        task_apps = {
            "ContactsAddContact": (apps.ContactsApp,),
            "SystemWifiTurnOn": (apps.SettingsApp,),
            "CameraTakePhoto": (apps.CameraApp,),
            "ClockTimerEntry": (apps.ClockApp,),
            "SimpleSmsSend": (apps.SimpleSMSMessengerApp,),
            "FilesMoveFile": (apps.FilesApp,),
            # Clipper supports the verifier. The selected GUI editor supplies
            # text selection/copy; official setup/reset is separate from actions.
            "SystemCopyToClipboard": (apps.ClipperApp,
                apps.MarkorApp if config.get("clipboard_input_app") == "markor" else apps.ChromeApp),
        }
        required = (apps.AndroidWorldApp,) + task_apps[args.task]
        from android_world.utils import app_snapshot, file_utils
        # Check each app separately, including clipboard verifier infrastructure.
        for app in required:
            ensure_required_app(app, env, output)
        random.seed(args.seed)
        task_class = registry.TaskRegistry().get_registry("android_world")[args.task]
        params = json.loads(args.params.read_text(encoding="utf-8")) if args.params else task_class.generate_random_params()
        task = task_class(params)
        # Clipper is official verifier infrastructure, not an interactive GUI app.
        config["allowed_apps"] = [app.app_name for app in task_apps[args.task] if app.app_name != "clipper"]
        save_json(output / "config.json", config)
        save_json(output / "task.json", {"name": args.task, "goal": task.goal, "parameters": params,
                  "seed": args.seed, "source_commit": "2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7",
                  "initialization_mode": "linked_existing_file" if args.continue_state else
                      "scoped_new_file" if args.task == "FilesMoveFile" else "official_task_reset"})
        log_event(output, "OFFICIAL TASK INPUT", {"goal": task.goal, "parameters": params,
                  "task_seed": args.seed, "model_metadata": "versions.json"})
        # Match the official runner: reset BEFORE task-specific initialization.
        # A reset after initialization was measured to turn Wi-Fi back on.
        env.reset(go_home=True)
        # Official task initialization resets its own apps. Also restore the
        # extra GUI app used for clipboard entry, avoiding cross-run editor state.
        for app in task_apps[args.task]:
            if app.app_name not in task.app_names and app.app_name != "clipper":
                app_snapshot.restore_snapshot(app.app_name, env.controller)
        if args.task == "SystemCopyToClipboard" and config.get("reset_clipboard_editor"):
            reset_clipboard_editor(env, output)
        env.reset(go_home=True)
        # Official initialization clears test contacts/sets Wi-Fi state and device time.
        if args.task == "FilesMoveFile" or args.continue_state:
            initialize_existing_move(task, env, prepare_source=args.task == "FilesMoveFile" and not args.continue_state)
            log_event(output, "LINKED FILE INITIALIZATION", {"mode":"official_base_initialization",
                "storage_reset":False, "source_file_created":not args.continue_state,
                "file_moved_by_preparation":False})
        else:
            task.initialize_task(env)
        summary["initial_verifier_score"] = verify_task(task, env, output)
        log_event(output, "INITIAL VERIFIER", {"score": summary["initial_verifier_score"]})
        if summary["initial_verifier_score"] != 0.0:
            raise RuntimeError("Invalid starting state: task already satisfies the verifier")
        summary["evaluation_valid"] = True
        recorder = threading.Thread(target=record_video, args=(adb, output, stop, ready, video_errors))
        recorder.start()
        if not ready.wait(timeout=15) or video_errors:
            raise RuntimeError("Recording failed to start: " + str(video_errors))
        agent = agent_class(env, output, config, params)
        agent.recording_ready = ready
        agent.recording_errors = video_errors
        start = time.monotonic()
        agent_start = start
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
        summary["error_class"] = "environment_setup_error" if agent is None else "validation_error" if isinstance(error, ValueError) else "api_error" if isinstance(error, urllib.error.URLError) else "control_no_progress" if str(error) == "Repeated action without visible effect; stopping" else "environment_or_execution_error"
        if agent is not None and agent.assessment_errors:
            summary["error_class"] = "assessment_error"
        summary["stop_reason"] = "error"
        log_event(output, "RUN ERROR", {"error": summary["error"], "class": summary["error_class"]}, summary.get("steps_attempted"))
        print(summary["error"], flush=True)
    finally:
        # Verification is independent of agent completion, including after errors.
        if task is not None and task.initialized and env is not None:
            try:
                score = verify_task(task, env, output)
                summary["verifier_score"] = score
                summary["verifier"] = "PASS" if score == 1.0 else "FAIL"
                summary["failure_class"] = "false_done" if summary["agent_done"] and score != 1.0 else None
            except Exception:
                summary["verifier"] = "ERROR"
                summary["verifier_error"] = traceback.format_exc()
        stop.set()
        if agent is not None:
            summary["model_calls_attempted"] = agent.calls
            summary["assessment_calls_attempted"] = agent.assessment_calls
            summary["assessment_errors"] = agent.assessment_errors
            summary["gui_actions_dispatched"] = sum(action["action_type"] != "status" for action in agent.executed_actions)
            summary["screenshot_fallbacks"] = agent.fallback_events
        if recorder is not None:
            recorder.join(timeout=55)  # Shutdown's bounded phases total at most 45 seconds.
        summary["video_errors"] = video_errors
        if video_errors or (recorder is not None and recorder.is_alive()):
            summary["evaluation_valid"] = False
            summary["recording_error"] = "Recording failed or did not finish within its join budget"
        summary["verified_agent_success"] = summary["evaluation_valid"] and summary["verifier"] == "PASS"
        summary["clean_agent_success"] = summary["verified_agent_success"] and summary["agent_done"] and summary.get("stop_reason") == "complete" and not summary.get("error")
        summary["videos"] = [path.name for path in sorted(output.glob("video_*.mp4"))]
        summary["duration_seconds"] = time.monotonic() - run_start
        summary["agent_phase_seconds"] = time.monotonic() - agent_start if agent_start is not None else None
        save_json(output / "summary.json", summary)
        log_event(output, "STOP AND OFFICIAL VERIFICATION", summary)
        print(json.dumps(summary, indent=2), flush=True)
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()
