"""Offline checks for action safety and recorded target-freshness failure cases."""

from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
from autoglm_agent import repeated_without_progress
from unittest.mock import patch
import numpy as np
from android_world.env.interface import State
from android_world.env.representation_utils import BoundingBox, UIElement
from autoglm_agent import AutoGLMAgent, convert_action, freshness, parse_action, screen_controls, xml_controls, control_notes, type_without_submit, no_observed_effect, timer_buffer_note


class AdapterTests(unittest.TestCase):
    """Check safe actions, normal focus taps and changes around a selected target."""

    def setUp(self):
        """Create a focused Phone control and unrelated keyboard suggestion."""
        self.field = UIElement(text="", hint_text="Phone", is_visible=True,
            is_enabled=True, is_editable=True, is_focused=True,
            bbox_pixels=BoundingBox(100, 300, 100, 200), package_name="contacts")
        self.suggestion = UIElement(text="old", is_visible=True,
            bbox_pixels=BoundingBox(0, 100, 400, 450), package_name="keyboard")
        self.state = SimpleNamespace(pixels=np.zeros((500, 400, 3), dtype=np.uint8), ui_elements=[self.field, self.suggestion])
        self.config = {"freshness_global_difference": .08, "freshness_target_difference": .08}

    def test_coordinates(self):
        """Coordinates map to physical pixels; malformed values cannot dispatch."""
        action = convert_action(parse_action('<answer>do(action="Tap", element=[1000,1000])</answer>'), self.state, [])
        self.assertEqual(action, {"action_type": "click", "x": 399, "y": 499})
        for point in ([True, 50], [-1, 50], [1001, 50], "100,200"):
            with self.subTest(point=point), self.assertRaises(ValueError):
                convert_action({"command": "do", "action": "Tap", "element": point}, self.state, [])

    def test_runner_tasks_have_rules_and_launch_names(self):
        """Every runner task has a completion rule; multiword official app names launch."""
        from autoglm_agent import COMPLETION_RULES
        from run_task import TASKS
        self.assertLessEqual(set(TASKS), set(COMPLETION_RULES))
        allowed = ["simple calendar pro", "osmand"]
        for app, expected in (("Simple Calendar Pro", "simple calendar pro"), ("SimpleCalendarPro", "simple calendar pro"),
                              ("OsmAnd", "osmand"), ("OsmAnd~", "osmand")):
            with self.subTest(app=app):
                action = convert_action({"command": "do", "action": "Launch", "app": app}, self.state, allowed)
                self.assertEqual(action, {"action_type": "open_app", "app_name": expected})
        # Recorded Chinese translations of "Simple Calendar Pro" (trials
        # SimpleCalendarAddOneEvent_20261008T110618 and _20261008T111150), built
        # from code points so this source file stays ASCII.
        simple_calendar = "".join(map(chr, (0x7B80, 0x5355, 0x65E5, 0x5386)))
        for app in (simple_calendar + " Pro", simple_calendar + "".join(map(chr, (0x4E13, 0x4E1A, 0x7248)))):
            with self.subTest(translated=app):
                action = convert_action({"command": "do", "action": "Launch", "app": app}, self.state, ["simple calendar pro"])
                self.assertEqual(action, {"action_type": "open_app", "app_name": "simple calendar pro"})
                # Ambiguous with two allowed apps: never guess.
                with self.assertRaises(ValueError):
                    convert_action({"command": "do", "action": "Launch", "app": app}, self.state, allowed)
        # An unlisted Latin-script app name is a real choice, not a translation.
        with self.assertRaises(ValueError):
            convert_action({"command": "do", "action": "Launch", "app": "Chrome"}, self.state, ["osmand"])

    def test_launch_waits_for_slow_cold_start(self):
        """Mapped apps get a long `am start -W` timeout; URI-launched apps keep the upstream path."""
        from autoglm_agent import launch_app
        with patch("autoglm_agent.adb_utils.start_activity") as start, patch("autoglm_agent.adb_utils.check_ok"), \
                patch("autoglm_agent.adb_utils.launch_app") as upstream:
            launch_app("osmand", None)
            self.assertIn("net.osmand", start.call_args.args[0])
            self.assertGreaterEqual(start.call_args.kwargs["timeout_sec"], 30)
            launch_app("contacts", None)
            upstream.assert_called_once_with("contacts", None)

    def test_skill_loads_only_for_its_task(self):
        """A configured Skill joins the prompt for its own task only; none when disabled."""
        from autoglm_agent import skill_text
        config = {"task_skills": {"OsmAndTrack": "instructions/skills/osmand_track.md"}}
        inputs = {"waypoints": ["Planken, Liechtenstein", "Rotenboden, Liechtenstein"]}
        text = skill_text(config, "OsmAndTrack", inputs)
        self.assertIn("Plan a route", text)
        # Recorded case (trial OsmAndTrack_20261008T125841): the model typed the full
        # "Planken, Liechtenstein" and only found the country. The Skill derives the terms.
        self.assertIn('1. "Planken"', text)
        self.assertIn('2. "Rotenboden"', text)
        self.assertEqual(skill_text(config, "SimpleCalendarAddOneEvent", inputs), "")
        self.assertEqual(skill_text({"task_skills": {}}, "OsmAndTrack", inputs), "")

    def test_skill_reminder_repeats_search_terms_each_step(self):
        """With the Skill on, every step restates the search terms; nothing without it."""
        from autoglm_agent import skill_reminder
        config = {"task_skills": {"OsmAndTrack": "instructions/skills/osmand_track.md"}}
        inputs = {"waypoints": ["Planken, Liechtenstein", "Rotenboden, Liechtenstein"]}
        reminder = skill_reminder(config, "OsmAndTrack", inputs)
        self.assertIn('1. "Planken"', reminder)
        self.assertIn("never the full", reminder)
        self.assertIn("INCREASE SEARCH RADIUS", reminder)
        # Final-evaluation failures: a same-name guidepost and a Favorite saved three times.
        self.assertIn("Village, Hamlet or Town", reminder)
        self.assertIn("Favorite", reminder)
        # Trial OsmAndTrack_20261008T153947 tapped the route panel's Add expecting a search.
        self.assertIn("Add never searches", reminder)
        # v55 dropped the region-first step (never completed by the model in v44-v52).
        self.assertNotIn('search "Liechtenstein"', reminder)
        self.assertNotIn("search \"", skill_reminder(config, "OsmAndTrack", {"waypoints": ["Planken", "Rotenboden"]}).split("Search terms")[0])
        self.assertEqual(skill_reminder({"task_skills": {}}, "OsmAndTrack", inputs), "")
        self.assertEqual(skill_reminder(config, "ContactsAddContact", {"name": "A"}), "")

    def test_small_text_change_is_an_effect(self):
        """A label change too small for the 64x128 comparison still counts as an effect."""
        before = SimpleNamespace(pixels=np.full((2400, 1080, 3), 200, dtype=np.uint8), ui_elements=[])
        label = before.pixels.copy()
        label[400:420, 300:330] = 0  # 600 pixels, like "5 mi" -> "10 mi" (296-1373 recorded)
        noise = before.pixels.copy()
        noise[1000, 500:505] = 0  # 5 pixels; truly ineffective taps changed 0-8
        self.assertFalse(no_observed_effect(before, SimpleNamespace(pixels=label, ui_elements=[]), 0.001))
        self.assertTrue(no_observed_effect(before, SimpleNamespace(pixels=noise, ui_elements=[]), 0.001))
        self.assertTrue(no_observed_effect(before, before, 0.001))

    def test_route_progress_and_favorite_guard(self):
        """Code keeps the reported route progress; saving a Favorite is refused for the route task."""
        from autoglm_agent import favorite_save, reported_route_points, skill_reminder
        config = {"task_skills": {"OsmAndTrack": "instructions/skills/osmand_track.md"}}
        inputs = {"waypoints": ["Planken, Liechtenstein", "Rotenboden, Liechtenstein"]}
        self.assertIn("not in a route yet", skill_reminder(config, "OsmAndTrack", inputs, 0))
        self.assertIn('Next waypoint: 2. "Rotenboden"', skill_reminder(config, "OsmAndTrack", inputs, 1))
        self.assertIn("tap Done", skill_reminder(config, "OsmAndTrack", inputs, 2))
        # Recorded replies (trials _153947 and _154334).
        self.assertEqual(reported_route_points('The route panel is open with "0 ft, points: 1" displayed.'), 1)
        self.assertIsNone(reported_route_points("The map is centered on Planken."))
        save = 'The "Add Favorite" dialog is open for Rotenboden. To add it to the route, I should tap the "Save" button.'
        self.assertTrue(favorite_save(save, {"action_type": "click", "x": 1, "y": 1}))
        self.assertFalse(favorite_save("Never tap the star Add: it saves a Favorite. I tap Actions.", {"action_type": "click", "x": 1, "y": 1}))
        self.assertFalse(favorite_save(save, {"action_type": "navigate_back"}))

    def test_route_add_requires_search_first(self):
        """The route panel's Add is refused until the next waypoint was searched (trials _153947, _154913)."""
        from autoglm_agent import route_add_too_early
        reply = 'The route panel shows "0 ft, points: 1" and an "Add" button. To add the next waypoint, I should tap the "Add" button.'
        click = {"action_type": "click", "x": 1, "y": 1}
        self.assertTrue(route_add_too_early(reply, click, route_points=1, searched_next=False))
        self.assertFalse(route_add_too_early(reply, click, route_points=1, searched_next=True))
        self.assertFalse(route_add_too_early(reply, click, route_points=0, searched_next=False))
        self.assertFalse(route_add_too_early("I tap the Search button at the top left.", click, route_points=1, searched_next=False))

    def test_forwarder_tree_without_focus_flags(self):
        """The forwarder reports OsmAnd's search field unfocused; Android's input method decides then."""
        field = UIElement(text="Planken", is_visible=True, is_editable=True, is_focused=False,
                          bbox_pixels=BoundingBox(189, 954, 128, 275), package_name="net.osmand")
        state = SimpleNamespace(pixels=self.state.pixels, ui_elements=[field])
        typed = {"command": "do", "action": "Type", "text": "Planken"}
        self.assertEqual(convert_action(typed, state, [], focus_check=lambda: True)["action_type"], "input_text")
        with self.assertRaises(ValueError):
            convert_action(typed, state, [], focus_check=lambda: False)
        with self.assertRaises(ValueError):
            convert_action(typed, state, [])

    def test_osmand_screen_checks_from_gui_tree(self):
        """With the accessibility forwarder, checks read the real screen (boxes recorded in a probe)."""
        from autoglm_agent import osmand_view, osmand_tree_check
        def el(text, box):
            return UIElement(text=text, is_visible=True, bbox_pixels=BoundingBox(*box), package_name="net.osmand")
        results = [el("SHOW ON MAP", (142, 1080, 278, 404)),
                   el("Planken", (147, 847, 475, 532)), el("Village • 2.12 mi from Schaan", (147, 630, 532, 583)),
                   el("Planken", (147, 847, 635, 692)), el("Guidepost", (147, 315, 692, 743))]
        view = osmand_view(results)
        self.assertEqual([(r["name"], r["settlement"]) for r in view["rows"]], [("Planken", True), ("Planken", False)])
        click = lambda x, y: {"action_type": "click", "x": x, "y": y}
        self.assertIn("SHOW ON MAP", osmand_tree_check(view, click(600, 340), (2400, 1080), 0, False))
        self.assertIn("Guidepost", osmand_tree_check(view, click(500, 700), (2400, 1080), 0, False))
        self.assertIsNone(osmand_tree_check(view, click(500, 510), (2400, 1080), 0, False))
        card = osmand_view([el("Planken", (42, 221, 1809, 1876)), el("Add", (106, 172, 2141, 2192)), el("Marker", (348, 465, 2141, 2192)),
                            el("Share", (627, 722, 2141, 2192)), el("Actions", (879, 1003, 2141, 2192))])
        self.assertIn("Favorite", osmand_tree_check(card, click(139, 2110), (2400, 1080), 0, False))
        self.assertIsNone(osmand_tree_check(card, click(941, 2166), (2400, 1080), 0, False))
        dialog = osmand_view([el("Add Favorite", (189, 489, 166, 237)), el("Cancel", (192, 369, 1390, 1485)), el("Save", (727, 871, 1390, 1485))])
        self.assertIn("Favorite", osmand_tree_check(dialog, click(799, 1437), (2400, 1080), 0, False))
        panel = osmand_view([el("0 ft, points: 1", (271, 1038, 1933, 1990)), el("Add", (867, 998, 2221, 2316))])
        self.assertEqual(panel["points"], 1)
        self.assertIn("Search", osmand_tree_check(panel, click(932, 2268), (2400, 1080), 1, False))
        self.assertIsNone(osmand_tree_check(panel, click(932, 2268), (2400, 1080), 1, True))

    def test_osmand_rule_breaks_are_refused(self):
        """Rules the model broke repeatedly become checks: SHOW ON MAP and full-text queries."""
        from autoglm_agent import osmand_rule_break
        click, typed = {"action_type": "click", "x": 1, "y": 1}, {"action_type": "input_text", "text": "Planken, Liechtenstein"}
        # Recorded replies from trial OsmAndTrack_20261008T155302.
        self.assertIn("SHOW ON MAP", osmand_rule_break('I should open the place card by tapping the "SHOW ON MAP" row.', click))
        self.assertIn("Planken", osmand_rule_break("Type the full waypoint name.", typed))
        self.assertIsNone(osmand_rule_break('Tap "SHOW MALBUN ON THE MAP" to select the village.', click))
        self.assertIsNone(osmand_rule_break("Type the search term.", {"action_type": "input_text", "text": "Planken"}))

    def test_text_field_focus_without_gui_tree(self):
        """Android's input-method dump tells whether a text field holds focus."""
        from autoglm_agent import text_field_focused
        def dump(served):
            return SimpleNamespace(generic=SimpleNamespace(output=f"  mServedView={served}\n  mServedView=null\n".encode()))
        # Recorded on the emulator: OsmAnd search field focused versus the map / an unfocused page.
        for served, expected in (("androidx.appcompat.widget.AppCompatEditText{158e104", True),
                                 ("com.google.android.apps.nexuslauncher.search.SearchEditText{eff4ff0", True),
                                 ("DecorView@60e968a[MapActivity]", False)):
            with self.subTest(served=served), patch("autoglm_agent.adb_utils.issue_generic_request", return_value=dump(served)):
                self.assertIs(text_field_focused(None), expected)

    def test_history_window_keeps_goal_and_recent_turns(self):
        """Long runs keep the first (goal) turn and the latest turns within the prompt limit."""
        from autoglm_agent import history_window
        conversation = [{"role": "user" if i % 2 == 0 else "assistant", "content": str(i)} for i in range(176)]
        window = history_window(conversation, 20)
        self.assertEqual(len(window), 40)
        self.assertEqual(window[:2], conversation[:2])
        self.assertEqual(window[2:], conversation[-38:])
        self.assertEqual(history_window(conversation[:10], 20), conversation[:10])

    def test_long_action_cycle_stops(self):
        """A block of two to six actions repeated three times is no progress, even with screen changes."""
        cycle = [{"action_type": "click", "x": 187, "y": 83}, {"action_type": "input_text", "text": "Planken, Liechtenstein", "clear_text": True},
                 {"action_type": "click", "x": 499, "y": 141}, {"action_type": "click", "x": 922, "y": 83}]
        changed = {"no_visible_effect": False}
        history = cycle * 3 + cycle[:3]
        self.assertTrue(repeated_without_progress(cycle[3], history, [changed] * len(history)))
        # The candidate completes only the second repetition: keep going.
        self.assertFalse(repeated_without_progress(cycle[3], cycle + cycle[:3], [changed] * 7))
        typed = [dict(cycle[1], text=name) for name in ("Planken", "Rotenboden", "Malbun")]
        self.assertFalse(repeated_without_progress(cycle[0], [cycle[0], typed[0], cycle[0], typed[1], cycle[0], typed[2]], [changed] * 6))

    def test_adb_retry_keeps_server(self):
        """A timed-out ADB command is retried without killing the shared ADB server."""
        from android_env.components import adb_controller
        from android_compat import keep_adb_server
        self.addCleanup(setattr, adb_controller.AdbController, "_restart_server", adb_controller.AdbController._restart_server)
        keep_adb_server()
        controller = object.__new__(adb_controller.AdbController)
        with patch.object(adb_controller.AdbController, "execute_command") as execute, patch("android_compat.time.sleep"):
            controller._restart_server(timeout=5)
            execute.assert_not_called()

    def test_fresh_xml_retries_transient_null_root(self):
        """A launching app's transient null root is retried; stale XML is never returned."""
        from android_world.env import adb_utils
        from android_compat import enable_fresh_xml
        self.addCleanup(setattr, adb_utils, "uiautomator_dump", adb_utils.uiautomator_dump)
        enable_fresh_xml()

        def device(dump_replies):
            """Fake ADB: scripted dump outputs, a valid hierarchy on read, silent cleanup."""
            def reply(command, env, timeout_sec=None):
                text = ""
                if " dump " in command:
                    text = dump_replies.pop(0).replace("{path}", command.split()[-1])
                elif " cat " in command:
                    text = "<hierarchy/>"
                return SimpleNamespace(generic=SimpleNamespace(output=text.encode()))
            return reply

        null_root = "ERROR: null root node returned by UiTestAutomationBridge."
        with patch("android_world.env.adb_utils.check_ok"), patch("android_compat.time.sleep"):
            with patch("android_world.env.adb_utils.issue_generic_request", device([null_root, "UI hierchary dumped to: {path}"])):
                self.assertEqual(adb_utils.uiautomator_dump(None), "<hierarchy/>")
            with patch("android_world.env.adb_utils.issue_generic_request", device([null_root] * 3)), self.assertRaises(RuntimeError):
                adb_utils.uiautomator_dump(None)

    def test_reject_executable_text(self):
        """Expressions, command overrides and multiple actions never dispatch."""
        for raw in ('do(action="Type", text=__import__("os").getcwd())',
                    'do(command="finish", message="done")',
                    'do(action="Back"); do(action="Home")',
                    'do(action="Back", action="Home")',
                    'do(**{"action": "Back"})'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                convert_action(parse_action(raw), self.state, [])

    def test_focus_and_exact_type(self):
        """Ordinary focus taps remain valid and Type preserves exact task values."""
        self.assertEqual(convert_action(parse_action('do(action="Tap", element=[500,300])'), self.state, [])["action_type"], "click")
        self.assertEqual(convert_action(parse_action('do(action="Type", text="Camila da Silva")'), self.state, [])["text"], "Camila da Silva")
        unfocused = SimpleNamespace(pixels=self.state.pixels, ui_elements=[replace(self.field, is_focused=False)])
        with self.assertRaises(ValueError):
                convert_action(parse_action('do(action="Type", text="test")'), unfocused, [])

    def test_native_finish_text(self):
        """Quoted UI names remain inert finish text; extra calls/arguments are rejected."""
        raw = 'finish(message="Wi-Fi is ON; network "AndroidWifi" is visible.")'
        self.assertEqual(parse_action(raw)["message"], 'Wi-Fi is ON; network "AndroidWifi" is visible.')
        self.assertEqual(convert_action(parse_action(raw), self.state, [])["action_type"], "status")
        for raw in ('finish(message="done"); do(action="Home")',
                    'finish(message="done", extra="x")',
                    'finish(message="done" extra="x")',
                    'finish(message="done" + __import__("os").getcwd())'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                convert_action(parse_action(raw), self.state, [])

    def test_exact_duplicate_calls(self):
        """Collapse one identical decision; different actions/messages remain invalid."""
        for call in ('finish(message="One new photo thumbnail is visible.")', 'do(action="Tap", element=[500,500])'):
            self.assertEqual(parse_action(call + "\n\n" + call), parse_action(call))
        for raw in ('do(action="Back")\ndo(action="Home")', 'finish(message="a")\nfinish(message="b")'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_action(raw)

    def test_type_does_not_submit(self):
        """Replacing text clears first and never adds an Enter/navigation action."""
        with patch("autoglm_agent.adb_utils.issue_generic_request") as clear, patch("autoglm_agent.adb_utils.press_keyboard_generic") as key, patch("autoglm_agent.adb_utils.type_text") as typing, patch("autoglm_agent.adb_utils.check_ok"), patch("autoglm_agent.adb_utils.press_enter_button") as enter:
            type_without_submit("alex.jordan@example.net", None)
            clear.assert_called_once_with(["shell", "input", "keycombination", "113", "29"], None)
            key.assert_called_once_with("67", None)
            typing.assert_called_once_with("alex.jordan@example.net", None, timeout_sec=60)
            enter.assert_not_called()

    def test_model_box_grounding(self):
        """Use the selected box center; inverted/empty/outside boxes cannot dispatch."""
        action = convert_action(parse_action('do(action="Tap", element=[200,300,400,500])'), self.state, [])
        self.assertEqual((action["x"], action["y"]), (120, 200))
        for point in ([400,300,200,500], [200,300,200,500], [0,0,1001,1000], [True,0,100,100]):
            with self.subTest(point=point), self.assertRaises(ValueError):
                convert_action({"command":"do", "action":"Tap", "element":point}, self.state, [])
        with self.assertRaises(ValueError):
            convert_action(parse_action('do(action="Tap", label="invented")'), self.state, [])

    def test_clock_keyboard_input_guards(self):
        """A visible noneditable Clock keypad does not invent a native Type target."""
        display = UIElement(text="00h 00m 00s", is_visible=True,
            resource_id="com.google.android.deskclock:id/timer_setup_time", bbox_pixels=self.field.bbox_pixels)
        state = SimpleNamespace(pixels=self.state.pixels, ui_elements=[display])
        with self.assertRaises(ValueError):
            convert_action(parse_action('do(action="Type", text="200701")'), state, [])

    def test_ineffective_action_cycle(self):
        """Stop repeated zero-effect cycles, permitting recovery and model finish."""
        actions = [{"action_type":"click", "x":x, "y":20} for x in (1,0,2)]
        effects = [{"no_visible_effect":True} for _ in actions]
        self.assertTrue(repeated_without_progress(actions[0], actions, effects))
        self.assertFalse(repeated_without_progress({"action_type":"click", "x":99, "y":20}, actions, effects))
        self.assertFalse(repeated_without_progress({"action_type":"status", "goal_status":"complete"}, actions, effects))
        self.assertFalse(repeated_without_progress(actions[0], actions, [{"no_visible_effect":False},*effects[1:]]))

    def test_waiting_on_loading_screen_is_bounded_separately(self):
        """Unchanged waits are normal on a slow splash screen; stop only after ten in a row."""
        wait, launch = {"action_type": "wait", "seconds": 1.0}, {"action_type": "open_app", "app_name": "osmand"}
        unchanged = {"no_visible_effect": True}
        # Recorded cases: trial OsmAndTrack_20261008T122441 stopped after launch, wait,
        # wait; trial _20261008T123559 needed more than six unchanged waits (over 40 s).
        self.assertFalse(repeated_without_progress(wait, [launch, wait, wait], [unchanged] * 3))
        self.assertFalse(repeated_without_progress(wait, [launch] + [wait] * 6, [unchanged] * 7))
        self.assertTrue(repeated_without_progress(wait, [wait] * 10, [unchanged] * 10))
        self.assertFalse(repeated_without_progress(wait, [wait] * 10, [unchanged] * 9 + [{"no_visible_effect": False}]))

    def test_xml_edittext_without_editable_attribute(self):
        """Real XML EditText supports native Type; unrelated focused nodes do not."""
        xml = '<hierarchy><node class="android.widget.EditText" text="" focused="true" enabled="true" bounds="[100,100][300,200]" package="com.android.chrome" /></hierarchy>'
        elements = xml_controls(xml)
        self.assertTrue(elements[0].is_editable)
        self.assertTrue(elements[0].metadata["editable_from_observed_class"])
        state = SimpleNamespace(pixels=self.state.pixels, ui_elements=elements)
        self.assertEqual(convert_action(parse_action('do(action="Type", text="john.doe@example.com")'), state, [])["text"], "john.doe@example.com")
        elements[0].text = "Address field"
        self.assertIn("editable, focused", control_notes(state))
        state.ui_elements = xml_controls(xml.replace("android.widget.EditText", "android.widget.TextView"))
        with self.assertRaises(ValueError):
            convert_action(parse_action('do(action="Type", text="x")'), state, [])

    def test_small_digit_progress(self):
        """A changed actual timer display is progress despite negligible image area."""
        display = UIElement(text="00h 00m 03s", is_visible=True, package_name="com.google.android.deskclock")
        before = SimpleNamespace(pixels=self.state.pixels, ui_elements=[display])
        after = SimpleNamespace(pixels=self.state.pixels, ui_elements=[replace(display, text="00h 00m 33s")])
        self.assertFalse(no_observed_effect(before, after, .001))
        self.assertTrue(no_observed_effect(before, before, .001))

    def test_observed_timer_buffer(self):
        """Decode genuine padded GUI digits; absent/malformed displays stay unknown."""
        display = UIElement(text="01h 33m 33s", is_visible=True, resource_id="com.google.android.deskclock:id/timer_setup_time")
        state = SimpleNamespace(ui_elements=[display])
        self.assertIn("'13333'", timer_buffer_note(state))
        self.assertIn("digit count: 5", timer_buffer_note(state))
        display.text = "00h 00m 20s"
        self.assertIn("'20'", timer_buffer_note(state))
        display.text = "00h 00m 00s"
        self.assertIn("digit count: 0", timer_buffer_note(state))
        display.text = "loading"
        self.assertEqual(timer_buffer_note(state), "")

    def test_unrelated_suggestion(self):
        """Changing Gboard suggestions does not block an unchanged Phone field."""
        fresh = SimpleNamespace(pixels=self.state.pixels, ui_elements=[self.field, replace(self.suggestion, text="new")])
        self.assertTrue(freshness(self.state, fresh, {"action_type": "input_text"}, self.config)["safe"])

    def test_changed_target_and_modal(self):
        """A moved field or broad visual change invalidates the old decision."""
        fresh = SimpleNamespace(pixels=self.state.pixels, ui_elements=[replace(self.field, bbox_pixels=BoundingBox(200, 400, 100, 200))])
        self.assertFalse(freshness(self.state, fresh, {"action_type": "input_text"}, self.config)["safe"])
        modal = SimpleNamespace(pixels=np.full_like(self.state.pixels, 255), ui_elements=self.state.ui_elements)
        self.assertFalse(freshness(self.state, modal, {"action_type": "click", "x": 200, "y": 150}, self.config)["safe"])

    def test_observed_switch_flags(self):
        """Expose true and false switch states faithfully; ordinary labels have no state."""
        label = UIElement(text="Wi-Fi", is_visible=True, package_name="com.android.settings")
        switch = UIElement(is_checkable=True, is_checked=True, is_visible=True, package_name="com.android.settings")
        self.state.ui_elements = [label, switch]
        self.assertIsNone(screen_controls(self.state)[0]["checked"])
        self.assertIs(screen_controls(self.state)[1]["checked"], True)
        switch.is_checked = False
        self.assertIs(screen_controls(self.state)[1]["checked"], False)
        xml = '<hierarchy><node><node text="Wi-Fi"/><node class="android.widget.Switch" checkable="true" checked="true"/></node><node><node text="Mobile data"/><node class="android.widget.Switch" checkable="true" checked="false"/></node></hierarchy>'
        self.state.ui_elements = xml_controls(xml)
        notes = control_notes(self.state)
        self.assertIn("Wi-Fi: switch ON (checked=true)", notes)
        self.assertIn("Mobile data: switch OFF (checked=false)", notes)

    def test_black_frame_is_infrastructure_error(self):
        """An all-black screenshot (failed emulator rendering) never reaches the model."""
        temp_root = Path(__file__).parent / ".tools/tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            agent = object.__new__(AutoGLMAgent)
            agent.output, agent.history, agent.deadline = Path(folder), [], float("inf")
            agent.config = {"visual_stability_checks": 1, "visual_stability_pause": 0,
                            "visual_stability_difference": .01, "tree_backend": "none"}
            for pixels in (np.zeros((500, 400, 3), dtype=np.uint8), np.full((500, 400, 3), 9, dtype=np.uint8)):
                agent.env = SimpleNamespace(get_state=lambda wait_to_stabilize, pixels=pixels: State(pixels, None, []))
                if pixels.any():
                    self.assertIs(agent.observe().pixels, pixels)
                else:
                    with self.assertRaisesRegex(RuntimeError, "black"):
                        agent.observe()

    def test_observation_waits_for_search_spinner_and_hides_keyboard(self):
        """A list read while OsmAnd's spinner turns looks empty; keyboard keys never reach the model."""
        temp_root = Path(__file__).parent / ".tools/tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        spinner = UIElement(is_visible=True, resource_name="net.osmand:id/searchProgressBar", bbox_pixels=BoundingBox(975, 1059, 159, 243))
        key = UIElement(content_description="q", is_visible=True, is_clickable=True, bbox_pixels=BoundingBox(5, 112, 1654, 1808),
                        package_name="com.google.android.inputmethod.latin")
        row = UIElement(text="Planken", is_visible=True, is_clickable=True, bbox_pixels=BoundingBox(0, 1080, 404, 530), package_name="net.osmand")
        up = UIElement(content_description="Navigate up", is_visible=True, is_clickable=True, bbox_pixels=BoundingBox(0, 147, 128, 275), package_name="net.osmand")
        pixels = np.full((500, 400, 3), 9, dtype=np.uint8)
        screens = iter([[spinner, key], [spinner, key], [spinner, key], [up, row, key]])
        with tempfile.TemporaryDirectory(dir=temp_root) as folder, patch("autoglm_agent.time.sleep"):
            agent = object.__new__(AutoGLMAgent)
            agent.output, agent.history, agent.deadline = Path(folder), [], float("inf")
            agent.config = {"visual_stability_checks": 1, "visual_stability_pause": 0,
                            "visual_stability_difference": 1, "tree_backend": "a11y_forwarder"}
            agent.env = SimpleNamespace(get_state=lambda wait_to_stabilize: State(pixels, None, next(screens)))
            state = agent.observe()
        self.assertEqual(state.ui_elements, [up, row, key])
        self.assertEqual([c["label"] for c in screen_controls(state)], ["Navigate up", "Planken"])

    def test_region_row_and_label_tap_centres(self):
        """v51 seed 8: the country row (Skill's region step) was refused, and unclickable labels had no centre."""
        from autoglm_agent import osmand_view, osmand_tree_check
        el = lambda text, box: UIElement(text=text, is_visible=True, bbox_pixels=BoundingBox(*box), package_name="net.osmand")
        country = osmand_view([el("Liechtenstein", (189, 600, 404, 466)), el("Country", (189, 400, 466, 512))])
        self.assertIsNone(osmand_tree_check(country, {"action_type": "click", "x": 400, "y": 440}, (2400, 1080), 0, False))
        radius = el("INCREASE SEARCH RADIUS", (189, 900, 700, 760))
        state = SimpleNamespace(pixels=np.zeros((2400, 1080, 3), dtype=np.uint8), ui_elements=[radius])
        self.assertEqual(screen_controls(state)[0]["tap_center"], [504, 304])

    def test_osmand_next_step_follows_the_procedure(self):
        """Labels and resource names as recorded in v50-v52 runs; one step per screen through a two-waypoint track."""
        from autoglm_agent import osmand_next_step
        def el(label, box, rid="", desc=False, hint=None):
            return UIElement(text=None if desc else label, content_description=label if desc else None, hint_text=hint, is_visible=True,
                             bbox_pixels=BoundingBox(*box), resource_name="net.osmand:id/" + rid, package_name="net.osmand")
        terms, shape = ["Planken", "Rotenboden"], (2400, 1080)
        step = lambda screen, points=0, centred=None: osmand_next_step(screen, terms, points, centred, shape)
        field = lambda text: el(text, (189, 975, 128, 275), "searchEditText", hint="Type to search all")
        self.assertIn('Tap "Search" at tap center [187, 83]', step([el("Map", (0, 1080, 0, 2337), desc=True),
            el("Configure map", (16, 132, 128, 236), desc=True), el("Search", (145, 261, 128, 275), desc=True)])[0])
        self.assertEqual(step([field("Type to search all")])[0], 'Type "Planken" (only the place name).')
        # UIAutomator XML (the fallback) carries the id in resource_id, not resource_name.
        xml_field = UIElement(text="Planken", is_visible=True, bbox_pixels=BoundingBox(189, 975, 128, 275), resource_id="net.osmand:id/searchEditText")
        self.assertIn('Tap "INCREASE SEARCH RADIUS"', step([xml_field, el("INCREASE SEARCH RADIUS", (189, 900, 770, 840))])[0])
        empty = [field("Planken"), el("Clear", (900, 1050, 128, 275), desc=True), el("INCREASE SEARCH RADIUS", (189, 900, 770, 840))]
        self.assertIn('Tap "INCREASE SEARCH RADIUS"', step(empty)[0])
        self.assertIn('Tap "Clear"', step([field("Liechtenstein"), el("Clear", (900, 1050, 128, 275), desc=True)])[0])
        rows = [field("Planken"), el("Planken", (189, 900, 1400, 1460), "title"), el("Guidepost", (189, 600, 1460, 1500), "subtitle"),
                el("Planken", (189, 900, 1500, 1560), "title"), el("Village", (189, 600, 1560, 1600), "subtitle")]
        self.assertIn('Village row "Planken" at tap center [503, 637]', step(rows)[0])
        card = lambda name, kind: [el(name, (42, 900, 1809, 1876), "context_menu_line1"), el(kind, (42, 600, 1876, 1920), "context_menu_line2"),
                                   el("Add", (106, 172, 2141, 2192)), el("Marker", (348, 465, 2141, 2192)), el("Share", (500, 600, 2141, 2192)),
                                   el("Actions", (800, 1000, 2141, 2192))]
        self.assertIn('Tap "Actions"', step(card("Planken", "Village"))[0])
        self.assertIn("not the place", step(card("Planken", "Guidepost"))[0])
        menu = [el("Directions from", (0, 1080, 800, 900), "title"), el("Plan a route", (0, 1080, 1000, 1100), "title")]
        self.assertIn('Tap "Plan a route"', step(menu)[0])
        panel = lambda n: [el("Search", (145, 261, 291, 407), desc=True), el("Done", (835, 1027, 154, 249)), el(f"points: {n}", (271, 1038, 1933, 1990)),
                           el("Add", (867, 998, 2221, 2316))]
        self.assertIn('Tap "Search"', step(panel(1), 1)[0])
        self.assertEqual(step(card("Rotenboden", "Hamlet"), 1)[1], "Rotenboden")
        self.assertIn("Press Back", step([field("Rotenboden")], 1, "Rotenboden")[0])
        self.assertIn('Tap "Add"', step(panel(1), 1, "Rotenboden")[0])
        # v56 seed 8: the place card lies over the route panel after SHOW ... ON THE MAP.
        self.assertEqual(step(card("Rotenboden", "Village • 1.10 mi from Vaduz") + panel(1), 1), (
            'Press Back until the route panel ("points: 1", Add, Done) is shown; the map stays centred on "Rotenboden".', "Rotenboden"))
        # v55 seed 8: a street list inside the place, and a panel whose centre is still the last point.
        streets = [field("Rotenboden "), el("SHOW ROTENBODEN ON THE MAP", (142, 1080, 278, 404), "buttonToolbarTitle")]
        self.assertIn('Tap "SHOW ROTENBODEN ON THE MAP"', step(streets, 1, "Rotenboden")[0])
        self.assertIn('Tap "Search"', step(panel(1) + [el("0 ft • 0°", (189, 309, 1990, 2041))], 1, "Rotenboden")[0])
        self.assertIn('Tap "Done"', step(panel(2), 2)[0])
        self.assertIn("Tap \"Cancel\"", step([el("Exit without saving?", (0, 1080, 800, 900), "title"), el("Cancel", (0, 500, 1500, 1600))], 1)[0])

    def test_near_empty_forwarder_tree_falls_back_to_uiautomator(self):
        """The forwarder shows OsmAnd's Plan a route screen as only "Map"; UIAutomator then reads it."""
        from autoglm_agent import thin_tree
        el = lambda label, package="net.osmand": UIElement(content_description=label, is_visible=True, package_name=package,
                                                           bbox_pixels=BoundingBox(0, 10, 0, 10))
        plan_route = [el("Map"), el("15:42", "com.android.systemui")]
        self.assertTrue(thin_tree(plan_route))
        self.assertFalse(thin_tree(plan_route + [el("Search")]))
        temp_root = Path(__file__).parent / ".tools/tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        pixels = np.full((500, 400, 3), 9, dtype=np.uint8)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            agent = object.__new__(AutoGLMAgent)
            agent.output, agent.history, agent.deadline = Path(folder), [], float("inf")
            agent.config = {"visual_stability_checks": 1, "visual_stability_pause": 0, "visual_stability_difference": 1,
                            "tree_backend": "a11y_forwarder", "supplemental_tree_packages": ["com.android.settings"]}
            agent.env = SimpleNamespace(get_state=lambda wait_to_stabilize: State(pixels, None, plan_route))
            with patch.object(AutoGLMAgent, "supplement_controls", return_value="uiautomator state") as supplement:
                self.assertEqual(agent.observe(), "uiautomator state")
            supplement.assert_called_once()
            self.assertTrue(supplement.call_args.kwargs["any_app"])

    def test_xml_image_pairing(self):
        """Keep genuine XML on an unchanged scene, discard it after a visual transition."""
        state = State(self.state.pixels, None, [])
        xml = '<hierarchy><node text="Wi-Fi" package="com.android.settings" bounds="[1,1][10,10]" checkable="true" checked="true"/></hierarchy>'
        # A fresh clone has no generated tooling directory until it is needed.
        temp_root = Path(__file__).parent / ".tools/tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            agent = object.__new__(AutoGLMAgent)
            agent.output, agent.observations, agent.history = Path(folder), 0, []
            agent.config = {"supplemental_tree_packages": ["com.android.settings"], "visual_stability_difference": .01}
            for pixels, expected in ((state.pixels, 1), (np.full_like(state.pixels, 255), 0)):
                agent.env = SimpleNamespace(controller=None, get_state=lambda wait_to_stabilize: replace(state, pixels=pixels))
                with patch("autoglm_agent.adb_utils.get_current_activity", return_value=("com.android.settings/Settings", None)), patch("autoglm_agent.adb_utils.check_ok"), patch("autoglm_agent.adb_utils.uiautomator_dump", return_value=xml):
                    self.assertEqual(len(agent.supplement_controls(state).ui_elements), expected)


if __name__ == "__main__":
    unittest.main()
