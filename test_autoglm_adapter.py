"""Offline checks for action safety and recorded target-freshness failure cases."""

from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
import json
from PIL import Image
from autoglm_agent import repeated_without_progress, assessment_text, native_prompt
from unittest.mock import patch, Mock
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

    def test_container_title_must_be_inside_its_card(self):
        """Reject the recorded recycled-title shape rather than give a folder the wrong name."""
        prefix = '<hierarchy><node class="androidx.cardview.widget.CardView" clickable="true" bounds="[10,50][90,80]">'
        suffix = '</node></hierarchy>'
        valid = prefix + '<node text="project_easy" bounds="[20,55][80,75]"/>' + suffix
        self.assertEqual(xml_controls(valid)[0].metadata['observed_label'], 'project_easy')
        stale = prefix + '<node text="Android" bounds="[20,10][80,30]"/>' + suffix
        with self.assertRaisesRegex(ValueError, 'outside its bounds'):
            xml_controls(stale)

    def test_failed_xml_read_has_one_bounded_recovery(self):
        """Recover checked labels after a read error; two failures still fall back safely."""
        xml = '<hierarchy><node text="project_easy" clickable="true" bounds="[10,50][90,80]"/></hierarchy>'
        empty = State(self.state.pixels, None, [])
        temp_root = Path(__file__).resolve().parent / '.tools/tmp'
        temp_root.mkdir(parents=True, exist_ok=True)
        for second_read, expected_nodes in ((xml, 1), (RuntimeError('dump exit137'), 0)):
            with self.subTest(second_read=type(second_read).__name__), tempfile.TemporaryDirectory(dir=temp_root) as directory:
                agent = AutoGLMAgent.__new__(AutoGLMAgent)
                agent.config = {'supplemental_tree_packages': ['com.google.android.documentsui'],
                    'supplemental_read_retries': 1, 'visual_stability_difference': .01}
                agent.output, agent.observations, agent.history = Path(directory), 0, []
                agent.env = SimpleNamespace(controller=Mock(), get_state=Mock(return_value=empty))
                with patch('autoglm_agent.adb_utils.get_current_activity', return_value=('com.google.android.documentsui/FilesActivity', None)), \
                     patch('autoglm_agent.adb_utils.check_ok'), \
                     patch('autoglm_agent.adb_utils.uiautomator_dump', side_effect=[RuntimeError('dump exit137'), second_read]) as dump:
                    result = agent.supplement_controls(empty)
                self.assertEqual(dump.call_count, 2)
                self.assertEqual(agent.observations, 2)
                self.assertEqual(len(result.ui_elements), expected_nodes)
                records = [json.loads(line) for line in (agent.output / 'trajectory.jsonl').read_text().splitlines()]
                self.assertEqual([item['data']['capture'] for item in records], [1, 2])
                self.assertEqual([item['data']['used'] for item in records], [False, bool(expected_nodes)])

    def test_http_error_exposes_provider_code_without_key_or_retry(self):
        """Preserve the real API rejection and show its redacted details without replay."""
        import io
        import time
        import urllib.error
        temp_root = Path(__file__).resolve().parent / '.tools/tmp'
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            agent = AutoGLMAgent.__new__(AutoGLMAgent)
            agent.output, agent.calls = Path(directory), 0
            agent.endpoint, agent.key = 'https://example.test', 'test-secret'
            agent.config = {'model':'test', 'sampling':{}, 'request_timeout':1}
            agent.deadline = time.monotonic() + 60
            body = b'{"error":{"code":"1210","message":"invalid test-secret"}}'
            failure = urllib.error.HTTPError(agent.endpoint,400,'Bad Request',None,io.BytesIO(body))
            with patch('autoglm_agent.urllib.request.urlopen', side_effect=failure) as send, patch('builtins.print') as console:
                with self.assertRaises(urllib.error.HTTPError):
                    agent.request_model([],agent.output,'action_0',1)
            send.assert_called_once()
            self.assertEqual(agent.calls,1)
            record = (agent.output/'action_0_api_error.json').read_text()
            self.assertIn('1210',record)
            self.assertNotIn('test-secret',record)
            self.assertNotIn('test-secret',(agent.output/'trajectory.txt').read_text())
            self.assertIn('1210',str(console.call_args))
            self.assertNotIn('test-secret',str(console.call_args))

    def test_exact_sms_alias_preserves_allowed_app_boundary(self):
        """Observed translations launch only the task-allowed SMS package."""
        for name in ('简单短信消息发送器', '简单短信消息', 'SimpleSMSMessenger'):
            fields = {'command':'do', 'action':'Launch', 'app':name}
            self.assertEqual(convert_action(fields, self.state, ['simple sms messenger'])['app_name'],
                             'simple sms messenger')
            with self.assertRaises(ValueError):
                convert_action(fields, self.state, ['contacts'])
        with self.assertRaises(ValueError):
            convert_action({'command':'do', 'action':'Launch', 'app':'Unknown SMS app'},
                           self.state, ['simple sms messenger'])

    def test_empty_field_and_visual_fallback_for_tree_availability(self):
        """Empty hints stay groundable; tree availability alone is not a GUI change."""
        controls = screen_controls(self.state)
        self.assertTrue(any(c['label']=='Phone' and c.get('editable') for c in controls))
        before = SimpleNamespace(pixels=self.state.pixels, ui_elements=[])
        self.assertTrue(freshness(before, self.state,
            {'action_type':'click', 'x':200, 'y':150}, self.config)['safe'])
        changed = SimpleNamespace(pixels=np.full_like(self.state.pixels, 255), ui_elements=self.state.ui_elements)
        self.assertFalse(freshness(before, changed,
            {'action_type':'click', 'x':200, 'y':150}, self.config)['safe'])
        label = UIElement(text='project_medium', is_visible=True, is_clickable=False,
            bbox_pixels=BoundingBox(20,100,200,250), package_name='files')
        folder = SimpleNamespace(pixels=self.state.pixels, ui_elements=[label])
        self.assertNotIn('tap_center', screen_controls(folder)[0])
        card = UIElement(text='', is_visible=True, is_clickable=True,
            bbox_pixels=BoundingBox(20,100,200,250), package_name='files',
            metadata={'observed_label':'project_medium'})
        folder = SimpleNamespace(pixels=self.state.pixels, ui_elements=[card,label])
        self.assertEqual(screen_controls(folder)[0]['tap_center'], [150,450])
        self.assertIn('project_medium (clickable)', control_notes(folder))
        wrong = SimpleNamespace(pixels=self.state.pixels, ui_elements=[
            replace(card, metadata={'observed_label':'Recordings'})])
        self.assertFalse(freshness(folder, wrong,
            {'action_type':'click','x':60,'y':225}, self.config)['safe'])

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

    def test_assessment_is_read_only(self):
        """Outcome summaries remain text; native action/finish responses cannot dispatch."""
        self.assertEqual(assessment_text('<think>visible explanation</think><answer>The field is empty after Clear input.</answer>'),
            'The field is empty after Clear input.')
        self.assertEqual(assessment_text('The timer shows the wrong value.\ndo(action="Tap", element=[245,340])'),
            'The timer shows the wrong value.')
        self.assertEqual(assessment_text('The field is empty.\n<answer>finish(message="done")</answer>'), 'The field is empty.')
        for raw in ('', 'finish(message="done")', '<answer>do(action="Back")</answer>', 'x' * 1601):
            with self.subTest(raw=raw[:40]), self.assertRaises(ValueError):
                assessment_text(raw)

    def test_launch_example_has_a_valid_argument(self):
        """The native example is legal in the actual supplied action space."""
        prompt = native_prompt(['chrome'])
        self.assertIn('do(action="Launch", app="chrome")', prompt)
        self.assertNotIn('app="app_name"', prompt)
        self.assertEqual(convert_action(parse_action('do(action="Launch", app="chrome")'), self.state, ['chrome'])['app_name'], 'chrome')
        with self.assertRaises(ValueError):
            native_prompt([])

    def test_assessment_pair_and_next_decision(self):
        """Distinct before/after inputs produce feedback supplied to the next action call."""
        temp_root = Path(__file__).parent / '.tools/tmp'
        temp_root.mkdir(parents=True, exist_ok=True)
        after = SimpleNamespace(pixels=np.full_like(self.state.pixels, 255), ui_elements=[replace(self.field, text='new')])
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            folder = Path(directory)
            agent = object.__new__(AutoGLMAgent)
            agent.config = {'task_name':'SystemCopyToClipboard', 'allowed_apps':['chrome'], 'max_steps':12}
            agent.scratch = {'clipboard_content':'new'}
            agent.output, agent.assessment_calls = folder, 0
            agent.pending_reply = 'do(action="Type", text="new")'
            with patch.object(agent, 'request_model', return_value='The field now contains new.') as call:
                summary = agent.assess_step(self.state, after, folder, 'Copy new', {'action_type':'input_text','text':'new'}, {}, 1)
                content = call.call_args.args[0][1]['content']
                self.assertIn('do(action="Type"', call.call_args.args[0][0]['content'])
                self.assertIn('Read-only step assessment', call.call_args.args[0][0]['content'])
                self.assertIn('Exact task inputs: {"text_to_copy": "new"}', content[0]['text'])
                self.assertEqual(sum(part['type']=='image_url' for part in content), 2)
                self.assertIn('BEFORE', content[1]['text'])
                self.assertIn('AFTER', content[3]['text'])
                self.assertNotEqual(Image.open(folder/'assessment_before.png').getpixel((0,0)),
                    Image.open(folder/'assessment_after.png').getpixel((0,0)))
            agent.history = [{'model_assessment':summary}]
            agent.conversation = [{'role':'user','content':'Original task'}]
            agent.corrections_this_step = 0
            (folder/'model_input.png').write_bytes((folder/'assessment_after.png').read_bytes())
            with patch.object(agent, 'request_model', return_value='finish(message="done")') as call:
                fields, _ = agent.ask_action(after, folder, 'Copy new', 2)
                self.assertIn(summary, call.call_args.args[0][-1]['content'][1]['text'])
                self.assertEqual(fields['command'], 'finish')
            self.assertFalse(json.loads((folder/'assessment.json').read_text())['verifier_feedback'])

    def test_assessment_failure_preserves_dispatch(self):
        """A failed assessment saves the real prior action and never replays it."""
        temp_root = Path(__file__).parent / '.tools/tmp'
        temp_root.mkdir(parents=True, exist_ok=True)
        config = {'invalid_reply_corrections':1, 'max_reobservations':0,
            'max_seconds':900, 'model':'test-model', 'step_assessment':True,
            'no_effect_difference':.001}
        env = SimpleNamespace(execute_action=Mock())
        with tempfile.TemporaryDirectory(dir=temp_root) as directory, patch('autoglm_agent.api_settings',
                return_value=('test-endpoint', 'test-model', 'test-secret')):
            agent = AutoGLMAgent(env, directory, config, {})
            agent.pending_user, agent.pending_reply = 'Task', 'do(action="Home")'
            with patch.object(agent, 'observe', return_value=self.state), patch.object(agent, 'capture'), \
                    patch.object(agent, 'ask_action', return_value=({'command':'do','action':'Home'}, {'action_type':'navigate_home'})), \
                    patch.object(agent, 'assess_step', side_effect=ValueError('Truncated model reply')):
                with self.assertRaises(ValueError):
                    agent.step('Task')
            env.execute_action.assert_called_once()
            self.assertEqual(len(agent.executed_actions), 1)
            result = json.loads((Path(directory)/'step_001/result.json').read_text())
            error = json.loads((Path(directory)/'step_001/assessment_error.json').read_text())
            self.assertTrue(result['dispatch_returned'])
            self.assertTrue(error['action_already_dispatched'])
            self.assertFalse(error['automatic_replay'])


if __name__ == "__main__":
    unittest.main()
