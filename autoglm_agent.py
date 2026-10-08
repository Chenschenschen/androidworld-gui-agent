"""One screenshot → AutoGLM → checked Android World action loop.

Protocol adapted from zai-org/Open-AutoGLM's English prompt, model client and
action handler. Pseudo-calls are parsed as data with AST, never executed as code.
The existing GELab file and recorded runs remain available as historical evidence.
"""

import ast
import base64
from dataclasses import asdict, replace
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from android_world.agents import base_agent
from android_world.env import adb_utils, json_action, representation_utils
import numpy as np
from PIL import Image, ImageChops, ImageStat

from probe_connection import save_json
from trajectory import log_event

PROJECT = Path(__file__).resolve().parent

# Visible completion criteria, not fixed coordinates, action replays or verifier
# results. The model decides from the latest screenshot and supplied GUI state.
COMPLETION_RULES = {
    "SystemWifiTurnOn": "Wi-Fi in Settings is ON (checked=true). A network connection is not required. Finish when this observed state holds.",
    "CameraTakePhoto": "Exactly one new photo has been captured: one shutter action in the executed history and a new captured-photo thumbnail or preview in the GUI. Finish when both hold; launching Camera alone is insufficient.",
    "ClockTimerEntry": "Timer displays the exact requested hours, minutes and seconds, with Start available and the timer not running. Finish when that visible state holds; do not start it.",
    "ContactsAddContact": "The saved contact view shows the exact requested full name and phone number after Save. A filled unsaved form is insufficient. Finish on the saved result.",
    "SystemCopyToClipboard": "The exact requested text has been fully selected and copied through the visible Copy command; the selection menu has closed afterwards. Finish on that observed result. A transient clipboard chip or toast is optional. The task input is text to copy, not current clipboard state. Clipper is verifier infrastructure.",
    "SimpleCalendarAddOneEvent": "Simple Calendar Pro shows a saved event with the exact requested title and description, on the requested date, starting at the requested hour and lasting the requested minutes. A filled unsaved event editor is insufficient. Finish on the saved result.",
    "OsmAndTrack": "OsmAnd has saved a track whose route passes through every requested waypoint, in the listed order, each at the exact named place. An unsaved route, or one that misses or reorders a waypoint, is insufficient. Finish on the saved-track result.",
}


def launch_name(app, allowed_apps):
    """Resolve a model Launch name to one allowed app.

    Matching ignores case, spaces, '-', '_' and '~', like the alias table in
    upstream Open-AutoGLM (phone_agent/config/apps.py). The multilingual model
    sometimes translates an app name into Chinese (two different translations of
    "Simple Calendar Pro" were recorded), so a non-Latin name resolves only when
    exactly one app is allowed. An unlisted Latin-script name is never guessed.
    """
    key = re.sub(r"[\s\-_~]", "", app.lower())
    for allowed in allowed_apps:
        if key == re.sub(r"[\s\-_~]", "", allowed):
            return allowed
    if not app.isascii() and len(allowed_apps) == 1:
        return allowed_apps[0]
    return None


def skill_text(config, task_name, inputs):
    """Return the task's optional Skill (procedural app knowledge) for the prompt, or "".

    Course D2 pattern: a Skill file is loaded only when its trigger matches,
    here the task name in config["task_skills"]. Disabled when the map is empty.
    For waypoint tasks it also lists each given waypoint's search term (the
    name before the comma): the model typed "Planken, Liechtenstein"
    literally and found only the country (trial OsmAndTrack_20261008T125841).
    """
    path = config.get("task_skills", {}).get(task_name)
    if not path:
        return ""
    text = f"\nSKILL for {task_name} (app procedure):\n" + (PROJECT / path).read_text(encoding="utf-8")
    if inputs.get("waypoints"):
        terms = "\n".join(f'{number}. "{waypoint.split(",")[0].strip()}"' for number, waypoint in enumerate(inputs["waypoints"], 1))
        text += "\nSearch terms for this task's waypoints, in the required order (type exactly these):\n" + terms + "\n"
    return text


def reported_route_points(reply):
    """Return the last "points: N" the model read from the route panel, or None."""
    counts = re.findall(r"points:\s*(\d+)", reply)
    return int(counts[-1]) if counts else None


def favorite_save(reply, action):
    """True when the model is about to save OsmAnd's Favorite dialog (not a route point).

    The model saved Favorites repeatedly although the reminder forbids it
    (final seed 43, trial _154334). It names the dialog in its own reply.
    """
    return (action["action_type"] == "click" and re.search(r"\b(Add|Edit) Favorite\b", reply, re.IGNORECASE) is not None
            and re.search(r"\bSave\b", reply) is not None)


SETTLEMENT = re.compile(r"^(Village|Hamlet|Town|City)\b")


