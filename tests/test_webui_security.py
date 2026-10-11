import tempfile
import unittest
import os
import subprocess
import sys
from pathlib import Path

from webui_security import launch_options


class LaunchSecurityTest(unittest.TestCase):
    def test_default_is_local_and_only_serves_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            options = launch_options(root, {})
            self.assertEqual(options['server_name'], '127.0.0.1')
            self.assertIsNone(options['auth'])
            self.assertFalse(options['share'])
            self.assertEqual(options['allowed_paths'], [str(Path(root) / 'web_out')])
            self.assertNotIn(root, options['allowed_paths'])

    def test_external_host_requires_auth(self):
        for host in ('0.0.0.0', '::', '192.0.2.1'):
            with self.subTest(host=host), self.assertRaises(ValueError):
                launch_options('/workspace', {'GRADIO_SERVER_NAME': host})

    def test_complete_credentials_work_for_external_host(self):
        options = launch_options('/workspace', {
            'GRADIO_SERVER_NAME': '0.0.0.0',
            'GRADIO_USER': 'test-user', 'GRADIO_PASSWORD': 'test-password',
        })
        self.assertEqual(options['auth'], ('test-user', 'test-password'))

    def test_missing_or_blank_credential_never_disables_auth(self):
        for env in (
            {'GRADIO_USER': 'test-user'}, {'GRADIO_PASSWORD': 'test-password'},
            {'GRADIO_USER': '', 'GRADIO_PASSWORD': ''},
            {'GRADIO_USER': 'test-user', 'GRADIO_PASSWORD': ' '},
            {'GRADIO_USER': ' ', 'GRADIO_PASSWORD': 'test-password'},
        ):
            with self.subTest(keys=list(env)), self.assertRaises(ValueError):
                launch_options('/workspace', env)

    def test_empty_host_is_rejected(self):
        with self.assertRaises(ValueError):
            launch_options('/workspace', {'GRADIO_SERVER_NAME': ' '})

    def test_app_rejects_unsafe_settings_before_model_imports(self):
        app = Path(__file__).resolve().parents[1] / 'app.py'
        for settings in (
            {'GRADIO_SERVER_NAME': '0.0.0.0'},
            {'GRADIO_USER': 'test-user'},
        ):
            env = {key: value for key, value in os.environ.items() if not key.startswith('GRADIO_')}
            env.update(settings)
            result = subprocess.run([sys.executable, str(app)], env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ValueError:', result.stderr)
            self.assertNotIn('ModuleNotFoundError', result.stderr)


if __name__ == '__main__':
    unittest.main()
