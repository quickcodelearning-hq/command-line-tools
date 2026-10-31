"""Offline listing checks; future utilities exist only in temporary fixtures."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class MyCommandsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='command tools test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repository with spaces'
        self.repo.mkdir()
        shutil.copy2(ROOT / 'mycommands', self.repo / 'mycommands')
        for name in ('atb-tools', 'lshed-tool'):
            shutil.copytree(ROOT / name, self.repo / name)
        self.link = self.base / 'installed-command'
        self.link.symlink_to(self.repo / 'mycommands')

    def run_command(self, *args):
        result = subprocess.run([str(self.link), *args], cwd='/', text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def add_utility(self, folder, command):
        utility = self.repo / folder
        utility.mkdir()
        (utility / 'README.md').write_text(
            f'# Utility\n\n## Commands\n\n  {command}\n    Unique description for {command}.\n\n'
            '## Installation\nDo not display this section.\n')
        executable = utility / command
        executable.write_text('#!/bin/zsh\nexit 99\n')
        executable.chmod(0o755)

    def test_original_output_and_help(self):
        source = (ROOT / 'mycommands').read_text()
        expected = source.split("cat <<'HELP'\n", 1)[1].split('\nHELP\n', 1)[0] + '\n'
        for args in ((), ('-h',), ('--help',), ('help',)):
            with self.subTest(args=args):
                self.assertEqual(self.run_command(*args), expected)

    def test_prefixes_and_case(self):
        for prefix in ('a', 'at', 'atb', 'A', 'AtB', 'ATB-TOOLS'):
            with self.subTest(prefix=prefix):
                output = self.run_command(prefix)
                self.assertIn('  atb\n', output)
                self.assertIn('  atb-review "filename.mp4"', output)
                self.assertIn('  atb-backup', output)
                self.assertNotIn('  lshed ', output)
        for prefix in ('l', 'ls', 'lshed', 'L', 'LsHeD', 'LSHED-TOOL'):
            with self.subTest(prefix=prefix):
                output = self.run_command(prefix)
                self.assertIn('  lshed run --limit 10', output)
                self.assertIn('  lshed retry-emails --limit 100', output)
                self.assertNotIn('  atb', output)

    def test_unknown_and_literal_prefixes(self):
        for prefix in ('unknown', 'shed', '*', '[a]', '--unknown'):
            with self.subTest(prefix=prefix):
                self.assertIn('No utility folders start with', self.run_command(prefix))

    def test_future_folders_multiple_matches_and_full_listing(self):
        fixtures = {'dental-tools': 'smile', 'marketing-tool': 'promote',
                    'reporting-tools': 'report', 'Dental-admin-tool': 'appointments'}
        for folder, command in fixtures.items():
            self.add_utility(folder, command)
        for prefix, commands in (('d', ('smile', 'appointments')), ('DENTAL', ('smile', 'appointments')),
                                 ('m', ('promote',)), ('marketing', ('promote',)),
                                 ('r', ('report',)), ('reporting', ('report',))):
            with self.subTest(prefix=prefix):
                output = self.run_command(prefix)
                for command in commands:
                    self.assertIn(f'Unique description for {command}.', output)
                self.assertNotIn('Do not display this section.', output)
        output = self.run_command()
        for command in fixtures.values():
            self.assertIn(f'Unique description for {command}.', output)
        self.assertIn('  atb-backup', output)
        self.assertIn('  lshed help', output)

    def test_nonutility_folders_ignored_and_undocumented_folder_explained(self):
        self.add_utility('dental-app', 'ignored')
        (self.repo / 'empty-tools').mkdir()
        self.assertIn('No utility folders start with', self.run_command('d'))
        self.assertIn('No commands documented yet', self.run_command('empty'))

    def test_extra_arguments_get_usage(self):
        result = subprocess.run([str(self.link), 'atb', 'extra'], cwd='/', text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Usage: mycommands [folder-prefix]', result.stderr)


if __name__ == '__main__':
    unittest.main()