def element_id(element):
    """Forwarder trees fill resource_name; UIAutomator XML fills resource_id (v54 seed 8 missed the search field)."""
    return element.resource_name or element.resource_id or ""


def search_busy(elements):
    """True while OsmAnd's search progress spinner is on screen (only visible in a GUI tree)."""
    return any(e.is_visible and element_id(e).endswith(":id/searchProgressBar") for e in elements or [])


def thin_tree(elements):
    """True when the tree names at most one app control: the forwarder shows OsmAnd's Plan a route screen as just "Map"."""
    named = [e for e in elements or [] if e.is_visible and (e.text or e.content_description)
             and e.package_name != "com.android.systemui" and "inputmethod" not in (e.package_name or "")]
    return len(named) <= 1


def osmand_view(elements):
    """Read OsmAnd's screen from the GUI tree: route count, dialogs and search rows with their types.

    Layout recorded with the accessibility forwarder: a result row is a name
    label with its type label ("Village • ...", "Guidepost") directly below it.
    """
    visible = [e for e in elements if e.is_visible and e.bbox_pixels and e.text]
    texts = {e.text for e in visible}
    route = next((e.bbox_pixels for e in elements if e.is_visible and element_id(e).endswith("map_route_info_button")), None)
    view = {"points": None, "route_button": route, "favorite_dialog": bool(texts & {"Add Favorite", "Edit Favorite"}),
            "place_card": {"Actions", "Marker", "Share"} <= texts, "rows": [], "boxes": {}}
    for e in visible:
        match = re.search(r"points:\s*(\d+)", e.text)
        if match:
            view["points"] = int(match[1])
        view["boxes"].setdefault(e.text, e.bbox_pixels)
    # Result rows exist only on the search screen; on the route panel the date and title formed a false row
    # whose span covered Done, and the row check refused Done at points: 2 of 2 (v57 seed 8).
    searching = any(element_id(e).endswith("searchEditText") for e in elements if e.is_visible)
    for name in visible if searching else []:
        for kind in visible:
            if (kind is not name and kind.bbox_pixels.x_min == name.bbox_pixels.x_min
                    and abs(kind.bbox_pixels.y_min - name.bbox_pixels.y_max) <= 4 and not re.search(r"\d+(\.\d+)? (mi|km)$", kind.text)):
                view["rows"].append({"name": name.text, "type": kind.text, "settlement": bool(SETTLEMENT.match(kind.text)),
                                     "top": name.bbox_pixels.y_min, "bottom": kind.bbox_pixels.y_max,
                                     "center": ((name.bbox_pixels.x_min + name.bbox_pixels.x_max) // 2, (name.bbox_pixels.y_min + name.bbox_pixels.y_max) // 2)})
    return view


def osmand_tree_check(view, action, shape, route_points, searched_next):
    """Return a correction for an OsmAnd tap that the real screen shows to be wrong, else None.

    Replaces v46-v48's checks on the model's words: those were bypassed when a
    corrected reply carried no text (practice batch eval_batch_20261008T155849).
    `shape` is the screenshot's (height, width) for normalised tap centres.
    """
    if action["action_type"] != "click":
        return None
    x, y = action["x"], action["y"]
    inside = lambda box, pad_x=0, pad_up=0, pad_down=0: (box is not None and box.x_min - pad_x <= x <= box.x_max + pad_x
                                                        and box.y_min - pad_up <= y <= box.y_max + pad_down)
    boxes = view["boxes"]
    if inside(view.get("route_button")):
        return ("Route opens navigation directions, which save no track. Tap Search (the magnifier), find the first waypoint, "
                "then use its place card's Actions > Plan a route.")
    if inside(boxes.get("SHOW ON MAP")):
        return ("SHOW ON MAP only moves the map; it never opens a place. If the search shows 'Could not find anything', "
                "tap INCREASE SEARCH RADIUS; when the place row appears, tap that row.")
    if view["favorite_dialog"] and inside(boxes.get("Save")):
        return "This dialog saves a Favorite, which is not a route point. Tap Cancel (or press Back), then use Actions > Plan a route."
    # v60 seed 7: on the second waypoint's card the model chose Actions > Plan a route, which starts a new route.
    if route_points >= 1 and ((view["place_card"] and inside(boxes.get("Actions")))
                              or ("Directions from" in boxes and inside(boxes.get("Plan a route")))):
        return (f"The route already has {route_points} point(s); Plan a route here would start a new route. Press Back until the route "
                "panel shows, then tap its Add (the map stays centred on this place).")
    if view["place_card"] and inside(boxes.get("Add"), 60, 90, 10):
        return ("The place card's Add saves a Favorite, not a route point. For the first waypoint tap Actions, then Plan a route; "
                "for a later waypoint press Back until the route panel shows 'points: N' and tap that panel's Add.")
    height, width = shape
    for row in view["rows"]:
        # The country row is the Skill's region step (v51 seed 8 had it refused).
        if row["top"] <= y <= row["bottom"] and not row["settlement"] and not row["type"].startswith("Country"):
            good = [r for r in view["rows"] if r["settlement"]]
            if good:
                cx, cy = good[0]["center"]
                kind = lambda r: r["type"].split(" •")[0]
                return (f"This row is a {kind(row)}, not the place itself. Tap the {kind(good[0])} row "
                        f"\"{good[0]['name']}\" at tap center [{cx * 1000 // width}, {cy * 1000 // height}].")
            return ("This row is not the place itself (a Village, Hamlet or Town row). If that row is not listed, scroll the results down, "
                    "or tap INCREASE SEARCH RADIUS when the search found nothing.")
    if route_points >= 1 and not searched_next and view["points"] is not None and inside(boxes.get("Add"), 60, 90, 10):
        return ("Add only adds the point under the map centre, which still shows the previous waypoint. First tap the Search "
                "(magnifier) button, the second round button at the top left (the first, a globe, is Configure map), search the next waypoint, open its row, press Back here, then tap Add.")
    return None


def osmand_rule_break(reply, action):
    """Return a correction when an action breaks a Skill rule the model kept breaking, else None.

    Recorded repeatedly: tapping the plain "SHOW ON MAP" row on an empty result
    (the map jumps elsewhere; trials _154334, _154913, _155302) and typing the
    full "Name, Region" text, which finds only the country.
    """
    if action["action_type"] == "click" and re.search(r"\bSHOW ON MAP\b", reply):
        return ("SHOW ON MAP only moves the map; it never opens a place. If the search shows 'Could not find anything', "
                "tap INCREASE SEARCH RADIUS; when the place row appears, tap that row.")
    if action["action_type"] == "input_text" and "," in action["text"]:
        return f'Type only the search term before the comma: "{action["text"].split(",")[0].strip()}".'
    return None


def osmand_next_step(elements, terms, route_points, centred_on, shape):
    """The Skill's procedure as code: the next step for the observed OsmAnd screen (v53).

    v49-v52 gave the procedure as text plus checks; the model still lost its
    place between screens (it retyped searches, which resets the radius, and
    tapped remembered coordinates). Screens are recognised by labels and
    resource names recorded in those runs. Returns (hint or None, name of a
    waypoint whose place card is open in route mode, else None).
    """
    height, width = shape
    seen = [e for e in elements if e.is_visible and e.bbox_pixels and (e.text or e.content_description)]
    find = lambda pattern: next((e for e in seen if any(v and re.fullmatch(pattern, v.strip()) for v in (e.text, e.content_description))), None)
    by_id = lambda suffix: next((e for e in elements if e.is_visible and element_id(e).endswith(suffix)), None)
    def tap(e, label=None):
        b = e.bbox_pixels
        return f'Tap "{label or e.text or e.content_description}" at tap center [{(b.x_min + b.x_max) * 500 // width}, {(b.y_min + b.y_max) * 500 // height}].'
    view = osmand_view(elements)
    total = len(terms)
    term = terms[min(route_points, total - 1)]
    if view["favorite_dialog"] or find(r"Exit without saving\?"):
        cancel = find("Cancel")
        return (tap(cancel) + " This dialog is not part of the route." if cancel else "Press Back."), None
    if find("Directions from") and find("Plan a route"):
        return tap(find("Plan a route")) + f' This starts the route at "{terms[0]}" (points: 1).', None
    if view["place_card"]:  # checked before the route panel it can cover (v56 seed 8)
        name, kind = by_id("context_menu_line1"), by_id("context_menu_line2")
        name, kind = (name.text or "").strip() if name else "", (kind.text or "") if kind else ""
        if name != term or not SETTLEMENT.match(kind):
            return f'This card is not the place "{term}" (a Village, Hamlet or Town). Press Back and choose the place row.', None
        if route_points == 0:
            return tap(find("Actions")) + ' Then choose "Plan a route".', None
        return f'Press Back until the route panel ("points: {route_points}", Add, Done) is shown; the map stays centred on "{name}".', name
    if view["points"] is not None:
        n = view["points"]
        if n >= total:
            done = find("Done")
            return (tap(done) + f" All {total} waypoints are in the route; Done saves the track." if done else None), None
        if centred_on == terms[n] and not find(r"0 (ft|m) •.*"):
            add = find("Add")
            return (tap(add) + f' The map is centred on "{terms[n]}"; Add makes it point {n + 1}.' if add else None), None
        search = find("Search")
        return (tap(search) + f' (the magnifier) to look up the next waypoint "{terms[n]}".' if search else None), None
    field = by_id("searchEditText")
    if field is not None:
        # Once its card was seen the map is there; Back passes the street list again (v58 seed 8 looped SHOW/Back).
        if route_points and centred_on == term:
            return f'Press Back until the route panel is shown; the map is centred on "{term}".', None
        show = find(f"SHOW {re.escape(term.upper())} ON THE MAP")
        if show:
            return tap(show) + f' This selects "{term}" itself.', None
        typed = "" if field.text in (None, "", field.hint_text) else field.text.strip()
        if typed != term:
            clear = find("Clear")
            if typed and clear:
                return tap(clear) + f' Then type "{term}".', None
            return f'Type "{term}" (only the place name).', None
        row = next((r for r in view["rows"] if r["settlement"] and r["name"] == term), None)
        if row:
            return (f'Tap the {row["type"].split(" •")[0]} row "{term}" at tap center '
                    f'[{row["center"][0] * 1000 // width}, {row["center"][1] * 1000 // height}].'), None
        # At the end of the list INCREASE SEARCH RADIUS restarts the search from the top (v61 seed 31 kept swiping there).
        radius = find("INCREASE SEARCH RADIUS")
        if radius:
            return tap(radius) + " Repeat until the place row appears; do not retype the text (that resets the radius).", None
        if view["rows"]:
            # A manual search for "Malbun" listed nine same-name rows (streets, ski lifts, hotels) before its Village row.
            return ('The place row is further down. Scroll the results: do(action="Swipe", start=[500, 560], end=[500, 260]). '
                    "Do not retype the text."), None
        return "Wait for the results.", None
    search = find("Search")
    if search and route_points == 0:
        return tap(search) + f' (the magnifier) to look up "{terms[0]}".', None
    if route_points >= total:
        return "All waypoints were added and Done was tapped: the track is saved. Finish.", None
    return None, None


def route_add_too_early(reply, action, route_points, searched_next):
    """True when the model taps the route panel's Add before searching the next waypoint.

    Add places the map centre, which still shows the previous waypoint. Twice
    the model reached points: 1 and then tapped Add expecting a search,
    despite the reminder (trials _153947, _154913).
    """
    return (route_points >= 1 and not searched_next and action["action_type"] == "click"
            and re.search(r'"Add"|\bAdd button\b', reply) is not None
            and re.search(r"route panel|points:\s*\d", reply, re.IGNORECASE) is not None)


def skill_reminder(config, task_name, inputs, route_points=0):
    """One status line per step that restates the Skill's search terms (D2 status bar).

    The Skill in the system prompt alone was not followed: trial
    OsmAndTrack_20261008T131512 still typed "Planken, Liechtenstein", and
    _131754 tapped SHOW ON MAP on an empty result instead of widening it.
    `route_points` is the last route-panel count the model reported; code keeps
    it so the line can say which waypoint comes next (trial _154334 searched
    the second waypoint before the first was in a route).
    """
    if not config.get("task_skills", {}).get(task_name) or not inputs.get("waypoints"):
        return ""
    names = [waypoint.split(",")[0].strip() for waypoint in inputs["waypoints"]]
    if route_points <= 0:
        progress = (f'Route progress (from the last "points: N" you reported): 0 of {len(names)}. The first waypoint is not in a '
                    f'route yet: open "{names[0]}"\'s place card and choose Actions > Plan a route. ')
    elif route_points < len(names):
        progress = f'Route progress: {route_points} of {len(names)}. Next waypoint: {route_points + 1}. "{names[route_points]}". '
    else:
        progress = f"Route progress: {route_points} of {len(names)}: all waypoints are in the route, tap Done to save the track. "
    terms = " ".join(f'{number}. "{name}"' for number, name in enumerate(names, 1))
    # v44-v52 asked to open the region first; the model never completed that step, so v55 drops it (as the Skill file did in v53).
    start = ""
    # The last three rules answer the v42 final-evaluation failures: a same-name
    # guidepost chosen, a Favorite saved three times, searches switched too early.
    return (f"Skill reminder: {progress}{start}Type only the search term, never the full waypoint text. Search terms in order: {terms}. "
            "If the search shows 'Could not find anything', tap INCREASE SEARCH RADIUS (not SHOW ON MAP) until the place row appears, then tap that row. "
            "Choose only a row whose type is Village, Hamlet or Town, never a guidepost, station, stop or street. "
            "Never tap the star 'Add' on a place card: it saves a Favorite. First waypoint: Actions > Plan a route. "
            # Trial _153947 reached points: 1, then tapped the panel's Add expecting a search.
            "Add never searches: it only adds the point under the map centre. For each later waypoint, in this order: "
            "tap the Search (magnifier) button, the second round button at the top left (the first, a globe, is Configure map), clear the old text, type the term, tap the place's row, "
            "press Back until the route panel shows 'points: N', and only then tap that panel's Add once. "
            "Finish the current waypoint before searching the next.\n")


def text_field_focused(controller):
    """Ask Android whether a text field holds the input connection (needs no GUI tree).

    Without a GUI tree the adapter's focus check cannot run: trial
    OsmAndTrack_20261008T134852 typed "Balzers" into an unfocused page and the
    text vanished. The input-method dump names the focused view's class.
    """
    response = adb_utils.issue_generic_request(["shell", "dumpsys", "input_method"], controller)
    served = re.findall(r"mServedView=([^\s}]+)", response.generic.output.decode("utf-8", errors="replace"))
    return any(re.search(r"EditText|AutoComplete|TextInput", view) for view in served)


def history_window(conversation, turns):
    """Keep the first executed turn (it carries the task goal) and the latest turns.

    Course D1 p.40: keep the latest observation, drop what no longer matters.
    An 88-step OsmAnd run exceeded the provider's prompt limit (HTTP 400
    "Prompt exceeds max length", trial OsmAndTrack_20261008T125841). The full
    history stays on disk in every step's request file.
    """
    if len(conversation) <= 2 * turns:
        return conversation
    return conversation[:2] + conversation[-2 * (turns - 1):]


def launch_app(app_name, controller, timeout_sec=30):
    """Launch like Android World's launch_app, but give `am start -W` time to finish.

    Android World waits only 5 seconds. A cold OsmAnd start on the software-
    rendered emulator took longer; android_env then restarted the ADB server,
    which also ended the screen recorder (batch eval_batch_20261008T113903).
    URI-launched apps (for example Contacts) keep the upstream path.
    """
    activity = None if app_name in adb_utils._DEFAULT_URIS else adb_utils.get_adb_activity(app_name)
    if activity is None:
        return adb_utils.launch_app(app_name, controller)
    adb_utils.check_ok(adb_utils.start_activity(activity, [], controller, timeout_sec=timeout_sec), f"Launch {app_name} failed")


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
        raise ValueError("Coordinates must be two point integers or four box integers in 0..1000")
    if len(point) == 4:
        if point[0] >= point[2] or point[1] >= point[3]:
            raise ValueError("Bounding box must have ordered, nonzero width and height")
        # This is geometric grounding of the model's own region, not a new decision.
        point = [(point[0] + point[2]) / 2, (point[1] + point[3]) / 2]
    height, width = state.pixels.shape[:2]
    return min(width - 1, int(point[0] * width / 1000)), min(height - 1, int(point[1] * height / 1000))


def convert_action(fields, state, allowed_apps, focus_check=None):
    """Validate action-specific fields and convert to Android World's fixed actions.

    `focus_check` answers "is a text field focused?" when the GUI tree reports no
    focus at all: the accessibility forwarder marks OsmAnd's focused search field
    unfocused (probe, 8 October 2026).
    """
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
        if (state.ui_elements and not any(e.is_visible and e.is_editable and e.is_focused for e in state.ui_elements)
                and not (focus_check and focus_check())):
            raise ValueError("No focused editable field; tap the real field first")
        return {"action_type": "input_text", "text": text, "clear_text": True}
    if name == "Launch":
        app = fields["app"]
        resolved = launch_name(app, allowed_apps) if isinstance(app, str) else None
        if resolved is None:
            raise ValueError(f"Launch app {app!r} is unavailable; allowed app values: {json.dumps(allowed_apps)}")
        return {"action_type": "open_app", "app_name": resolved}
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
    # Per word. OsmAnd searches on every typed character; on the software-
    # rendered emulator one word took over 10 s (trial OsmAndTrack_20261008T123135).
    adb_utils.type_text(text, controller, timeout_sec=60)


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
    # Keep informative app nodes; status-bar clocks, keyboard keys (Type enters text) and empty containers add noise.
    for element in state.ui_elements:
        if element.is_visible and element.package_name != "com.android.systemui" and "inputmethod" not in (element.package_name or "") and (
                element.text or element.content_description or element.is_checkable or element.is_selected):
            control = {"label": (element.metadata or {}).get("observed_label") or element.text or element.content_description or element.class_name,
                "checked": element.is_checked if element.is_checkable else None,
                "selected": element.is_selected}
            # Often only a label's unlabeled container is clickable (OsmAnd's rows, Actions, INCREASE SEARCH
            # RADIUS in the forwarder tree); a tap on the label reaches that container, so labels get a centre too.
            if element.bbox_pixels:
                height, width = state.pixels.shape[:2]
                box = element.bbox_pixels
                control["tap_center"] = [int((box.x_min + box.x_max) * 500 / width), int((box.y_min + box.y_max) * 500 / height)]
            if element.is_clickable or element.is_editable:
                control["editable"] = element.is_editable
                control["focused"] = element.is_focused
            controls.append(control)
    return controls[:60]


def xml_controls(xml):
    """Use the official XML parser and attach nearby row text to unlabeled switches."""
    elements = representation_utils.xml_dump_to_ui_elements(xml)
    root = ET.fromstring(xml)
    parents = {child: parent for parent in root.iter() for child in parent}
    # A switch often has no text; its containing GUI row supplies the visible label.
    for node, element in zip(root.iter("node"), elements):
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
        if "tap_center" in control:
            note += " at observed tap center=" + json.dumps(control["tap_center"])
        notes.append(note)
    return "\n".join(notes) or "No GUI tree available; inspect the screenshot."


def changed_pixels(before, after):
    """Count full-resolution pixels that clearly changed, excluding status and navigation bars."""
    if before.pixels.shape != after.pixels.shape:
        return before.pixels.size
    height = before.pixels.shape[0]
    band = slice(int(height * .06), int(height * .94))
    first, second = (np.asarray(Image.fromarray(state.pixels[band]).convert("L"), dtype=np.int16) for state in (before, after))
    return int((np.abs(first - second) > 24).sum())


def no_observed_effect(before, after, threshold):
    """Require unchanged GUI labels/state as well as little pixel change."""
    # Small timer digits can change while affecting very few full-screen pixels.
    # Without a GUI tree (OsmAnd), a label such as "5 mi" -> "10 mi" vanishes at
    # 64x128; recorded ineffective taps changed 0-8 full-resolution pixels and
    # such label changes 296-1373, so more than 50 counts as an effect.
    return (image_difference(before, after) < threshold and changed_pixels(before, after) <= 50
            and screen_controls(before) == screen_controls(after))


def repeated_without_progress(action, actions, results):
    """Bound unchanged repeats/cycles; never turn a stop into model completion."""
    if action["action_type"] == "status":
        return False  # The independent verifier judges a model-issued finish.
    if action["action_type"] == "wait":
        # A slow splash screen legitimately stays unchanged for several waits
        # (cold OsmAnd start took over 40 s, trial OsmAndTrack_20261008T123559).
        # Bound waiting separately: stop only after ten unchanged waits in a row.
        recent = list(zip(actions, results))[-10:]
        return len(recent) == 10 and all(a["action_type"] == "wait" and r["no_visible_effect"] for a, r in recent)
    # D4 p.26: identical actions that return to the same state are no progress,
    # even when each step changes the screen. Two OsmAnd runs repeated a 4- and
    # a 6-action block for over 60 steps (trials _125841, _115319).
    sequence = actions + [action]
    for size in range(2, 7):
        if len(sequence) >= 3 * size and sequence[-size:] == sequence[-2 * size:-size] == sequence[-3 * size:-2 * size]:
            return True
    same = len(actions) >= 2 and all(previous == action for previous in actions[-2:]) and all(r["no_visible_effect"] for r in results[-2:])
    cycle = len(actions) >= 3 and action in actions[-3:] and all(r["no_visible_effect"] for r in results[-3:])
    return same or cycle


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
        self.conversation = []
        self.executed_actions = []
        self.deadline = time.monotonic() + config["max_seconds"]
        self.recording_ready, self.recording_errors = None, []
        self.corrections_this_step = 0
        self.observations = 0
        self.route_points = 0  # last route-panel count the model reported (OsmAnd Skill)
        self.searched_next = False  # next waypoint typed since the route count last changed
        self.centred_on = None  # waypoint whose place card was open in route mode (Back leaves the map there)
        self.next_hint = None  # code-computed next step for the observed OsmAnd screen (v53)
        self.tree_route = False  # True once the GUI tree has shown the route count

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
        # OsmAnd searches in the background: a list read while its spinner turns looks empty (v49 seed 8 read it as "no match").
        for waited in range(30):
            if time.monotonic() >= self.deadline or not search_busy(state.ui_elements):
                break
            time.sleep(1)
            state = self.env.get_state(wait_to_stabilize=False)
        else:
            waited = 30
        if waited:
            log_event(self.output, "SEARCH SPINNER WAIT", {"seconds": waited, "still_busy": search_busy(state.ui_elements)}, len(self.history) + 1)
        # A working display always renders something (at least the status bar).
        # An all-zero frame is an emulator rendering failure (observed with the
        # host-GPU backend: glReadPixels error 0x506), not a screen to reason about.
        if not state.pixels.any():
            raise RuntimeError("Screenshot is entirely black: emulator rendering failure (try -gpu swiftshader_indirect)")
        if self.config["tree_backend"] == "a11y_forwarder":
            # The same screen read by UIAutomator lists the route panel (points, Add, Done) in about 3 s.
            # Checked first: v51-v53 took the package-list branch below, so the fallback never ran.
            # v61 seed 31: right after the forwarder crashed its tree was empty and the UIAutomator dump was
            # rejected (screen still changing), so the model decided without labels; read once more.
            for attempt in range(2):
                if not thin_tree(state.ui_elements):
                    break
                state = self.supplement_controls(state, any_app=True)
                if attempt == 0 and thin_tree(state.ui_elements):
                    time.sleep(2)
                    state = self.env.get_state(wait_to_stabilize=False)
        elif self.config.get("supplemental_tree_packages"):
            state = self.supplement_controls(state)
        return state

    def supplement_controls(self, state, any_app=False):
        """Pair a checked, unique XML dump with a visually unchanged fresh screenshot."""
        self.observations += 1
        record = {"capture": self.observations, "used": False}
        try:
            activity, response = adb_utils.get_current_activity(self.env.controller)
            adb_utils.check_ok(response, "Current activity unavailable")
            record["activity"] = activity
            if not activity or not any_app and activity.split("/")[0] not in self.config["supplemental_tree_packages"]:
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
            return fresh
        except Exception as error:
            record["error"] = str(error)
            return self.env.get_state(wait_to_stabilize=False)
        finally:
            log_event(self.output, "SUPPLEMENTAL GUI STATE", record, len(self.history) + 1)

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
        prompt = (PROJECT / "instructions/autoglm.md").read_text(encoding="utf-8")
        task_name = self.config["task_name"]
        # A benchmark parameter name can resemble current state; label the goal.
        model_inputs = {"text_to_copy": self.scratch["clipboard_content"]} if task_name == "SystemCopyToClipboard" else self.scratch
        prompt += "\nCOMPLETION CONDITION for " + task_name + ":\n" + completion_condition(task_name, self.scratch)
        prompt += skill_text(self.config, task_name, self.scratch)
        prompt += f"\nAvailable apps: {json.dumps(self.config['allowed_apps'])}\n"
        # Upstream gives the goal once; later user turns are observations of that
        # same task, not new requests to perform it again (especially one photo).
        text = f"Task: {goal}\nExact task inputs: {json.dumps(model_inputs)}\n" if not self.conversation else "Latest observation of the original task after the preceding executed action.\n"
        text += f"** Screen Info ** Step {step}/{self.config['max_steps']}.\n"
        text += "Fresh observed GUI labels and state:\n" + control_notes(state) + "\n"
        if task_name == "ClockTimerEntry":
            text += timer_buffer_note(state) + "\n"
        if self.config.get("task_skills", {}).get(task_name) and state.ui_elements:
            view = osmand_view(state.ui_elements)
            if view["points"] is not None:
                self.tree_route = True  # the tree, not the model's words, now keeps the count
                if view["points"] != self.route_points:
                    self.route_points, self.searched_next, self.centred_on = view["points"], False, None
            places = [r for r in view["rows"] if r["settlement"]]
            if places:
                height, width = state.pixels.shape[:2]
                rows = [f'"{r["name"]}" ({r["type"].split(" •")[0]}) at tap center '
                        f'[{r["center"][0] * 1000 // width}, {r["center"][1] * 1000 // height}]' for r in places]
                text += "Place rows on this screen (choose one of these, never another row): " + "; ".join(rows) + "\n"
        self.next_hint = None
        if self.config.get("task_skills", {}).get(task_name) and state.ui_elements:
            terms = [waypoint.split(",")[0].strip() for waypoint in self.scratch["waypoints"]]
            self.next_hint, card = osmand_next_step(state.ui_elements, terms, self.route_points, self.centred_on, state.pixels.shape[:2])
            self.centred_on = card or self.centred_on
        if self.next_hint:
            names = "; ".join(f'{i}. "{t}"' for i, t in enumerate(terms, 1))
            text += (f"Skill status: route points {self.route_points} of {len(terms)} (read from the route panel). Waypoints in order: {names}. "
                     f"Next step for this screen (computed by code from the OsmAnd procedure): {self.next_hint}\n")
        else:
            text += skill_reminder(self.config, task_name, self.scratch, self.route_points)
        if self.history:
            text += "Actual observed result of last action: " + json.dumps(self.history[-1]) + "\n"
        text += "Check the original completion condition before acting; finish when it is satisfied."
        image = base64.b64encode((folder / "model_input.png").read_bytes()).decode("ascii")
        messages = [{"role": "system", "content": prompt}, *history_window(self.conversation, self.config["history_turns"]), {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}}, {"type": "text", "text": text}]}]
        image_message = len(messages) - 1
        # A correction only repairs unexecuted data; HTTP/execution errors never replay.
        for attempt in range(2 - self.corrections_this_step):
            payload = {"model": self.config["model"], "messages": messages, "stream": False, **self.config["sampling"]}
            logged = json.loads(json.dumps(payload))
            logged["messages"][image_message]["content"][0]["image_url"]["url"] = "model_input.png (base64 encoded for API)"
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
                action = convert_action(fields, state, self.config["allowed_apps"], focus_check=lambda: text_field_focused(self.env.controller))
                # convert_action checks focus only when a GUI tree exists; otherwise ask Android.
                if action["action_type"] == "input_text" and not state.ui_elements and not text_field_focused(self.env.controller):
                    raise ValueError("No text field is focused, so nothing would be typed. Tap the text field first, then Type.")
                skill_on = bool(self.config.get("task_skills", {}).get(task_name))
                if skill_on and state.ui_elements:
                    # GUI tree available (accessibility forwarder, v49): check the real screen, not the reply's words.
                    view = osmand_view(state.ui_elements)
                    points_now = self.route_points if view["points"] is None else view["points"]
                    terms = [waypoint.split(",")[0].strip() for waypoint in self.scratch["waypoints"]]
                    searched = points_now == self.route_points and self.centred_on == terms[min(points_now, len(terms) - 1)]
                    correction = osmand_tree_check(view, action, state.pixels.shape[:2], points_now, searched)
                    # false_done (D1 p.50): v56 seed 8 finished at points: 1 of 2. The panel stays until Done saves the track.
                    if action["action_type"] == "status" and self.tree_route and (points_now < len(terms) or view["points"] is not None):
                        correction = (f"The route has {points_now} of {len(terms)} points and is not saved yet (the route panel closes when Done "
                                      "saves the track), so the task is not complete.")
                    if correction is None and action["action_type"] == "input_text" and "," in action["text"]:
                        correction = osmand_rule_break(raw, action)
                    if correction:
                        # v52 seed 8: a fixed "tap INCREASE SEARCH RADIUS" sent the model away from the country row.
                        raise ValueError(correction + (f" Next step for this screen: {self.next_hint}" if self.next_hint else ""))
                elif skill_on:
                    rule_break = osmand_rule_break(raw, action)
                    if rule_break:
                        raise ValueError(rule_break)
                    # The count this reply reads counts too: the Add attempt and "points: 1" arrive together.
                    reported = reported_route_points(raw)
                    points_now = self.route_points if reported is None else reported
                    searched = self.searched_next and points_now == self.route_points
                    if route_add_too_early(raw, action, points_now, searched):
                        waypoint = self.scratch["waypoints"][min(points_now, len(self.scratch["waypoints"]) - 1)].split(",")[0].strip()
                        raise ValueError(f"Add only adds the point under the map centre, which still shows the previous waypoint. First tap the Search "
                                         f'(magnifier) button, the second round button at the top left (the first, a globe, is Configure map), type "{waypoint}", open its row, press Back to this panel, then tap Add.')
                    if favorite_save(raw, action):
                        raise ValueError("That is OsmAnd's Favorite dialog: a Favorite is not a route point and creates no track. Do not save it. "
                                         "Press Back to leave it, then use Actions > Plan a route (first waypoint) or Back to the route panel and its Add.")
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
        if action["action_type"] == "slide":
            adb_utils.check_ok(adb_utils.issue_generic_request(adb_utils.generate_swipe_command(*action["start"], *action["end"]), self.env.controller), "Swipe failed")
        elif action["action_type"] == "wait":
            time.sleep(action["seconds"])
        elif action["action_type"] == "input_text":
            type_without_submit(action["text"], self.env.controller)
        elif action["action_type"] == "open_app":
            launch_app(action["app_name"], self.env.controller)
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
        # Keep the route-panel count the model just reported for the next status line.
        points = reported_route_points(self.pending_reply)
        if points is not None and points != self.route_points and not self.tree_route:
            self.route_points, self.searched_next = points, False
        if action["action_type"] == "input_text" and self.scratch.get("waypoints"):
            names = [w.split(",")[0].strip().lower() for w in self.scratch["waypoints"]]
            following = names[min(self.route_points, len(names) - 1)]
            self.searched_next = self.searched_next or following in action["text"].lower()
        self.history.append(result)
        self.executed_actions.append(action)
        # Keep native executed decisions, removing old images as upstream does.
        # Failed validation, discarded stale choices and uncertain dispatches
        # never enter the executed conversation; original replies stay on disk.
        self.conversation += [{"role": "user", "content": self.pending_user},
                              {"role": "assistant", "content": self.pending_reply}]
        save_json(folder / "result.json", result)
        log_event(self.output, "OBSERVED RESULT", result, step)
        return base_agent.AgentInteractionResult(done=action["action_type"] == "status", data={"action": action})
