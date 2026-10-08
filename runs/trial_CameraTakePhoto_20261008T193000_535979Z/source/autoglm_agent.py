"""One screenshot → AutoGLM → checked Android World action loop.

Protocol adapted from zai-org/Open-AutoGLM's English prompt, model client and
action handler. Pseudo-calls are parsed as data with AST, never executed as code.
The existing GELab file and recorded runs remain available as historical evidence.
"""

import ast
import base64
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from android_world.agents import base_agent
from android_world.env import adb_utils, json_action, representation_utils
from PIL import Image, ImageChops, ImageStat

from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent

# Exact observed multilingual names, plus the pinned upstream SMS app identifier.
# Values still pass the task's allowed-app check; unknown names are never guessed.
APP_NAME_ALIASES = {
    "简单短信消息发送器": "simple sms messenger",
    "简单短信消息": "simple sms messenger",
    "simplesmsmessenger": "simple sms messenger",
}


def launch_chrome_once(timeout):
    """Launch the model-selected Chrome activity once, with a bounded cold-start wait.

    Use Android World's component mapping and its am-start command. Its generic
    helper retries and restarts ADB after5 seconds, terminating video sessions.
    This isolated transport repair permits no uncertain launch replay.
    """
    activity = adb_utils.get_adb_activity("chrome")
    if not activity:
        raise RuntimeError("Official Chrome activity mapping unavailable")
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    return subprocess.run([str(adb), "-s", "emulator-5554", "shell", "am", "start",
        "-W", "-n", activity], check=True, capture_output=True, timeout=timeout)

# Visible completion criteria, not fixed coordinates, action replays or verifier
# results. The model decides from the latest screenshot and supplied GUI state.
COMPLETION_RULES = {
    "SystemWifiTurnOn": "Wi-Fi in Settings is ON (checked=true). A network connection is not required. Finish when this observed state holds.",
    "CameraTakePhoto": "Exactly one new photo has been captured: one shutter action in the executed history and a new captured-photo thumbnail or preview in the GUI. Finish when both hold; launching Camera alone is insufficient.",
    "ClockTimerEntry": "Timer displays the exact requested hours, minutes and seconds, with Start available and the timer not running. Finish when that visible state holds; do not start it.",
    "ContactsAddContact": "The saved contact view shows the exact requested full name and phone number after Save. A filled unsaved form is insufficient. Finish on the saved result.",
    "SimpleSmsSend": "Simple SMS Messenger shows the exact requested message as an outgoing sent message in the conversation with the requested phone number, after the Send action. A filled message draft is insufficient; a pending or failed message is not sent. Finish when the visible sent result holds; do not send it again.",
    "FilesMoveFile": "The exact requested file is present in the destination folder and absent from the source folder after a GUI move. A copy or an open destination-selection dialog is insufficient. Check the current folder and exact filename, then finish when the move result is supported by the GUI and executed history. Do not move it again after completion.",
    "SystemCopyToClipboard": "The exact requested text has been fully selected and copied through the visible Copy command; the selection menu has closed afterwards. Finish on that observed result. A transient clipboard chip or toast is optional. The task input is text to copy, not current clipboard state. Clipper is verifier infrastructure.",
}


def api_settings():
    """Read simple .env values as data; return endpoint/model/key without logging it."""
    values = {}
    # Only parse assignments, never execute shell expressions or expand variables.
    for line in (PROJECT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z_][A-Z_0-9]*", name.strip()):
            raise ValueError("Unsupported .env assignment")
        values[name.strip()] = value.strip().strip("\"'")
    endpoint = values.get("PHONE_AGENT_BASE_URL", "").rstrip("/")
    model = values.get("PHONE_AGENT_MODEL")
    key = values.get("ZAI_API_KEY") or values.get("PHONE_AGENT_API_KEY")
    if endpoint != "https://api.z.ai/api/paas/v4" or model != "autoglm-phone-multilingual" or not key:
        raise ValueError("Expected Z.ai endpoint, multilingual model and a nonempty key in .env")
    return endpoint, model, key


def completion_condition(task_name, inputs):
    """State the visible goal and format a timer's exact requested keypad value."""
    condition = COMPLETION_RULES[task_name]
    if task_name == "ClockTimerEntry":
        hours, minutes, seconds = (inputs[key] for key in ("hours", "minutes", "seconds"))
        # Leading zero taps do not change an empty keypad; the final display is padded.
        digits = f"{hours:02d}{minutes:02d}{seconds:02d}".lstrip("0") or "0"
        condition += f" Target display: {hours:02d}h {minutes:02d}m {seconds:02d}s. Equivalent literal HHMMSS input value: {digits!r}."
    return condition


def native_prompt(apps):
    """Render the existing Launch example with a real allowed argument, not a placeholder."""
    prompt = (PROJECT / "instructions/autoglm.md").read_text(encoding="utf-8")
    if not apps:
        raise ValueError("Native action context needs an available GUI app")
    # This changes an example argument only; the model still selects every action.
    return prompt.replace('do(action="Launch", app="app_name")',
        'do(action="Launch", app=' + json.dumps(apps[0]) + ')')


