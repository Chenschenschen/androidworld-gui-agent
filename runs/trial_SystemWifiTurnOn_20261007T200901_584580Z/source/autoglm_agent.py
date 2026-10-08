"""One screenshot → AutoGLM → checked Android World action loop.

Protocol adapted from zai-org/Open-AutoGLM's English prompt, model client and
action handler. Pseudo-calls are parsed as data with AST, never executed as code.
The existing GELab file and recorded runs remain available as historical evidence.
"""

import ast
import base64
from dataclasses import asdict
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

from android_world.agents import base_agent
from android_world.env import adb_utils, json_action
from PIL import Image, ImageChops, ImageStat

from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent


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


def parse_action(raw):
    """Accept exactly one allowlisted pseudo-call containing only literal keywords."""
    if "<answer>" in raw:
        answers = re.findall(r"<answer>(.*?)</answer>", raw, flags=re.DOTALL)
        if len(answers) != 1:
            raise ValueError("Expected one complete answer block")
        body = answers[0].strip()
    else:
        # Native newer replies may omit tags; only their final action line counts.
        lines = [line.strip() for line in raw.splitlines() if re.match(r"\s*(do|finish)\(", line)]
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
    except (SyntaxError, TypeError) as error:
        raise ValueError("Malformed action syntax") from error
    return {"command": node.func.id, **values}


def pixel_point(point, state):
    """Convert AutoGLM's normalized 0..1000 integers into bounded screen pixels."""
    if not isinstance(point, list) or len(point) != 2 or any(type(v) is not int or not 0 <= v <= 1000 for v in point):
        raise ValueError("Coordinates must be two integers in 0..1000")
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
        if not isinstance(app, str) or app.lower() not in allowed_apps:
            raise ValueError("Launch must use an app available for this task")
        return {"action_type": "open_app", "app_name": app.lower()}
    if name == "Wait":
        duration = fields["duration"]
        if isinstance(duration, str) and re.fullmatch(r"\d+(?:\.\d+)? seconds?", duration):
            duration = float(duration.split()[0])
        if type(duration) not in {int, float} or not 0 <= duration <= 5:
            raise ValueError("Wait duration must be 0..5 seconds")
        return {"action_type": "wait", "seconds": duration}
    return {"action_type": "navigate_back" if name == "Back" else "navigate_home"}


def image_difference(before, after, box=None):
    """Measure normalized grayscale change in a screen region, ignoring no pixels implicitly."""
    images = [Image.fromarray(state.pixels).convert("L") for state in (before, after)]
    if images[0].size != images[1].size:
        return 1.0
    if box:
        images = [image.crop(box) for image in images]
    images = [image.resize((64, 128)) for image in images]
    return ImageStat.Stat(ImageChops.difference(*images)).mean[0] / 255


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


