"""Regression checks for the real recorder/Chrome timeout failure."""

import subprocess
import threading
import tempfile
import base64
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from run_task import watch_recording, ensure_required_app, finish_recording, initialize_existing_move
from autoglm_agent import launch_chrome_once, type_with_adb_keyboard
from android_compat import enable_single_attempt_adb


class RecordingTransportTests(unittest.TestCase):
    """Keep recording availability honest and prevent uncertain launch replay."""

    def test_linked_move_initializes_without_recreating_file(self):
        """The reverse trial retains the file and rejects invalid starting states."""
        from android_world.task_evals.single.files import FilesMoveFile
        task = FilesMoveFile({'file_name':'cooking-recipe.md', 'source_folder':'project_medium',
                             'destination_folder':'project_easy', 'noise_candidates':['cooking-recipe.md']})
        env = SimpleNamespace(controller=None)
        with patch('android_world.utils.file_utils.check_file_or_folder_exists', side_effect=[False, True]), \
                patch('android_world.task_evals.task_eval.TaskEval.initialize_task') as base, \
                patch.object(task, 'initialize_task') as reset, \
                patch('android_world.utils.file_utils.create_file') as create:
            initialize_existing_move(task, env)
            self.assertEqual(base.call_count, 2)
            reset.assert_not_called()
            create.assert_not_called()
        for state in ([False, False], [True]):
            with self.subTest(state=state), \
                    patch('android_world.utils.file_utils.check_file_or_folder_exists', side_effect=state), \
                    patch('android_world.task_evals.task_eval.TaskEval.initialize_task') as base:
                with self.assertRaises(RuntimeError):
                    initialize_existing_move(task, env)
                base.assert_not_called()
        with patch('android_world.utils.file_utils.check_file_or_folder_exists', side_effect=[False, False]), \
                patch('android_world.task_evals.task_eval.TaskEval.initialize_task'), \
                patch('android_world.utils.file_utils.create_file') as create, \
                patch('android_world.utils.file_utils.mkdir') as mkdir, \
                patch('android_world.task_evals.utils.user_data_generation.clear_device_storage') as clear:
            initialize_existing_move(task, env, prepare_source=True)
            create.assert_called_once_with('cooking-recipe.md', task.move_file_task.source_directory, None)
            mkdir.assert_called_once_with(task.move_file_task.dest_directory, None)
            clear.assert_not_called()

    def test_sdk_app_launch_has_bounded_cold_start_timeout(self):
        """The observed SMS launch timeout gets thirty seconds with one dispatch."""
        from android_env.components import adb_controller, errors
        controller = SimpleNamespace(command_prefix=lambda **kwargs: ['adb'],
            _config=SimpleNamespace(default_timeout=5), _os_env_vars={})
        with patch.object(adb_controller.AdbController, 'execute_command'):
            enable_single_attempt_adb()
            with patch('android_compat.subprocess.check_output',
                       side_effect=subprocess.TimeoutExpired('adb', 30)) as run:
                with self.assertRaises(errors.AdbControllerError):
                    adb_controller.AdbController.execute_command(controller,
                        ['shell', 'am', 'start', '-W', '-n', 'test/activity'], timeout=5)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.kwargs['timeout'], 30)

    def test_early_exit_clears_ready(self):
        """An exited recorder cannot retain a ready flag for later GUI actions."""
        ready = threading.Event()
        ready.set()
        with self.assertRaisesRegex(RuntimeError, "recorder exited"):
            watch_recording(Mock(poll=Mock(return_value=0)), threading.Event(), ready)
        self.assertFalse(ready.is_set())

    def test_chrome_timeout_no_retry(self):
        """A timeout escapes after exactly one launch, without ADB restart/replay."""
        with patch('autoglm_agent.subprocess.run', side_effect=subprocess.TimeoutExpired('adb',30)) as run:
            with patch.dict('os.environ', {'LOCALAPPDATA': 'C:/test'}):
                with self.assertRaises(subprocess.TimeoutExpired):
                    launch_chrome_once(30)
        self.assertEqual(run.call_count,1)
        self.assertEqual(run.call_args.kwargs['timeout'],30)

    def test_snapshot_without_package_prepares_again(self):
        """The actual Clipper failure must reinstall despite existing snapshot data."""
        app = SimpleNamespace(app_name='clipper', package_name=lambda:'ca.zgrs.clipper')
        env = SimpleNamespace(controller=None)
        with patch('android_world.env.setup_device.setup.is_package_installed',side_effect=[False,True]), \
                patch('android_world.utils.file_utils.check_directory_exists',return_value=True), \
                patch('run_task.setup_required_app') as prepare, patch('run_task.log_event'), patch('run_task.save_json'):
            ensure_required_app(app,env,None)
        prepare.assert_called_once_with(app,env,None)

    def test_failed_preparation_does_not_claim_readiness(self):
        """A still-missing APK stops before initialization instead of saving a ready marker."""
        app = SimpleNamespace(app_name='clipper', package_name=lambda:'ca.zgrs.clipper')
        env = SimpleNamespace(controller=None)
        with patch('android_world.env.setup_device.setup.is_package_installed',return_value=False), \
                patch('android_world.utils.file_utils.check_directory_exists',return_value=True), \
                patch('run_task.setup_required_app'), patch('run_task.log_event'), patch('run_task.save_json') as save:
            with self.assertRaisesRegex(RuntimeError,'readiness'):
                ensure_required_app(app,env,None)
        save.assert_not_called()

    def test_shutdown_transfer_failure_preserves_remote(self):
        """A bounded failed pull never removes the only copy of a video."""
        temporary = Path(__file__).parent/'.tools/tmp'
        temporary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            local = Path(directory)/'video_001.mp4'
            process = Mock()
            with patch('run_task.subprocess.run',side_effect=[Mock(),subprocess.TimeoutExpired('pull',20)]) as run:
                with self.assertRaises(subprocess.TimeoutExpired):
                    finish_recording(['adb','-s','emulator-5554'],process,'123','/sdcard/our_video.mp4',local)
            self.assertEqual(run.call_count,2)
            self.assertEqual(run.call_args.kwargs['timeout'],20)
            process.wait.assert_called_once_with(timeout=15)
            self.assertIn('"phase": "pull"',local.with_suffix('.shutdown.json').read_text())

    def test_native_type_timeout_restores_without_replay(self):
        """Uncertain broadcast fails once, restores IME and never submits or repeats text."""
        temporary = Path(__file__).parent/'.tools/tmp'
        temporary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            ime = 'com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME'
            responses = [Mock(stdout=ime),Mock(),Mock(),subprocess.TimeoutExpired('broadcast',10),Mock()]
            with patch('autoglm_agent.subprocess.run',side_effect=responses) as run, \
                    patch('autoglm_agent.time.sleep'), patch.dict('os.environ',{'LOCALAPPDATA':'C:/test'}):
                with self.assertRaises(subprocess.TimeoutExpired):
                    type_with_adb_keyboard('Çağrı',30,Path(directory))
            commands = [call.args[0] for call in run.call_args_list]
            inputs = [command for command in commands if 'ADB_INPUT_B64' in command]
            self.assertEqual(len(inputs),1)
            self.assertEqual(base64.b64decode(inputs[0][-1]).decode('utf-8'),'Çağrı')
            self.assertEqual(commands[-1][-3:],['ime','set',ime])
            self.assertFalse(any('keyevent' in command or 'kill-server' in command for command in commands))

    def test_sdk_timeout_never_restarts_or_replays(self):
        """The exact UIAutomator timeout remains an error without killing video connections."""
        from android_env.components import adb_controller, errors
        original = adb_controller.AdbController.execute_command
        controller = object.__new__(adb_controller.AdbController)
        controller._config = SimpleNamespace(default_timeout=5)
        controller._os_env_vars = {}
        with patch.object(adb_controller.AdbController,'execute_command',original), \
                patch.object(controller,'command_prefix',return_value=['adb','-s','emulator-5554']), \
                patch.object(controller,'_restart_server') as restart, \
                patch('android_compat.subprocess.check_output',side_effect=subprocess.TimeoutExpired('dump',8)) as command:
            enable_single_attempt_adb()
            with self.assertRaises(errors.AdbControllerError):
                controller.execute_command(['shell','uiautomator','dump','/sdcard/unique.xml'],timeout=8)
            command.assert_called_once()
            self.assertEqual(command.call_args.kwargs['timeout'],8)
            restart.assert_not_called()