def task_guide(task_name, inputs):
    """Load one procedure; format task values without choosing its next action."""
    source = (PROJECT / "instructions/task_guides.md").read_text(encoding="utf-8")
    heading = f"## {task_name}\n"
    if source.count(heading) != 1:
        raise ValueError("Expected exactly one guide for the selected task")
    common = source.split("\n## ", 1)[0].split("\n", 1)[1].strip()
    selected = source.split(heading, 1)[1].split("\n## ", 1)[0].strip()
    if task_name == "ClockTimerEntry":
        display = f"{inputs['hours']:02d}h {inputs['minutes']:02d}m {inputs['seconds']:02d}s"
        digits = f"{inputs['hours']:02d}{inputs['minutes']:02d}{inputs['seconds']:02d}".lstrip("0") or "0"
        selected = selected.format(timer_display=display, timer_input=digits, timer_sequence=", ".join(digits))
    return common + "\n\n" + selected


def parse_action(raw):
    """Accept one unique literal pseudo-call, collapsing only exact duplicates."""
    if "<answer>" in raw:
        answers = list(dict.fromkeys(answer.strip() for answer in re.findall(r"<answer>(.*?)</answer>", raw, flags=re.DOTALL)))
        if len(answers) != 1:
            raise ValueError("Expected one complete answer block")
        body = answers[0].strip()
    else:
        # Native newer replies may omit tags; only their final action line counts.
        lines = list(dict.fromkeys(line.strip() for line in raw.splitlines() if re.match(r"\s*(do|finish)\(", line)))
        if len(lines) != 1:
            raise ValueError("Expected exactly one do(...) or finish(...) action")
        body = lines[0]
    try:
        node = ast.parse(body, mode="eval").body
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id not in {"do", "finish"} or node.args:
            raise ValueError("Only do/finish with literal keyword arguments are allowed")
        values = {}
        # Reject duplicate keywords and **expansion instead of guessing intent.
        for item in node.keywords:
            if item.arg is None or item.arg == "command" or item.arg in values:
                raise ValueError("Duplicate or expanded argument")
            values[item.arg] = ast.literal_eval(item.value)
    except SyntaxError as error:
        # Native finish messages sometimes contain unescaped quoted UI labels.
        # Treat only that outer text wrapper as data, never as executable syntax.
        match = re.fullmatch(r"finish\(message=([\"'])(.+)\1\)", body, re.DOTALL)
        if match and not re.search(r"[\"']\s*(?:\)|,|[A-Za-z_]\w*\s*=)", match[2]):
            return {"command": "finish", "message": match[2]}
        raise ValueError("Malformed action syntax") from error
    except TypeError as error:
        raise ValueError("Malformed action syntax") from error
    return {"command": node.func.id, **values}


def pixel_point(point, state):
    """Convert a checked normalized point or model-chosen box center to pixels."""
    if not isinstance(point, list) or len(point) not in {2, 4} or any(type(v) is not int or not 0 <= v <= 1000 for v in point):
        raise ValueError("Coordinates must be two point integers or four box integers in normalized 0..1000 units, NOT screenshot pixels. Use the current observed tap centres: they are already normalized. Do not reuse pixel bounds as an action point.")
    if len(point) == 4:
        if point[0] >= point[2] or point[1] >= point[3]:
            raise ValueError("Bounding box must have ordered, nonzero width and height")
        # This is geometric grounding of the model's own region, not a new decision.
        point = [(point[0] + point[2]) / 2, (point[1] + point[3]) / 2]
    height, width = state.pixels.shape[:2]
    return min(width - 1, int(point[0] * width / 1000)), min(height - 1, int(point[1] * height / 1000))


def convert_action(fields, state, allowed_apps):
    """Validate action-specific fields and convert to Android World's fixed actions."""
    if fields["command"] == "finish":
        if set(fields) != {"command", "message"} or not isinstance(fields["message"], str):
            raise ValueError("finish requires only a text message")
        return {"action_type": "status", "goal_status": "complete", "reason": fields["message"]}
    name = fields.get("action")
    arguments = {"Tap": {"element"}, "Long Press": {"element"}, "Swipe": {"start", "end"},
                 "Type": {"text"}, "Launch": {"app"}, "Back": set(), "Home": set(), "Wait": {"duration"}}
    if not isinstance(name, str) or name not in arguments or set(fields) != {"command", "action"} | arguments[name]:
        raise ValueError("Unsupported action or unexpected arguments")
    if name in {"Tap", "Long Press"}:
        x, y = pixel_point(fields["element"], state)
        return {"action_type": "click" if name == "Tap" else "long_press", "x": x, "y": y}
    if name == "Swipe":
        return {"action_type": "slide", "start": pixel_point(fields["start"], state), "end": pixel_point(fields["end"], state)}
    if name == "Type":
        text = fields["text"]
        if not isinstance(text, str) or not text or len(text) > 2000:
            raise ValueError("Type needs 1..2000 characters")
        if state.ui_elements and not any(e.is_visible and e.is_editable and e.is_focused for e in state.ui_elements):
            raise ValueError("No focused editable field; tap the real field first")
        return {"action_type": "input_text", "text": text, "clear_text": True}
    if name == "Launch":
        app = fields["app"]
        canonical = APP_NAME_ALIASES.get(app.lower(), app.lower()) if isinstance(app, str) else None
        if canonical not in allowed_apps:
            examples = [f'do(action="Launch", app={json.dumps(value)})' for value in allowed_apps]
            raise ValueError(f"Launch app {app!r} is unavailable; allowed app values: {json.dumps(allowed_apps)}. "
                f"Copy a literal app value without translation. Valid Launch syntax: {' OR '.join(examples)}")
        return {"action_type": "open_app", "app_name": canonical}
    if name == "Wait":
        duration = fields["duration"]
        if isinstance(duration, str) and re.fullmatch(r"\d+(?:\.\d+)? seconds?", duration):
            duration = float(duration.split()[0])
        if type(duration) not in {int, float} or not 0 <= duration <= 5:
            raise ValueError("Wait duration must be 0..5 seconds")
        return {"action_type": "wait", "seconds": duration}
    return {"action_type": "navigate_back" if name == "Back" else "navigate_home"}


