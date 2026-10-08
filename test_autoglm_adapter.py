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
        for app in ("Simple Calendar Pro", "OsmAnd"):
            with self.subTest(app=app):
                action = convert_action({"command": "do", "action": "Launch", "app": app}, self.state, ["simple calendar pro", "osmand"])
                self.assertEqual(action, {"action_type": "open_app", "app_name": app.lower()})

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
            typing.assert_called_once_with("alex.jordan@example.net", None, timeout_sec=10)
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
