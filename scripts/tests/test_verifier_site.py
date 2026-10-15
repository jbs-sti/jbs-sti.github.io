"""Tests du verrou de publication avec de vrais petits PDF générés en mémoire."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

SCRIPTS = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.resource = self.root / 'bts1/reseaux/04-couche-liaison/cours-test'
        self.resource.mkdir(parents=True)
        text = (SCRIPTS.parent / '_templates/cours.qmd').read_text()
        text = text.replace('draft: true', 'draft: false').replace('00 — À préciser', '04 — Couche liaison')
        self.source = self.resource / 'index.qmd'
        self.source.write_text(text)
        self.output = self.root / '_site' / self.resource.relative_to(self.root)
        self.output.mkdir(parents=True)
        self.html = self.output / 'index.html'
        self.pdf = self.output / 'index.pdf'
        self.html.write_text('<!doctype html><html><body><h1>Cours</h1></body></html>')
        self.write_pdf()

    def write_pdf(self, count=1, encrypted=False, invalid_page=False):
        writer = PdfWriter()
        for _ in range(count):
            page = writer.add_blank_page(width=595, height=842)
            contents = DecodedStreamObject()
            contents.set_data(b'q\nQ\n')
            page[NameObject('/Contents')] = writer._add_object(contents)
            if invalid_page:
                page[NameObject('/Type')] = NameObject('/NotAPage')
        if encrypted:
            writer.encrypt('mot-de-passe')
        with self.pdf.open('wb') as output:
            writer.write(output)

    def run_check(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPTS / 'verifier_site.py'),
                               '--racine', str(self.root), *extra], capture_output=True, text=True)

    def test_valid_one_and_multiple_pages(self):
        for count in (1, 3):
            self.write_pdf(count=count)
            result = self.run_check()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f'({count} page(s))', result.stdout)

    def test_missing_html_pdf_and_site(self):
        self.html.unlink()
        self.pdf.unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('HTML absente', result.stdout)
        self.assertIn('PDF absent', result.stdout)
        result = self.run_check('--site', str(self.root / 'absent'))
        self.assertEqual(result.returncode, 1)
        self.assertIn('dossier de rendu absent', result.stdout)

    def test_empty_html_and_quarto_draft_placeholder(self):
        for content in ('', '<html></html>', '<html><body> </body></html>',
                        '<html><body><script>console.log(42)</script></body></html>'):
            self.html.write_text(content)
            result = self.run_check()
            self.assertEqual(result.returncode, 1, content)
            self.assertIn('HTML vide', result.stdout)

    def test_corrupt_empty_truncated_pdf(self):
        original = self.pdf.read_bytes()
        for data in (b'', b'pas un PDF', b'%PDF-1.7\n%%EOF\n', original[:-20]):
            self.pdf.write_bytes(data)
            result = self.run_check()
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn('ERREUR', result.stdout)

    def test_zero_pages_and_encryption(self):
        self.write_pdf(count=0)
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('sans page', result.stdout)
        self.write_pdf(encrypted=True)
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('chiffré', result.stdout)

    def test_draft_ignored_and_invalid_metadata_rejected(self):
        self.source.write_text(self.source.read_text().replace('draft: false', 'draft: true'))
        self.html.unlink()
        self.pdf.unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('1 brouillon(s) ignoré(s)', result.stdout)
        self.source.write_text(self.source.read_text().replace('draft: true', 'draft: inconnu'))
        self.assertEqual(self.run_check().returncode, 1)

    def test_section_indexes_ignored_but_not_misplaced_resource(self):
        # Index de formation, de domaine et de chapitre : pages de navigation,
        # sans métadonnées de ressource et sans PDF attendu.
        section = '---\ntitle: "Section"\nformat:\n  html: default\n---\n'
        for folder in ('bts1', 'bts1/reseaux', 'bts1/reseaux/04-couche-liaison'):
            (self.root / folder / 'index.qmd').write_text(section)
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('1 ressource(s) publiable(s)', result.stdout)
        # Un dossier de ressource mal placé reste contrôlé.
        egare = self.root / 'bts1' / 'cours-egare'
        egare.mkdir()
        (egare / 'index.qmd').write_text(section)
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('cours-egare', result.stdout)

    def test_snt_and_external_site_directory(self):
        snt = self.root / 'snt/01-internet/fiche-ip'
        snt.mkdir(parents=True)
        text = self.source.read_text().replace('type: cours', 'type: fiche')
        text = text.replace('domaine: reseaux', 'domaine: snt').replace('categories: [cours, reseaux]', 'categories: [fiche, snt]')
        text = text.replace('04 — Couche liaison', '01 — Internet')
        (snt / 'index.qmd').write_text(text)
        outputs = self.root / '_site' / snt.relative_to(self.root)
        outputs.mkdir(parents=True)
        (outputs / 'index.html').write_bytes(self.html.read_bytes())
        (outputs / 'index.pdf').write_bytes(self.pdf.read_bytes())
        self.assertEqual(self.run_check().returncode, 0)
        external = self.root / 'rendu-personnalise'
        (self.root / '_site').rename(external)
        result = self.run_check('--site', str(external))
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