def timer_keypad_visible(state):
    """Recognize the actual Clock entry GUI without inferring its next action."""
    return any(e.is_visible and e.resource_id == "com.google.android.deskclock:id/timer_setup_time" for e in state.ui_elements)


def timer_buffer_note(state):
    """Render only observed display digits/count; never compare with a task target."""
    display = next((e.text for e in state.ui_elements if e.is_visible
        and e.resource_id == "com.google.android.deskclock:id/timer_setup_time"), "")
    match = re.fullmatch(r"(\d{2})h (\d{2})m (\d{2})s", display)
    if not match:
        return ""
    digits = "".join(match.groups()).lstrip("0")
    return f"Observed keypad buffer from the GUI display (padding removed): {digits!r}; observed non-padding digit count: {len(digits)}."


def image_difference(before, after, box=None):
    """Measure normalized grayscale change in a screen region, ignoring no pixels implicitly."""
    images = [Image.fromarray(state.pixels).convert("L") for state in (before, after)]
    if images[0].size != images[1].size:
        return 1.0
    if box:
        images = [image.crop(box) for image in images]
    images = [image.resize((64, 128)) for image in images]
    return ImageStat.Stat(ImageChops.difference(*images)).mean[0] / 255


def type_without_submit(text, controller):
    """Replace focused GUI text using official helpers without an added Enter."""
    # Match native AutoGLM Type semantics; Enter would submit Chrome or move focus.
    response = adb_utils.issue_generic_request(["shell", "input", "keycombination", "113", "29"], controller)
    adb_utils.check_ok(response, "Select existing text failed")
    adb_utils.check_ok(adb_utils.press_keyboard_generic("67", controller), "Delete selected text failed")
    adb_utils.type_text(text, controller, timeout_sec=10)


def type_with_adb_keyboard(text, timeout, folder):
    """Adapt native AutoGLM focused-input Type with UTF-8, bounded calls and no replay."""
    adb = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"
    prefix = [str(adb), "-s", "emulator-5554", "shell"]
    deadline = time.monotonic() + timeout
    record = {"backend": "native_adb_keyboard", "attempts": 1, "text_length": len(text), "enter_added": False}

    def call(arguments):
        """Run each native input command once within the shared action deadline."""
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Native typing deadline reached; no replay")
        return subprocess.run(prefix + arguments, check=True, capture_output=True, text=True, timeout=remaining)

    original = call(["settings", "get", "secure", "default_input_method"]).stdout.strip()
    if not re.fullmatch(r"[\w.]+/[\w.]+", original):
        raise RuntimeError("Original IME unavailable; native typing not attempted")
    record["original_ime"] = original
    try:
        record["phase"] = "switch"
        save_json(folder / "type_transport.json", record)
        call(["ime", "set", "com.android.adbkeyboard/.AdbIME"])
        time.sleep(1)  # Native AutoGLM's keyboard-switch/clear/input delays are one second.
        record["phase"] = "clear"
        save_json(folder / "type_transport.json", record)
        call(["am", "broadcast", "-a", "ADB_CLEAR_TEXT"])
        time.sleep(1)
        record["phase"] = "input"
        save_json(folder / "type_transport.json", record)
        payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
        call(["am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", payload])
        record["input_call_returned"] = True
        time.sleep(1)
    finally:
        # Restoring the keyboard is cleanup, never a retry of uncertain text input.
        subprocess.run(prefix + ["ime", "set", original], check=True, capture_output=True, timeout=5)
        time.sleep(1)
        record["restored_original_ime"] = True
        save_json(folder / "type_transport.json", record)
    record["phase"] = "complete"
    save_json(folder / "type_transport.json", record)


