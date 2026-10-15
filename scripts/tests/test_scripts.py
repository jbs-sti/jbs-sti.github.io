"""Tests d'intégration des garde-fous, sans modification des ressources réelles."""
from datetime import date
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from commun import check_schema, load_schema, read_source, validate, yaml
from verifier_sources import check_body

class ScriptsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ('scripts', '_schemas', '_templates'):
            shutil.copytree(SCRIPTS.parent / folder, self.root / folder,
                            ignore=shutil.ignore_patterns('__pycache__', 'tests'))

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(self.root / 'scripts' / script), *args],
                              capture_output=True, text=True, cwd=self.root.parent)

    def create(self, formation='bts1', kind='cours'):
        args = [formation, '01-internet', 'exemple'] if formation == 'snt' else [formation, 'reseaux', '04-couche-liaison', 'arp']
        result = self.run_script('nouveau.py', *args, '--type', kind)
        self.assertEqual(result.returncode, 0, result.stderr)
        base = self.root / formation
        if formation != 'snt':
            base = base / 'reseaux'
        return base / args[-2] / f'{kind}-{args[-1]}' / 'index.qmd'

    def check(self):
        return self.run_script('verifier_sources.py', '--racine', str(self.root))

    def test_all_types_and_formations(self):
        for formation in ('snt', 'bts1', 'bts2'):
            for kind in ('cours', 'tp', 'exercices', 'fiche'):
                path = self.create(formation, kind)
                metadata, _, _ = read_source(path)
                self.assertIs(metadata['draft'], True)
                self.assertEqual(metadata['date-modified'], date.today().isoformat())
                self.assertTrue((path.parent / 'img').is_dir())
                self.assertTrue((path.parent / 'fichiers').is_dir())
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('12 ressource(s)', result.stdout)

    def test_missing_index_and_invalid_path(self):
        path = self.create()
        moved = path.parent.with_name('cours-Sujet-invalide')
        path.parent.rename(moved)
        self.assertIn('dossier attendu', self.check().stdout)
        (moved / 'index.qmd').unlink()
        self.assertIn('index.qmd absent', self.check().stdout)

    def test_section_indexes_created_then_preserved(self):
        self.create()
        domaine = self.root / 'bts1' / 'reseaux' / 'index.qmd'
        chapitre = self.root / 'bts1' / 'reseaux' / '04-couche-liaison' / 'index.qmd'
        for index, titre in ((domaine, 'Reseaux'), (chapitre, '04 — Couche liaison')):
            metadata, _, _ = read_source(index)
            self.assertEqual(metadata['title'], titre)
        # Un index relu par l'enseignant n'est jamais réécrit.
        chapitre.write_text('---\ntitle: "04 — Couche liaison"\n---\n', encoding='utf-8')
        result = self.run_script('nouveau.py', 'bts1', 'reseaux', '04-couche-liaison', 'dhcp', '--type', 'tp')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('listing', chapitre.read_text())
        # Les index de section ne sont pas comptés comme des ressources.
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('2 ressource(s)', result.stdout)

    def test_existing_resource_unchanged(self):
        path = self.create()
        path.write_text('contenu à préserver')
        result = self.run_script('nouveau.py', 'bts1', 'reseaux', '04-couche-liaison', 'arp', '--type', 'cours')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_text(), 'contenu à préserver')

    def test_invalid_arguments_and_escape(self):
        for args in [('bts1','inconnu','04-liaison','arp'), ('bts1','reseaux','4-liaison','arp'),
                     ('bts1','reseaux','04-liaison','../arp'), ('snt','reseaux','01-internet','arp')]:
            result = self.run_script('nouveau.py', *args, '--type', 'cours')
            self.assertNotEqual(result.returncode, 0)
        (self.root / 'bts1').symlink_to(self.root.parent, target_is_directory=True)
        result = self.run_script('nouveau.py','bts1','reseaux','04-liaison','arp','--type','cours')
        self.assertNotEqual(result.returncode, 0)

    def test_multiple_errors_and_size_boundary(self):
        path = self.create()
        text = path.read_text().replace('draft: true', 'draft: oui').replace('domaine: reseaux','domaine: systemes')
        text += '\n![absente](img/manquante.svg)\n\n```\nsans langage\n```\n\n::: {.content-visible when-format="html"}\nWeb\n:::\n\n<iframe src="https://www.youtube.com/embed/test"></iframe>\n'
        path.write_text(text)
        large = path.parent / 'fichiers' / 'gros.bin'
        with large.open('wb') as output:
            output.truncate(5_000_000)
        self.assertNotIn('fichier > 5 Mo', self.check().stdout)
        with large.open('ab') as output:
            output.write(b'x')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        for expected in ('draft', 'incohérent', 'image locale absente','sans langage','sans équivalent PDF','youtube-nocookie', 'fichier > 5 Mo'):
            self.assertIn(expected, result.stdout)

    def test_yaml_duplicates_dates_types(self):
        path = self.create()
        path.write_text(path.read_text().replace('draft: true','draft: true\ndraft: false'))
        self.assertIn('dupliquée', self.check().stdout)
        schema = load_schema()
        for value in ('2026-02-30', '14/10/2026', '20261014'):
            self.assertTrue(validate(value, schema['properties']['date-modified']))
        self.assertTrue(validate(True, schema['properties']['order']))
        with self.assertRaises(ValueError):
            check_schema({'type':'string','maxLength':5})

    def test_pairs_nested_empty_and_code_ignored(self):
        path = self.root / 'index.qmd'
        valid = '''::: {.callout-note}
::: {.content-visible when-format="html"}
Web
:::
::: {.content-visible unless-format="html"}
Papier
:::
:::

```text
![exemple](absente.svg)
::: {.content-visible when-format="html"}
```
'''
        self.assertEqual(check_body(valid, path, self.root, 1), [])
        self.assertEqual(check_body(valid.replace('Papier', '```text\nVersion imprimable\n```'),path,self.root,1), [])
        self.assertTrue(check_body('```{=html}\n<p>Web seul</p>\n```',path,self.root,1))
        empty = valid.replace('Papier', '<!-- à compléter -->')
        self.assertTrue(any('vide' in error for error in check_body(empty,path,self.root,1)))
        other_parent = '''::: {.content-visible when-format="html"}
Web
:::
::: {.callout-note}
::: {.content-visible unless-format="html"}
Papier
:::
:::
'''
        self.assertTrue(any('sans équivalent' in error for error in check_body(other_parent,path,self.root,1)))
        executable = '```{python}\nprint(42)\n```\n'
        self.assertTrue(any('exécutable' in error for error in check_body(executable,path,self.root,1)))

    def test_images_reference_html_url_and_comments(self):
        image = self.root / 'image espace.svg'
        image.write_text('<svg/>')
        body = '''![direct](<image espace.svg>)
![référence][ok]
[ok]: image%20espace.svg
<img src="/image%20espace.svg">
![distante](https://example.com/image.svg)
<!-- ![ignorée](manquante.svg) -->
'''
        self.assertEqual(check_body(body,self.root/'index.qmd',self.root,1), [])
        self.assertTrue(check_body('![absente][non-definie]',self.root/'index.qmd',self.root,1))

if __name__ == '__main__':
    unittest.main()
