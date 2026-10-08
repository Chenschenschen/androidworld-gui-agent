"""Check that selected procedures reach action requests without task leakage."""

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from autoglm_agent import AutoGLMAgent, task_guide


class TaskGuidanceTests(unittest.TestCase):
    """Protect current-task context and independent model action selection."""

    def test_sms_native_contract_correction_remains_model_selected(self):
        """Recorded invalid app/finish shapes receive syntax feedback, never auto-execute."""
        cases = [
            ('do(action="Launch", app="Unknown app")',
             'do(action="Launch", app="simple sms messenger")', 'open_app'),
            ('do(action="finish(message="Text message sent successfully.")',
             'finish(message="Task completed.")', 'status'),
        ]
        temporary = Path(__file__).parent / '.tools/tmp'
        temporary.mkdir(parents=True, exist_ok=True)
        for invalid, corrected, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory(dir=temporary) as directory:
                folder = Path(directory)
                Image.new('RGB', (100, 200)).save(folder / 'model_input.png')
                state = SimpleNamespace(pixels=np.zeros((200,100,3), dtype=np.uint8), ui_elements=[])
                agent = object.__new__(AutoGLMAgent)
                agent.output = folder
                agent.config = {'task_name':'SimpleSmsSend', 'allowed_apps':['simple sms messenger'], 'max_steps':12}
                agent.scratch = {'number':'+10427517979', 'message':'Test message'}
                agent.history, agent.conversation, agent.corrections_this_step = [], [], 0
                with patch.object(agent, 'request_model', side_effect=[invalid, corrected]) as request:
                    _, action = agent.ask_action(state, folder, 'Send the requested SMS', 1)
                self.assertEqual(action['action_type'], expected)
                self.assertEqual(request.call_count, 2)
                feedback = request.call_args.args[0][-1]['content']
                self.assertIn('No action executed', feedback)
                self.assertIn('finish(message="Task completed.")', feedback)
                if expected == 'open_app':
                    self.assertIn('do(action="Launch", app="simple sms messenger")', feedback)

    def test_selected_task_only(self):
        """Clipboard receives its editor procedure, not unrelated task routes."""
        guide = task_guide('SystemCopyToClipboard',{})
        self.assertIn('Start in Markor',guide)
        self.assertIn('Select all',guide)
        self.assertNotIn('Start in Camera',guide)
        self.assertNotIn('Start in Clock',guide)
        with self.assertRaises(ValueError):
            task_guide('UnsupportedTask',{})

    def test_timer_values_follow_instance(self):
        """The guide formats this goal, without borrowing another seed's digits."""
        guide = task_guide('ClockTimerEntry',{'hours':1,'minutes':18,'seconds':45})
        self.assertIn('01h 18m 45s',guide)
        self.assertIn('11845: 1, 1, 8, 4, 5',guide)
        self.assertNotIn('200701',guide)

    def test_procedure_reaches_model_without_execution(self):
        """Real request assembly includes one guide; the returned action remains the model's."""
        temporary = Path(__file__).parent/'.tools/tmp'
        temporary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            folder = Path(directory)
            Image.new('RGB',(100,200)).save(folder/'model_input.png')
            state = SimpleNamespace(pixels=np.zeros((200,100,3),dtype=np.uint8),ui_elements=[])
            agent = object.__new__(AutoGLMAgent)
            agent.config = {'task_name':'SystemCopyToClipboard','allowed_apps':['markor'],
                'max_steps':12,'task_guidance':True}
            agent.scratch = {'clipboard_content':'john.doe@example.com'}
            agent.history,agent.conversation,agent.corrections_this_step = [],[],0
            with patch.object(agent,'request_model',return_value='do(action="Launch", app="markor")') as request:
                _,action = agent.ask_action(state,folder,'Copy exact text',1)
            self.assertEqual(action['app_name'],'markor')

            messages = request.call_args.args[0]
            self.assertIn('TASK PROCEDURE',messages[0]['content'])
            self.assertIn('Start in Markor',messages[0]['content'])
            self.assertIn('john.doe@example.com',messages[-1]['content'][1]['text'])

    def test_ongoing_goal_and_bounded_actual_history(self):
        """Later observations keep original values and recent facts without an extra call."""
        temporary = Path(__file__).parent/'.tools/tmp'
        temporary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            folder = Path(directory)
            Image.new('RGB',(100,200)).save(folder/'model_input.png')
            state = SimpleNamespace(pixels=np.zeros((200,100,3),dtype=np.uint8),ui_elements=[])
            agent = object.__new__(AutoGLMAgent)
            agent.config = {'task_name':'SystemCopyToClipboard','allowed_apps':['markor'],
                'max_steps':12,'recent_effect_context':True,'recent_actions':3}
            agent.scratch = {'clipboard_content':'john.doe@example.com'}
            agent.history = [{'selected_gui_control':{'label':label},'no_visible_effect':False}
                             for label in ['Excluded old action','Create file','OK','Parent directory']]
            agent.conversation = [{'role':'assistant','content':'An earlier uncertain explanation'}]
            agent.corrections_this_step = 0
            with patch.object(agent,'request_model',return_value='do(action="Back")') as request:
                agent.ask_action(state,folder,'Copy exact text',5)
            request.assert_called_once()
            latest = request.call_args.args[0][-1]['content'][1]['text']
            self.assertIn('Original ongoing goal',latest)
            self.assertIn('john.doe@example.com',latest)
            self.assertIn('Create file',latest)
            self.assertIn('Parent directory',latest)
            self.assertNotIn('Excluded old action',latest)

    def test_general_guidance_keeps_recipes_out(self):
        """General requests retain observed feedback and filter unavailable capabilities."""
        temporary = Path(__file__).parent/'.tools/tmp'
        temporary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            folder = Path(directory)
            Image.new('RGB',(100,200)).save(folder/'model_input.png')
            state = SimpleNamespace(pixels=np.zeros((200,100,3),dtype=np.uint8),ui_elements=[])
            agent = object.__new__(AutoGLMAgent)
            agent.config = {'task_name':'SystemCopyToClipboard','allowed_apps':['markor'],
                'max_steps':12,'interaction_guidance':True,'task_guidance':False,
                'app_capabilities':{'markor':'Text editor','chrome':'Browser'}}
            agent.scratch = {'clipboard_content':'john.doe@example.com'}
            agent.history = [{'no_visible_effect':True,'selected_gui_control':{'label':'Clear input'}}]
            agent.conversation,agent.corrections_this_step = [],0
            with patch.object(agent,'request_model',return_value='do(action="Launch", app="markor")') as request:
                _,action = agent.ask_action(state,folder,'Copy exact text',1)
            messages = request.call_args.args[0]
            self.assertIn('General Android interaction guidance',messages[0]['content'])
            self.assertIn('"markor": "Text editor"',messages[0]['content'])
            self.assertNotIn('Browser',messages[0]['content'])
            self.assertNotIn('TASK PROCEDURE',messages[0]['content'])
            self.assertNotIn('QuickNote',messages[0]['content'])
            self.assertIn('Clear input',messages[-1]['content'][1]['text'])
            self.assertEqual(action['app_name'],'markor')
