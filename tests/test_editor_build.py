"""A failed build step must not be reported as a successful editor build."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class EditorBuildFailure(unittest.TestCase):
    def test_failed_source_export_stops_the_build(self):
        source = Path(__file__).resolve().parents[1] / 'scripts/build-editor'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            shutil.copyfile(source, root / 'scripts/build-editor')
            tools = root / 'bin'
            tools.mkdir()
            for name, body in {
                'git': 'echo source-export-failed >&2; exit 17',
                'npm': 'touch "$BUILD_UNEXPECTED_NPM"; exit 0',
            }.items():
                path = tools / name
                path.write_text('#!' + shutil.which('bash') + '\n' + body + '\n')
                path.chmod(0o755)
            env = dict(os.environ, PATH=f'{tools}:{os.environ["PATH"]}',
                       BUILD_UNEXPECTED_NPM=str(root / 'npm-ran'),
                       GLOVE80_BUILD_CACHE=str(root / 'cache'))
            result = subprocess.run(['bash', str(root / 'scripts/build-editor')],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source-export-failed', result.stderr)
            self.assertNotIn('Editor built and tested', result.stdout)
            self.assertFalse((root / 'npm-ran').exists())
