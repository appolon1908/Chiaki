"""Exercise the owned launcher using temporary local executables, never hardware."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


LAUNCHER = Path(__file__).resolve().parents[1] / 'docs/scripts/nabeel-chiaki-launch.sh'


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.engine = self.bin / 'chiaki fixture'
        self.engine.write_text('#!/usr/bin/env python3\nimport json,os,sys\nopen(os.environ["CAPTURE"],"w").write(json.dumps(sys.argv[1:]))\nsys.exit(int(os.environ.get("ENGINE_EXIT", "0")))\n')
        self.engine.chmod(0o700)
        for name, text in {
            'dpkg-query': '#!/bin/sh\nprintf "package=chiaki version=fixture\\n"\n',
            'pgrep': '#!/bin/sh\ncase " $* " in *" -a "*) printf "777 /usr/bin/chiaki --token fixture-only-sensitive-data\\n";; *) printf "777\\n";; esac\n',
        }.items():
            path = self.bin / name
            path.write_text(text)
            path.chmod(0o700)
        self.env = os.environ | {
            'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
            'HOME': str(self.root / 'home'),
            'CHIAKI_BIN': str(self.engine),
            'NABEEL_LOG_ROOT': str(self.root / 'logs'),
            'XDG_CONFIG_HOME': str(self.root / 'config'),
            'CAPTURE': str(self.root / 'args.json'),
        }

    def run_launcher(self, *args, overrides=None):
        return subprocess.run(['bash', str(LAUNCHER), *args], env=self.env | (overrides or {}),
                              text=True, capture_output=True, timeout=5)

    def test_missing_binary_fails_closed(self):
        result = self.run_launcher('launch', overrides={'CHIAKI_BIN': str(self.root / 'absent')})
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / 'args.json').exists())

    def test_status_never_executes_engine(self):
        result = self.run_launcher('status')
        self.assertEqual(0, result.returncode)
        self.assertFalse((self.root / 'args.json').exists())
        self.assertIn('config_home=' + str(self.root / 'config'), result.stdout)

    def test_status_does_not_expose_running_process_arguments(self):
        result = self.run_launcher('status')
        self.assertEqual(0, result.returncode)
        self.assertNotIn('fixture-only-sensitive-data', result.stdout + result.stderr)
        self.assertIn('777', result.stdout)

    def test_launch_forwards_literal_arguments_without_shell_interpretation(self):
        marker = self.root / 'must-not-exist'
        args = ['--profile', 'spaces and symbols', '$(touch ' + str(marker) + ')', ';echo unsafe']
        result = self.run_launcher('launch', *args)
        self.assertEqual(0, result.returncode)
        self.assertEqual(args, json.loads((self.root / 'args.json').read_text()))
        self.assertFalse(marker.exists())

    def test_engine_failure_is_not_reported_as_success(self):
        result = self.run_launcher('launch', overrides={'ENGINE_EXIT': '17'})
        self.assertEqual(17, result.returncode)

    def test_unknown_operation_is_rejected_without_engine_launch(self):
        result = self.run_launcher('publish')
        self.assertEqual(64, result.returncode)
        self.assertFalse((self.root / 'args.json').exists())

    def test_default_operation_is_read_only_status(self):
        result = self.run_launcher()
        self.assertEqual(0, result.returncode)
        self.assertFalse((self.root / 'args.json').exists())
        self.assertTrue((self.root / 'logs').is_dir())

    def test_status_does_not_read_local_credential_files(self):
        config = self.root / 'config'
        config.mkdir()
        (config / 'private.ini').write_text('fixture-local-config-private-content')
        result = self.run_launcher('status')
        self.assertNotIn('fixture-local-config-private-content', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
