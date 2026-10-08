"""Instrument the pinned upstream PhoneAgent without changing its GUI policy.

The shared runner supplies official initialization, video and final verification.
This adapter supplies logging, emulator-only bounds and honest error reporting.
"""

import ast
import base64
import copy
from dataclasses import asdict
import hashlib
import importlib.util
from io import BytesIO
import os
from pathlib import Path
import subprocess
import sys
import time

from PIL import Image
from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent
UPSTREAM = PROJECT / ".tools/Open-AutoGLM"
COMMIT = "86f55382982fb054e8fc98ca80609dff8a2cdc3c"


def windows_prompt_import():
    """Load the unused Chinese prompt with equivalent Windows-safe date formatting.

    Windows Python's strftime cannot encode its Chinese literal format. The
    English prompt is untouched; the checkout and original evidence stay intact.
    """
    name = "phone_agent.config.prompts_zh"
    path = UPSTREAM / "phone_agent/config/prompts_zh.py"
    source = path.read_text(encoding="utf-8")
    expression = 'today.strftime("%Y年%m月%d日")'
    replacement = 'f"{today.year:04d}年{today.month:02d}月{today.day:02d}日"'
    if source.count(expression) != 1:
        raise RuntimeError("Unexpected pinned Chinese date expression")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(source.replace(expression, replacement), str(path), "exec"), module.__dict__)


def reference_preflight(adb):
    """Check native imports and enabled keyboard before task initialization/video."""
    sys.path.insert(0, str(UPSTREAM))
    windows_prompt_import()
    from phone_agent import PhoneAgent
    enabled = subprocess.check_output([str(adb), "-s", "emulator-5554", "shell", "ime", "list", "-s"], text=True, timeout=10)
    if "com.android.adbkeyboard/.AdbIME" not in enabled.splitlines():
        raise RuntimeError("Enable official ADB Keyboard before the upstream reference; see docs/UPSTREAM_REFERENCE_COMPARISON.md")


def literal_call(text):
    """Check one native call containing only literal keyword arguments."""
    call = ast.parse(text.strip(), mode="eval").body
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
        raise ValueError("Expected one native call")
    if call.func.id not in {"do", "finish"} or call.args:
        raise ValueError("Unsupported native call")
    fields = {}
    for keyword in call.keywords:
        if keyword.arg is None or keyword.arg in fields or keyword.arg == "_metadata":
            raise ValueError("Unsupported or repeated keyword")
        fields[keyword.arg] = ast.literal_eval(keyword.value)
    return {**fields, "_metadata": call.func.id}


def check_action(action):
    """Bound the reference's GUI arguments; never execute model-generated code."""
    if action.get("_metadata") == "finish":
        if set(action) != {"_metadata", "message"} or not isinstance(action["message"], str):
            raise ValueError("Invalid finish")
        return
    allowed = {"Launch": {"app"}, "Tap": {"element"}, "Double Tap": {"element"},
               "Long Press": {"element"}, "Type": {"text"}, "Type_Name": {"text"},
               "Swipe": {"start", "end"}, "Wait": {"duration"}, "Home": set(), "Back": set()}
    name = action.get("action")
    if name not in allowed or set(action) != allowed[name] | {"action", "_metadata"}:
        raise ValueError("Unsupported reference action or arguments")
    if action.get("_metadata") != "do":
        raise ValueError("Invalid native metadata")
    for field in ("element", "start", "end"):
        if field in action:
            point = action[field]
            if not isinstance(point, list) or len(point) != 2 or any(
                type(value) not in {int, float} or not 0 <= value <= 1000 for value in point):
                raise ValueError("Expected a normalized point in [0, 1000]")
    for field in ("app", "text", "duration"):
        if field in action and (not isinstance(action[field], str) or len(action[field]) > 1000):
            raise ValueError("Expected bounded string argument")
    if name == "Wait" and not 0 <= float(action["duration"].replace("seconds", "").strip()) <= 5:
        raise ValueError("Wait exceeds reference budget")