def target_at(state, action):
    """Identify the selected control, excluding unrelated keyboard/time widgets."""
    candidates = []
    # Only the control at the chosen point (or focused input) needs identity checks.
    for element in state.ui_elements:
        box = element.bbox_pixels
        if not element.is_visible or box is None:
            continue
        selected = element.is_editable and element.is_focused if action["action_type"] == "input_text" else (
            box.x_min <= action.get("x", -1) < box.x_max and box.y_min <= action.get("y", -1) < box.y_max)
        if selected and (element.is_clickable or element.is_editable or element.is_checkable):
            candidates.append(element)
    if not candidates:
        return None
    return asdict(min(candidates, key=lambda e: (e.bbox_pixels.x_max - e.bbox_pixels.x_min) * (e.bbox_pixels.y_max - e.bbox_pixels.y_min)))


def screen_controls(state):
    """Expose observed app labels and state flags without inventing task progress."""
    controls = []
    # Keep informative app nodes; status-bar clocks and empty containers add noise.
    for element in state.ui_elements:
        if element.is_visible and element.package_name != "com.android.systemui" and (
                element.text or element.content_description or element.is_checkable or element.is_selected or element.is_editable or
                (element.metadata or {}).get("observed_label")):
            control = {"label": (element.metadata or {}).get("observed_label") or element.text or element.content_description or element.hint_text or element.class_name,
                "checked": element.is_checked if element.is_checkable else None,
                "selected": element.is_selected}
            if (element.is_clickable or element.is_editable) and element.bbox_pixels:
                height, width = state.pixels.shape[:2]
                box = element.bbox_pixels
                control["tap_center"] = [int((box.x_min + box.x_max) * 500 / width), int((box.y_min + box.y_max) * 500 / height)]
                control["editable"] = element.is_editable
                control["focused"] = element.is_focused
                control["clickable"] = element.is_clickable
            controls.append(control)
    return controls[:60]


def xml_controls(xml):
    """Use the official XML parser and attach nearby row text to unlabeled switches."""
    elements = representation_utils.xml_dump_to_ui_elements(xml)
    root = ET.fromstring(xml)
    parents = {child: parent for parent in root.iter() for child in parent}
    # A switch often has no text; its containing GUI row supplies the visible label.
    for node, element in zip(root.iter("node"), elements):
        # Files uses a clickable card containing a non-clickable title. Associate
        # that actual descendant text with its card, without treating headings as buttons.
        if element.is_clickable and not (element.text or element.content_description):
            children = [child for child in node.iter("node") if child.get("text")]
            for child in children:
                coordinates = [int(value) for value in re.findall(r"-?\d+", child.get("bounds", ""))]
                box = element.bbox_pixels
                # Recycled Files cards can expose another row's old title. Never
                # label a card from text that is geometrically outside that card.
                if box and len(coordinates) == 4:
                    x0, y0, x1, y1 = coordinates
                    if not (box.x_min <= x0 <= x1 <= box.x_max and box.y_min <= y0 <= y1 <= box.y_max):
                        raise ValueError("Inconsistent XML: clickable container's text is outside its bounds")
            labels = [child.get("text") for child in children]
            if labels:
                element.metadata = {**(element.metadata or {}), "observed_label": labels[0]}
        # UIAutomator omits editable; its actual standard EditText class is
        # positive evidence, unlike treating every unknown flag as false.
        if element.is_editable is None and element.class_name == "android.widget.EditText":
            element.is_editable = True
            element.metadata = {**(element.metadata or {}), "editable_from_observed_class": True}
        if not element.is_checkable or element.text or element.content_description:
            continue
        parent = parents.get(node)
        while parent is not None:
            labels = [child.get("text") for child in parent.iter("node") if child.get("text")]
            if labels:
                element.metadata = {"observed_label": " / ".join(labels[:3])}
                break
            parent = parents.get(parent)
    return elements


def control_notes(state):
    """Render actual GUI properties as concise labeled observations for the model."""
    notes = []
    # Natural-language labels prevent the model from confusing an unlabeled flag.
    for control in screen_controls(state):
        note = control["label"]
        if control["checked"] is not None:
            note += ": switch " + ("ON (checked=true)" if control["checked"] else "OFF (checked=false)")
        if control["selected"]:
            note += " (selected)"
        if control.get("editable"):
            note += " (editable, " + ("focused" if control.get("focused") else "not focused") + ")"
        elif control.get("clickable"):
            note += " (clickable)"
        if "tap_center" in control:
            note += " at observed tap center=" + json.dumps(control["tap_center"])
        notes.append(note)
    return "\n".join(notes) or "No GUI tree available; inspect the screenshot."


def no_observed_effect(before, after, threshold):
    """Require unchanged GUI labels/state as well as little pixel change."""
    # Small timer digits can change while affecting very few full-screen pixels.
    return image_difference(before, after) < threshold and screen_controls(before) == screen_controls(after)


def repeated_without_progress(action, actions, results):
    """Bound unchanged repeats/cycles; never turn a stop into model completion."""
    if action["action_type"] == "status":
        return False  # The independent verifier judges a model-issued finish.
    same = len(actions) >= 2 and all(previous == action for previous in actions[-2:]) and all(r["no_visible_effect"] for r in results[-2:])
    cycle = len(actions) >= 3 and action in actions[-3:] and all(r["no_visible_effect"] for r in results[-3:])
    return same or cycle


