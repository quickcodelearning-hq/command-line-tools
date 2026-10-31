"""Offline wrapper/installer checks: only temporary apps, homes, and databases."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='lshed test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.app = self.base / 'fake app'
        (self.app / '.venv/bin').mkdir(parents=True)
        (self.app / 'lead_shredder.py').touch()
        (self.app / 'email_enrichment.py').touch()
        (self.app / 'tests').mkdir()
        (self.app / 'tests/test_email_enrichment.py').touch()
        self.log = self.base / 'args.json'
        python = self.app / '.venv/bin/python'
        python.write_text('#!/bin/zsh\n/usr/bin/python3 -c \'import json,os,sys; from pathlib import Path; Path(os.environ["LSHED_TEST_LOG"]).write_text(json.dumps([os.getcwd(),sys.argv[1:]]))\' "$@"\nexit "${LSHED_TEST_EXIT:-0}"\n')
        python.chmod(0o755)
        self.env = dict(os.environ, LSHED_APP_DIR=str(self.app), LSHED_TEST_LOG=str(self.log), HOME=str(self.base / 'home'))

    def run_cmd(self, *args):
        return subprocess.run([str(ROOT / 'lshed'), *args], env=self.env, cwd='/', capture_output=True, text=True)

    def test_dispatch_and_exit_status(self):
        mappings = {'run': ['lead_shredder.py', 'export'], 'dry-run': ['lead_shredder.py', 'export', '--dry-run'], 'enrich': ['lead_shredder.py', 'enrich-emails'], 'retry-emails': ['lead_shredder.py', 'enrich-emails', '--retry-checked']}
        for command, expected in mappings.items():
            with self.subTest(command=command):
                self.assertEqual(self.run_cmd(command, '--city', 'City with spaces').returncode, 0)
                self.assertEqual(json.loads(self.log.read_text()), [str(self.app), expected + ['--city', 'City with spaces']])
        self.env['LSHED_TEST_EXIT'] = '7'
        self.assertEqual(self.run_cmd('run').returncode, 7)

    def test_local_commands_and_errors(self):
        for command in ['help', 'history', 'status', 'doctor', 'test']:
            self.assertEqual(self.run_cmd(command).returncode, 0, command)
        self.assertEqual(json.loads(self.log.read_text())[1], ['-m', 'unittest', 'discover', '-s', 'tests', '-v'])
        self.assertNotEqual(self.run_cmd('reset').returncode, 0)
        self.assertNotEqual(self.run_cmd('status', 'unexpected').returncode, 0)
        self.env['LSHED_APP_DIR'] = str(self.base / 'missing')
        self.assertEqual(self.run_cmd('help').returncode, 0)
        self.assertNotEqual(self.run_cmd('run').returncode, 0)

    def test_read_only_history(self):
        python = self.app / '.venv/bin/python'
        python.unlink()
        python.symlink_to(sys.executable)
        self.assertEqual(self.run_cmd('history').returncode, 0, self.run_cmd('history').stderr)
        db = self.app / 'lead_shredder.sqlite3'
        self.assertFalse(db.exists())
        with sqlite3.connect(db) as conn:
            conn.execute('CREATE TABLE exported_leads(dedupe_key TEXT)')
            conn.executemany('INSERT INTO exported_leads VALUES (?)', [('a',), ('b',)])
        before = db.read_bytes(), db.stat().st_mtime_ns
        for command in ['history', 'status']:
            result = self.run_cmd(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Total leads already exported: 2', result.stdout)
        self.assertEqual(before, (db.read_bytes(), db.stat().st_mtime_ns))

    def test_install_idempotent_and_preserves_conflicts(self):
        def install():
            return subprocess.run([str(ROOT / 'install.sh')], env=self.env, capture_output=True, text=True)
        self.assertEqual(install().returncode, 0)
        self.assertEqual(install().returncode, 0)
        link = Path(self.env['HOME']) / '.local/bin/lshed'
        self.assertEqual(link.resolve(), ROOT / 'lshed')
        result = subprocess.run([str(link), 'help'], env=self.env, cwd='/', capture_output=True)
        self.assertEqual(result.returncode, 0)
        link.unlink()
        link.write_text('keep me')
        self.assertNotEqual(install().returncode, 0)
        self.assertEqual(link.read_text(), 'keep me')
        link.unlink()
        link.symlink_to('/missing/other-tool')
        self.assertNotEqual(install().returncode, 0)
        self.assertEqual(os.readlink(link), '/missing/other-tool')


if __name__ == '__main__':
    unittest.main()