def freshness(before, fresh, action, config):
    """Check screen/modal change and the chosen target without whole-tree equality."""
    height, width = before.pixels.shape[:2]
    global_change = image_difference(before, fresh, (0, int(height * .06), width, int(height * .94)))
    original, current = target_at(before, action), target_at(fresh, action)
    identity_keys = ("package_name", "resource_name", "resource_id", "text", "content_description", "hint_text",
                     "bbox_pixels", "is_enabled", "is_editable", "is_focused", "is_checked", "is_selected")
    target_same = original is None or (current is not None and all(original.get(k) == current.get(k) for k in identity_keys))
    target_change = 0.0
    if "x" in action:
        x, y = action["x"], action["y"]
        target_change = image_difference(before, fresh, (max(0, x - 60), max(0, y - 60), min(width, x + 60), min(height, y + 60)))
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
        self.executed_actions = []
        self.deadline = time.monotonic() + config["max_seconds"]
        self.recording_ready, self.recording_errors = None, []
        self.corrections_this_step = 0

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
            "screenshot": str((folder / "screen.png").relative_to(self.output)), "tree_used_for_model": False}, step)

    def ask_action(self, state, folder, goal, step):
        """Send a screenshot and exact inputs; allow one invalid-reply correction per step."""
        prompt = (PROJECT / "instructions/autoglm.md").read_text(encoding="utf-8")
        recent = self.history[-self.config["recent_actions"]:]
        text = f"Task: {goal}\nExact task inputs: {json.dumps(self.scratch)}\nAvailable apps: {json.dumps(self.config['allowed_apps'])}\n"
        text += f"Recent executed actions and observed results: {json.dumps(recent)}\nStep {step}/{self.config['max_steps']}. Current screenshot attached."
        image = base64.b64encode((folder / "model_input.png").read_bytes()).decode("ascii")
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}}, {"type": "text", "text": text}]}]
        # A correction only repairs unexecuted data; HTTP/execution errors never replay.
        for attempt in range(2 - self.corrections_this_step):
            payload = {"model": self.config["model"], "messages": messages, "stream": False, **self.config["sampling"]}
            logged = json.loads(json.dumps(payload))
            logged["messages"][1]["content"][0]["image_url"]["url"] = "model_input.png (base64 encoded for API)"
            save_json(folder / f"request_{attempt}.json", logged)
            self.calls += 1
            log_event(self.output, "MODEL REQUEST", {"call": self.calls, "endpoint": self.endpoint,
                "request": str((folder / f"request_{attempt}.json").relative_to(self.output))}, step)
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Model time budget exhausted")
            request = urllib.request.Request(self.endpoint + "/chat/completions", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
            start = time.monotonic()
            print(f"Step {step}, screenshot, AutoGLM call {self.calls}", flush=True)
            try:
                with urllib.request.urlopen(request, timeout=min(remaining, self.config["request_timeout"])) as response:
                    data = json.load(response)
            except urllib.error.HTTPError as error:
                save_json(folder / f"api_error_{attempt}.json", {"http_status": error.code,
                    "body": error.read().decode(errors="replace").replace(self.key, "[REDACTED]")})
                raise
            data["wall_seconds"] = time.monotonic() - start
            # Keep provider-visible replies and usage, never the Authorization header.
            data = json.loads(json.dumps(data).replace(self.key, "[REDACTED]"))
            save_json(folder / f"response_{attempt}.json", data)
            raw = data["choices"][0]["message"]["content"]
            log_event(self.output, "MODEL REPLY", raw, step)
            log_event(self.output, "MODEL TIMING", {"wall_seconds": data["wall_seconds"], "usage": data.get("usage")}, step)
            try:
                if data.get("model") != self.config["model"]:
                    raise RuntimeError("Provider returned a different model")
                if data["choices"][0]["finish_reason"] == "length":
                    raise ValueError("Truncated model reply")
                fields = parse_action(raw)
                return fields, convert_action(fields, state, self.config["allowed_apps"])
            except ValueError as error:
                save_json(folder / f"validation_error_{attempt}.json", {"error": str(error), "executed": False})
                log_event(self.output, "VALIDATION ERROR", {"error": str(error), "executed": False}, step)
                if self.corrections_this_step:
                    raise
                self.corrections_this_step += 1
                messages += [{"role": "assistant", "content": raw}, {"role": "user", "content": f"Invalid action: {error}. Return one corrected action. No action executed."}]

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
                break
            if observation == self.config["max_reobservations"]:
                raise RuntimeError("Target changed twice; no action executed")
            log_event(self.output, "REOBSERVE", {"reason": "Unexecuted target changed", "old_action_discarded": True}, step)
            state = fresh
        if time.monotonic() >= self.deadline:
            raise RuntimeError("Run deadline reached before dispatch")
        if self.recording_ready is not None and (not self.recording_ready.wait(15) or self.recording_errors):
            raise RuntimeError("Recording unavailable; no action executed")
        if len(self.history) >= 2 and all(a == action for a in self.executed_actions[-2:]) and all(r["no_visible_effect"] for r in self.history[-2:]):
            raise RuntimeError("Repeated action without visible effect; stopping")
        save_json(folder / "execution_start.json", {"action": action, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        log_event(self.output, "EXECUTION START", action, step)
        print("Chosen:", action, flush=True)
        started = time.monotonic()
        if action["action_type"] == "slide":
            adb_utils.check_ok(adb_utils.issue_generic_request(adb_utils.generate_swipe_command(*action["start"], *action["end"]), self.env.controller), "Swipe failed")
        elif action["action_type"] == "wait":
            time.sleep(action["seconds"])
        elif action["action_type"] != "status":
            self.env.execute_action(json_action.JSONAction(**action))
        after = self.observe()
        Image.fromarray(after.pixels).save(folder / "after.png")
        save_json(folder / "after_tree.json", [asdict(e) for e in after.ui_elements])
        changed = image_difference(state, after)
        # Past coordinates are excluded from model history; latest screenshot grounds anew.
        semantic = {key: value for key, value in fields.items() if key not in {"element", "start", "end"}}
        result = {"action": semantic, "no_visible_effect": changed < self.config["no_effect_difference"],
            "image_difference": changed, "dispatch_returned": action["action_type"] != "status",
            "visible_fields_after": [{"hint": e.hint_text, "text": e.text} for e in after.ui_elements if e.is_visible and e.is_editable],
            "execute_and_observe_seconds": time.monotonic() - started}
        self.history.append(result)
        self.executed_actions.append(action)
        save_json(folder / "result.json", result)
        log_event(self.output, "OBSERVED RESULT", result, step)
        return base_agent.AgentInteractionResult(done=action["action_type"] == "status", data={"action": action})