def assessment_text(raw):
    """Retain visible prose, discarding native operation lines without executing them."""
    answers = re.findall(r"<answer>(.*?)</answer>", raw, flags=re.DOTALL)
    visible = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    if len(answers) == 1 and not re.search(r"\b(?:do|finish)\s*\(", answers[0]):
        text = answers[0]
    else:
        text = re.sub(r"<answer>.*?</answer>", "", visible, flags=re.DOTALL)
        # AutoGLM can retain its action-trained output even in a summary request.
        # Only independent code lines are dropped; no code is parsed or dispatched.
        text = "\n".join(line for line in text.splitlines() if not re.match(r"\s*(?:do|finish)\s*\(", line))
    text = " ".join(text.split())
    if not text or len(text) > 1600 or re.search(r"\b(?:do|finish)\s*\(", text):
        raise ValueError("Expected a short read-only assessment, not an operation call")
    return text


def freshness(before, fresh, action, config):
    """Check screen/modal change and the chosen target without whole-tree equality."""
    height, width = before.pixels.shape[:2]
    global_change = image_difference(before, fresh, (0, int(height * .06), width, int(height * .94)))
    original, current = target_at(before, action), target_at(fresh, action)
    identity_keys = ("package_name", "resource_name", "resource_id", "text", "content_description", "hint_text",
                     "bbox_pixels", "is_enabled", "is_editable", "is_focused", "is_checked", "is_selected", "metadata")
    target_same = current is None if original is None else (
        current is not None and all(original.get(k) == current.get(k) for k in identity_keys))
    target_change = 0.0
    if "x" in action:
        x, y = action["x"], action["y"]
        target_change = image_difference(before, fresh, (max(0, x - 60), max(0, y - 60), min(width, x + 60), min(height, y + 60)))
    # XML can disappear while the actual screenshot remains identical. Preserve
    # screenshot fallback only for virtually unchanged scene AND target pixels.
    if (original is None) != (current is None):
        tolerance = config.get("no_effect_difference", 0.001)
        target_same = global_change <= tolerance and target_change <= tolerance
    return {"safe": target_same and global_change <= config["freshness_global_difference"] and target_change <= config["freshness_target_difference"],
            "target_identity_same": target_same, "global_image_difference": global_change,
            "target_image_difference": target_change, "selected_target_before": original, "selected_target_fresh": current}