class UpstreamReference:
    """Expose the official PhoneAgent through the project's existing run interface."""

    def __init__(self, env, output, config, scratch):
        """Load checked pinned sources and instrument their API and action boundaries."""
        from autoglm_agent import api_settings
        self.output, self.config = Path(output), config
        self.calls, self.assessment_calls = 0, 0
        self.assessment_errors, self.executed_actions, self.fallback_events = [], [], []
        self.recording_ready, self.recording_errors = None, []
        self.deadline = time.monotonic() + config["max_seconds"]
        self.response, self.folder, self.request_error = None, None, None
        revision = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
        if revision != COMMIT or subprocess.check_output(["git", "-C", str(UPSTREAM), "status", "--porcelain"], text=True).strip():
            raise RuntimeError("Reference checkout must be clean and pinned")
        sys.path.insert(0, str(UPSTREAM))
        os.environ["PATH"] = str(Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools") + os.pathsep + os.environ["PATH"]
        windows_prompt_import()
        from phone_agent import PhoneAgent
        from phone_agent.agent import AgentConfig
        from phone_agent.model import ModelConfig
        from openai import OpenAI
        endpoint, model, self.key = api_settings()
        self.native = PhoneAgent(ModelConfig(base_url=endpoint, api_key=self.key, model_name=model,
            lang="en", **config["sampling"]), AgentConfig(max_steps=config["max_steps"],
            device_id="emulator-5554", lang="en", verbose=False))
        # Only client timeout/retries change; upstream request construction stays intact.
        self.native.model_client.client = OpenAI(base_url=endpoint, api_key=self.key,
            timeout=config["request_timeout"], max_retries=0)
        self.request = self.native.model_client.request
        self.create = self.native.model_client.client.chat.completions.create
        self.native.model_client.client.chat.completions.create = self.logged_stream
        self.native.model_client.request = self.logged_request
        self.execute = self.native.action_handler.execute
        self.native.action_handler.execute = self.checked_execute
        hashes = {}
        # Snapshot every Python source actually available to the upstream package.
        for source in UPSTREAM.joinpath("phone_agent").rglob("*.py"):
            relative = source.relative_to(UPSTREAM)
            target = self.output / "source/upstream" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
        save_json(self.output / "upstream.json", {"commit": revision, "source_sha256": hashes,
            "openai": "2.9.0", "native_prompt": self.native.agent_config.system_prompt,
            "changes": ["logging", "emulator-only target", "literal/argument validation",
                        "Windows-safe equivalent date formatting in unused Chinese prompt import",
                        "bounded API timeout with no retries", "fail closed on errors or black screenshot"]})

    def logged_stream(self, **kwargs):
        """Save provider stream chunks unchanged and give them to the native client."""
        for chunk in self.create(**kwargs):
            data = chunk.model_dump()
            self.chunks.append(data)
            save_json(self.folder / "provider_chunks.json", self.chunks)
            yield chunk

    def logged_request(self, messages):
        """Preserve actual native model input and response without image/key dumps."""
        readable = copy.deepcopy(messages)
        for message in readable:
            if isinstance(message.get("content"), list):
                for item in message["content"]:
                    if item.get("type") == "image_url":
                        image = base64.b64decode(item["image_url"]["url"].split(",", 1)[1])
                        with Image.open(BytesIO(image)) as screen:
                            if screen.convert("RGB").getbbox() is None:
                                raise RuntimeError("Native screenshot is black; reference stopped")
                        (self.folder / "screen.png").write_bytes(image)
                        item["image_url"]["url"] = "[screen.png]"
        save_json(self.folder / "request.json", {"messages": readable, "stream": True,
            "model": self.config["model"], **self.config["sampling"]})
        self.calls += 1
        self.chunks = []
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Reference time budget expired")
        self.native.model_client.client.timeout = min(remaining, self.config["request_timeout"])
        log_event(self.output, "NATIVE MODEL REQUEST", {"call": self.calls, "request": str(self.folder.relative_to(self.output) / "request.json")}, self.native.step_count)
        try:
            self.response = self.request(messages)
            save_json(self.folder / "response.json", asdict(self.response))
            log_event(self.output, "NATIVE MODEL REPLY", self.response.raw_content, self.native.step_count)
            if any(choice.get("finish_reason") == "length" for chunk in self.chunks for choice in chunk.get("choices", [])):
                raise RuntimeError("Truncated upstream response")
            return self.response
        except Exception as error:
            self.request_error = str(error).replace(self.key, "[REDACTED]")
            save_json(self.folder / "request_error.json", {"error": self.request_error})
            raise

    def checked_execute(self, action, width, height):
        """Reject native error-as-finish fallbacks and record actual GUI dispatch."""
        save_json(self.folder / "parsed_action.json", action)
        try:
            expected = literal_call(self.response.action)
            if expected.get("action") == "Type_Name":
                expected["action"] = "Type"
            if action != expected:
                raise ValueError("Native parser altered the call or substituted finish after an error")
            check_action(action)
            if self.recording_errors or not self.recording_ready.wait(15):
                raise RuntimeError("Recording unavailable before native dispatch")
            if time.monotonic() >= self.deadline:
                raise TimeoutError("Reference time budget expired before dispatch")
            if action.get("action") in {"Type", "Type_Name"}:
                installed = subprocess.check_output(["adb", "-s", "emulator-5554", "shell", "ime", "list", "-s"], text=True)
                if "com.android.adbkeyboard/.AdbIME" not in installed:
                    raise RuntimeError("Native Type requires ADB Keyboard; missing emulator prerequisite")
        except Exception as error:
            # Native execution catches exceptions and tries a fallback finish.
            # Keep the first cause rather than replacing it with that second error.
            if not (self.folder / "boundary_error.json").exists():
                save_json(self.folder / "boundary_error.json", {"error": str(error), "executed": False})
            raise
        log_event(self.output, "NATIVE EXECUTION START", action, self.native.step_count)
        self.executed_actions.append({"action_type": "status" if action["_metadata"] == "finish" else action["action"], "native": action})
        result = self.execute(action, width, height)
        save_json(self.folder / "execution.json", asdict(result))
        log_event(self.output, "NATIVE EXECUTION RESULT", asdict(result), self.native.step_count)
        return result

    def step(self, goal):
        """Run one original native step and map only a valid model finish to done."""
        from android_world.agents.base_agent import AgentInteractionResult
        self.folder = self.output / f"step_{self.native.step_count + 1:03d}"
        self.folder.mkdir()
        self.response, self.request_error = None, None
        try:
            result = self.native.step(goal)
        except Exception:
            boundary = self.folder / "boundary_error.json"
            if boundary.exists():
                import json
                raise RuntimeError(json.loads(boundary.read_text())["error"]) from None
            raise
        save_json(self.folder / "result.json", asdict(result))
        boundary = self.folder / "boundary_error.json"
        if boundary.exists() or not result.success:
            raise RuntimeError("Upstream reference failed; inspect this step's raw reply and errors")
        done = result.finished and result.action is not None and result.action.get("_metadata") == "finish"
        if result.finished and not done:
            raise RuntimeError("Native stopped without a valid model finish")
        return AgentInteractionResult(done=done, data={"action": {"goal_status": "complete" if done else "running"}})
