"""Vérifier que les workflows conservent le verrou avant publication."""
from pathlib import Path
import re
import unittest

import yaml

WORKFLOWS = Path(__file__).resolve().parents[2] / '.github/workflows'


class WorkflowTests(unittest.TestCase):
    def load(self, name):
        # BaseLoader garde la clé YAML « on » comme chaîne.
        return yaml.load((WORKFLOWS / name).read_text(), Loader=yaml.BaseLoader)

    def test_same_checks_before_uploading_pages(self):
        verifier = self.load('verifier.yml')['jobs']['verifier']
        publisher = self.load('publier.yml')['jobs']['build']
        commands = lambda job: [step['run'] for step in job['steps'] if 'run' in step]
        self.assertEqual(commands(verifier), commands(publisher))
        expected = ['python scripts/verifier_sources.py', 'quarto render --no-execute',
                    'python scripts/verifier_site.py']
        sequence = commands(publisher)
        self.assertEqual(sequence[-3:], expected)
        steps = publisher['steps']
        upload = next(i for i, step in enumerate(steps) if 'actions/upload-pages-artifact@' in step.get('uses', ''))
        check = next(i for i, step in enumerate(steps) if step.get('run') == expected[-1])
        self.assertGreater(upload, check)
        self.assertNotIn('if', steps[upload])  # condition implicite success()
        self.assertNotIn('continue-on-error', publisher)
        for step in steps:
            self.assertNotIn('continue-on-error', step)

    def test_pr_read_only_and_deploy_requires_main_build(self):
        verifier = self.load('verifier.yml')
        self.assertIn('pull_request', verifier['on'])
        self.assertEqual(verifier['permissions'], {'contents':'read'})
        self.assertEqual(set(verifier['jobs']), {'verifier'})
        self.assertEqual(verifier['jobs']['verifier']['name'], 'Vérifier les ressources')
        publisher = self.load('publier.yml')
        self.assertEqual(publisher['jobs']['deploy']['needs'], 'build')
        self.assertEqual(publisher['jobs']['build']['if'], "github.ref == 'refs/heads/main'")
        self.assertEqual(publisher['permissions'], {'contents':'read'})
        self.assertEqual(publisher['jobs']['deploy']['permissions']['pages'], 'write')

    def test_pinned_tools_and_review_artifacts(self):
        for filename, jobname in (('verifier.yml','verifier'), ('publier.yml','build')):
            workflow = self.load(filename)
            job = workflow['jobs'][jobname]
            self.assertEqual(job['runs-on'], 'ubuntu-24.04')
            for each in workflow['jobs'].values():
                for step in each['steps']:
                    if 'uses' in step:
                        self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')
            setup = next(step for step in job['steps'] if step.get('uses','').startswith('quarto-dev/'))
            self.assertEqual(setup['with']['version'], '1.10.19')
            python = next(step for step in job['steps'] if step.get('uses','').startswith('actions/setup-python@'))
            self.assertRegex(python['with']['python-version'], r'^\d+\.\d+\.\d+$')
            artifact = next(step for step in job['steps'] if step.get('uses','').startswith('actions/upload-artifact@'))
            self.assertEqual(artifact['with']['path'], '_site/**/*.pdf')
            self.assertEqual(artifact['if'], '${{ !cancelled() }}')


if __name__ == '__main__':
    unittest.main()