class AutoGLMAgent(base_agent.EnvironmentInteractingAgent):
    """Capture a real screen, ask hosted AutoGLM, execute one checked action and log."""

    def __init__(self, env, output, config, scratch):
        """Keep run-local task inputs, API credentials, budgets and observed history."""
        super().__init__(env, name="autoglm_api", transition_pause=None)
        self.output, self.config, self.scratch = Path(output), config, scratch
        if config["invalid_reply_corrections"] != 1 or config["max_reobservations"] not in {0, 1}:
            raise ValueError("Use one correction and at most one fresh reobservation per step")
        self.endpoint, model, self.key = api_settings()
        if config["model"] != model:
            raise ValueError("Config model and .env model differ")
        self.history, self.calls, self.fallback_events = [], 0, []
        self.conversation = []
        self.executed_actions = []
        self.deadline = time.monotonic() + config["max_seconds"]
        self.recording_ready, self.recording_errors = None, []
        self.corrections_this_step = 0
        self.observations = 0
        self.assessment_calls = 0
        self.assessment_errors = []

    def request_model(self, messages, folder, name, step):
        """Call the same bounded API and save redacted requests/replies for either role."""
        payload = {"model": self.config["model"], "messages": messages, "stream": False, **self.config["sampling"]}
        logged = json.loads(json.dumps(payload))
        # Both action and assessment images stay on disk, not in readable API logs.
        for message in logged["messages"]:
            if isinstance(message["content"], list):
                for part in message["content"]:
                    if part.get("type") == "image_url":
                        part["image_url"]["url"] = "Saved screenshot (base64 encoded for API)"
        suffix = name.removeprefix("action_")
        request_path = folder / (f"request_{suffix}.json" if name.startswith("action_") else f"{name}_request.json")
        response_path = folder / (f"response_{suffix}.json" if name.startswith("action_") else f"{name}_response.json")
        save_json(request_path, logged)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Model time budget exhausted")
        self.calls += 1
        log_event(self.output, "MODEL REQUEST", {"call": self.calls, "role": name, "endpoint": self.endpoint,
            "request": str(request_path.relative_to(self.output))}, step)
        request = urllib.request.Request(self.endpoint + "/chat/completions", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
        started = time.monotonic()
        print(f"Step {step}, {name}, AutoGLM call {self.calls}", flush=True)
        try:
            with urllib.request.urlopen(request, timeout=min(remaining, self.config["request_timeout"])) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            details = {"http_status": error.code,
                "body": error.read().decode(errors="replace").replace(self.key, "[REDACTED]")}
            save_json(folder / f"{name}_api_error.json", details)
            log_event(self.output, "API ERROR", details, step)
            print(f"Z.ai rejected {name} (HTTP {error.code}): {details['body']}", flush=True)
            raise
        data["wall_seconds"] = time.monotonic() - started
        data = json.loads(json.dumps(data).replace(self.key, "[REDACTED]"))
        save_json(response_path, data)
        raw = data["choices"][0]["message"]["content"]
        log_event(self.output, "MODEL REPLY", raw if name.startswith("action_") else {"role": name, "reply": raw}, step)
        log_event(self.output, "MODEL TIMING", {"role": name, "wall_seconds": data["wall_seconds"], "usage": data.get("usage")}, step)
        if data.get("model") != self.config["model"]:
            raise RuntimeError("Provider returned a different model")
        if data["choices"][0]["finish_reason"] == "length":
            raise ValueError("Truncated model reply")
        return raw

    def assess_step(self, before, after, folder, goal, action, result, step):
        """Summarize observed before/after evidence without executing or forcing completion."""
        # M3A's summary template retains its agent/action prefix. The assessment
        # must know the same capabilities, while its output is still read-only.
        prompt = native_prompt(self.config["allowed_apps"])
        prompt += "\nAvailable apps: " + json.dumps(self.config["allowed_apps"]) + "\n"
        prompt += (PROJECT / "instructions/assessment.md").read_text(encoding="utf-8")
        text = f"Original goal: {goal}\nCompletion condition: {completion_condition(self.config['task_name'], self.scratch)}\n"
        inputs = {"text_to_copy":self.scratch["clipboard_content"]} if self.config['task_name'] == 'SystemCopyToClipboard' else self.scratch
        text += "Exact task inputs: " + json.dumps(inputs) + "\n"
        text += f"Dispatched action: {json.dumps(action)}\nPrevious model reply: {self.pending_reply}\n"
        text += f"Actual observed result: {json.dumps(result)}\n"
        content = [{"type": "text", "text": text}]
        # Label the two inputs in message order; save the exact resized images.
        for label, state in (("BEFORE", before), ("AFTER", after)):
            image = Image.fromarray(state.pixels)
            image.thumbnail((1280, 1280))
            path = folder / f"assessment_{label.lower()}.png"
            image.save(path)
            content += [{"type": "text", "text": f"{label} screenshot ({path.name}) and GUI properties:\n{control_notes(state)}"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")}}]
        self.assessment_calls += 1
        raw = self.request_model([{"role": "system", "content": prompt}, {"role": "user", "content": content}], folder, "assessment", step)
        summary = assessment_text(raw)
        discarded = re.findall(r"^\s*(?:do|finish)\([^\n]*", raw, flags=re.MULTILINE)
        save_json(folder / "assessment.json", {"summary": summary, "kind": "model_assessment", "verifier_feedback": False,
            "discarded_operation_lines": discarded, "operations_executed": 0})
        log_event(self.output, "STEP ASSESSMENT", {"summary": summary, "verifier_feedback": False}, step)
        return summary

    def observe(self):
        """Check successive screenshots visually; empty trees never imply a stable screen."""
        state = self.env.get_state(wait_to_stabilize=False)
        # Bound visual settling; loading remains visible to the model if it persists.
        for _ in range(self.config["visual_stability_checks"]):
            if time.monotonic() >= self.deadline:
                raise RuntimeError("Observation time budget exhausted")
            time.sleep(self.config["visual_stability_pause"])
            fresh = self.env.get_state(wait_to_stabilize=False)
            height, width = state.pixels.shape[:2]
            change = image_difference(state, fresh, (0, int(height * .06), width, int(height * .94)))
            state = fresh
            if change <= self.config["visual_stability_difference"]:
                break
        log_event(self.output, "VISUAL SETTLING", {"difference": change,
            "within_threshold": change <= self.config["visual_stability_difference"], "tree_backend": self.config["tree_backend"]}, len(self.history) + 1)
        if self.config.get("supplemental_tree_packages"):
            state = self.supplement_controls(state)
        return state

    def supplement_controls(self, state):
        """Pair a checked, unique XML dump with a visually unchanged fresh screenshot."""
        # Retrying observation is read-only; it never repeats a GUI dispatch.
        for attempt in range(1 + min(1, self.config.get("supplemental_read_retries", 0))):
            self.observations += 1
            record = {"capture": self.observations, "read_attempt": attempt, "used": False}
            try:
                activity, response = adb_utils.get_current_activity(self.env.controller)
                adb_utils.check_ok(response, "Current activity unavailable")
                record["activity"] = activity
                if not activity or activity.split("/")[0] not in self.config["supplemental_tree_packages"]:
                    return state
                xml = adb_utils.uiautomator_dump(self.env.controller, timeout_sec=8)
                path = self.output / f"ui_capture_{self.observations:03d}.xml"
                path.write_text(xml, encoding="utf-8")
                elements = xml_controls(xml)
                fresh = self.env.get_state(wait_to_stabilize=False)
                height, width = state.pixels.shape[:2]
                change = image_difference(state, fresh, (0, int(height * .06), width, int(height * .94)))
                record.update(xml=path.name, image_difference=change)
                # Reject a changing scene instead of pairing an old tree with a new image.
                if change <= self.config["visual_stability_difference"]:
                    record["used"] = True
                    return replace(fresh, ui_elements=elements)
                state = fresh
            except Exception as error:
                record["error"] = str(error)
                state = self.env.get_state(wait_to_stabilize=False)
            finally:
                log_event(self.output, "SUPPLEMENTAL GUI STATE", record, len(self.history) + 1)
        return state

    def capture(self, state, folder, step):
        """Save full observation and resized model input under a unique observation ID."""
        folder.mkdir()
        image = Image.fromarray(state.pixels)
        image.save(folder / "screen.png")
        image.thumbnail((1280, 1280))
        image.save(folder / "model_input.png")
        save_json(folder / "tree.json", [asdict(e) for e in state.ui_elements])
        log_event(self.output, "OBSERVATION", {"observation_id": str(folder.relative_to(self.output)),
            "screenshot": str((folder / "screen.png").relative_to(self.output)), "tree_used_for_model": bool(screen_controls(state))}, step)

    def ask_action(self, state, folder, goal, step):
        """Send a screenshot and exact inputs; allow one invalid-reply correction per step."""
        prompt = native_prompt(self.config["allowed_apps"])
        task_name = self.config["task_name"]
        # A benchmark parameter name can resemble current state; label the goal.
        model_inputs = {"text_to_copy": self.scratch["clipboard_content"]} if task_name == "SystemCopyToClipboard" else self.scratch
        prompt += "\nCOMPLETION CONDITION for " + task_name + ":\n" + completion_condition(task_name, self.scratch)
        prompt += f"\nAvailable apps: {json.dumps(self.config['allowed_apps'])}\n"
        if self.config.get("interaction_guidance"):
            prompt += "\n" + (PROJECT / "instructions/android_interactions.md").read_text(encoding="utf-8")
            capabilities = {name: description for name, description in self.config.get("app_capabilities", {}).items()
                            if name in self.config["allowed_apps"]}
            prompt += "\nAvailable app capabilities (environment facts): " + json.dumps(capabilities) + "\n"
        if self.config.get("task_guidance"):
            prompt += "\nTASK PROCEDURE (choose the next action from the current GUI):\n" + task_guide(task_name, self.scratch) + "\n"
        # Upstream gives the goal once; later user turns are observations of that
        # same task, not new requests to perform it again (especially one photo).
        text = f"Task: {goal}\nExact task inputs: {json.dumps(model_inputs)}\n" if not self.conversation else "Latest observation of the original task after the preceding executed action.\n"
        if self.config.get("recent_effect_context"):
            text = f"Original ongoing goal (same task; do not restart completed operations): {goal}\nExact task inputs: {json.dumps(model_inputs)}\n"
        text += f"** Screen Info ** Step {step}/{self.config['max_steps']}.\n"
        text += "Fresh observed GUI labels and state:\n" + control_notes(state) + "\n"
        if task_name == "ClockTimerEntry":
            text += timer_buffer_note(state) + "\n"
        if self.history:
            if self.config.get("recent_effect_context"):
                text += "Recent dispatched actions and actual observed results (oldest first, not proof of task success): " + json.dumps(self.history[-self.config["recent_actions"]:]) + "\n"
            else:
                text += "Actual observed result of last action: " + json.dumps(self.history[-1]) + "\n"
        text += "Check the original completion condition before acting; finish when it is satisfied."
        image = base64.b64encode((folder / "model_input.png").read_bytes()).decode("ascii")
        messages = [{"role": "system", "content": prompt}, *self.conversation, {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}}, {"type": "text", "text": text}]}]
        # A correction only repairs unexecuted data; HTTP/execution errors never replay.
        for attempt in range(2 - self.corrections_this_step):
            raw = ""  # A truncated transport reply can fail before returning text.
            try:
                raw = self.request_model(messages, folder, f"action_{attempt}", step)
                fields = parse_action(raw)
                action = convert_action(fields, state, self.config["allowed_apps"])
                calls = [line.strip() for line in raw.splitlines() if re.match(r"\s*(do|finish)\(", line)]
                if len(calls) > 1 and len(set(calls)) == 1:
                    log_event(self.output, "IDENTICAL CALLS COLLAPSED", {"copies": len(calls), "decisions": 1, "executions_at_most": 1}, step)
                self.pending_user, self.pending_reply = text, raw
                return fields, action
            except ValueError as error:
                save_json(folder / f"validation_error_{attempt}.json", {"error": str(error), "executed": False})
                log_event(self.output, "VALIDATION ERROR", {"error": str(error), "executed": False}, step)
                if self.corrections_this_step:
                    raise
                self.corrections_this_step += 1
                messages += [{"role": "assistant", "content": raw}, {"role": "user", "content":
                    f'Invalid action: {error}. Return one corrected action. No action executed. '
                    'If you intend to finish, the syntax is finish(message="Task completed.") as a standalone call, outside do.'}]

    def step(self, goal):
        """Make one decision/action; recapture once if an unexecuted target became stale."""
        step = len(self.history) + 1
        folder = self.output / f"step_{step:03d}"
        folder.mkdir()
        self.corrections_this_step = 0
        state = self.observe()
        # One bounded reobservation replaces stale choices before any dispatch.
        for observation in range(1 + self.config["max_reobservations"]):
            observed = folder / f"observation_{observation}"
            self.capture(state, observed, step)
            fields, action = self.ask_action(state, observed, goal, step)
            save_json(folder / "action.json", {"native": fields, "android": action, "observation_id": observed.name})
            if action["action_type"] not in {"click", "long_press", "input_text", "slide"}:
                break
            fresh = self.observe()
            self.capture(fresh, folder / f"freshness_{observation}", step)
            check = freshness(state, fresh, action, self.config)
            save_json(observed / "freshness.json", check)
            log_event(self.output, "TARGET FRESHNESS", check, step)
            if check["safe"]:
                state = fresh
                break
            if observation == self.config["max_reobservations"]:
                raise RuntimeError("Target changed twice; no action executed")
            log_event(self.output, "REOBSERVE", {"reason": "Unexecuted target changed", "old_action_discarded": True}, step)
            state = fresh
        if time.monotonic() >= self.deadline:
            raise RuntimeError("Run deadline reached before dispatch")
        if self.recording_ready is not None and (not self.recording_ready.wait(15) or self.recording_errors):
            raise RuntimeError("Recording unavailable; no action executed")
        if repeated_without_progress(action, self.executed_actions, self.history):
            raise RuntimeError("Repeated action without visible effect; stopping")
        save_json(folder / "execution_start.json", {"action": action, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        log_event(self.output, "EXECUTION START", action, step)
        print("Chosen:", action, flush=True)
        started = time.monotonic()
        selected = target_at(state, action)
        if action["action_type"] == "open_app" and action["app_name"] == "chrome" and self.config.get("chrome_launch_timeout"):
            timeout = min(self.config["chrome_launch_timeout"], self.deadline - time.monotonic())
            launched = launch_chrome_once(timeout)
            save_json(folder / "chrome_launch.json", {"attempts": 1, "timeout": timeout,
                "returncode": launched.returncode, "output": launched.stdout.decode(errors="replace"),
                "automatic_retry": False})
        elif action["action_type"] == "slide":
            adb_utils.check_ok(adb_utils.issue_generic_request(adb_utils.generate_swipe_command(*action["start"], *action["end"]), self.env.controller), "Swipe failed")
        elif action["action_type"] == "wait":
            time.sleep(action["seconds"])
        elif action["action_type"] == "input_text":
            if self.config.get("text_input_backend") == "adb_keyboard":
                type_with_adb_keyboard(action["text"], min(30, self.deadline - time.monotonic()), folder)
            else:
                type_without_submit(action["text"], self.env.controller)
        elif action["action_type"] != "status":
            self.env.execute_action(json_action.JSONAction(**action))
        after = self.observe()
        Image.fromarray(after.pixels).save(folder / "after.png")
        save_json(folder / "after_tree.json", [asdict(e) for e in after.ui_elements])
        changed = image_difference(state, after)
        # Past coordinates are excluded from model history; latest screenshot grounds anew.
        semantic = {key: value for key, value in fields.items() if key not in {"element", "start", "end"}}
        result = {"action": semantic, "no_visible_effect": no_observed_effect(state, after, self.config["no_effect_difference"]),
            "image_difference": changed, "dispatch_returned": action["action_type"] != "status",
            "visible_fields_after": [{"hint": e.hint_text, "text": e.text} for e in after.ui_elements if e.is_visible and e.is_editable],
            "execute_and_observe_seconds": time.monotonic() - started}
        if selected:
            result["selected_gui_control"] = {"label": (selected.get("metadata") or {}).get("observed_label")
                or selected.get("text") or selected.get("content_description") or selected.get("class_name"),
                "resource_id": selected.get("resource_id")}
        self.history.append(result)
        self.executed_actions.append(action)
        # Keep native executed decisions, removing old images as upstream does.
        # Failed validation, discarded stale choices and uncertain dispatches
        # never enter the executed conversation; original replies stay on disk.
        self.conversation += [{"role": "user", "content": self.pending_user},
                              {"role": "assistant", "content": self.pending_reply}]
        save_json(folder / "result.json", result)
        log_event(self.output, "OBSERVED RESULT", result, step)
        # Preserve dispatch evidence before any extra API call can fail. A finish
        # still belongs to the action model; this experiment adds no finish gate.
        if self.config.get("step_assessment") and action["action_type"] != "status":
            try:
                result["model_assessment"] = self.assess_step(state, after, folder, goal, action, result, step)
            except Exception as error:
                failure = {"step":step, "error":str(error).replace(self.key, "[REDACTED]"),
                    "phase":"assessment", "action_already_dispatched":True, "automatic_replay":False}
                self.assessment_errors.append(failure)
                save_json(folder / "assessment_error.json", failure)
                log_event(self.output, "ASSESSMENT ERROR", failure, step)
                raise
            save_json(folder / "result.json", result)
        return base_agent.AgentInteractionResult(done=action["action_type"] == "status", data={"action": action})
