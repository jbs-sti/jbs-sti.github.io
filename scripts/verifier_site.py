#!/usr/bin/env python3
"""Contrôler les sorties HTML/PDF des ressources publiables après le rendu."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import sys

from commun import ROOT, load_schema, read_source, validate, yaml

try:
    from pypdf import PdfReader
except ImportError as exc:
    raise SystemExit('pypdf manque : python3 -m pip install -r scripts/requirements.txt') from exc


class PageHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html = False
        self.body = False
        self.in_body = False
        self.content = False
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'html':
            self.html = True
        if tag == 'body':
            self.body = self.in_body = True
        if self.in_body:
            if tag in ('script', 'style'):
                self.hidden += 1
            elif tag in ('img', 'svg', 'video', 'canvas', 'iframe') and not self.hidden:
                self.content = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        if tag == 'body':
            self.in_body = False

    def handle_data(self, data):
        if self.in_body and not self.hidden and data.strip():
            self.content = True


def check_html(path):
    if not path.is_file():
        raise ValueError('page HTML absente')
    parser = PageHTML()
    parser.feed(path.read_text(encoding='utf-8'))
    parser.close()
    if not (parser.html and parser.body and parser.content):
        raise ValueError('page HTML vide ou dépourvue de contenu dans <body>')


def check_pdf(path):
    if not path.is_file():
        raise ValueError('PDF absent')
    # Le mode strict refuse les réparations silencieuses de structure.
    with path.open('rb') as stream:
        reader = PdfReader(stream, strict=True)
        if reader.is_encrypted:
            raise ValueError('PDF chiffré : relecture publique impossible')
        count = len(reader.pages)
        if count < 1:
            raise ValueError('PDF sans page')
        for page in reader.pages:
            if page.get('/Type') != '/Page':
                raise ValueError('objet de page PDF invalide')
            if len(page.mediabox) != 4 or page.mediabox.width <= 0 or page.mediabox.height <= 0:
                raise ValueError('dimensions de page PDF invalides')
            # Les flux sont lus paresseusement : forcer leur décodage.
            contents = page.get_contents()
            if contents is not None:
                contents.get_data()
        return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--racine', type=Path, default=ROOT, help='racine des sources')
    parser.add_argument('--site', type=Path, help='sortie du rendu (défaut : <racine>/_site)')
    args = parser.parse_args(argv)
    root = args.racine.resolve()
    site = args.site.resolve() if args.site else root / '_site'
    if not root.is_dir():
        parser.error('racine des sources inexistante')
    schema = load_schema()
    failures = published = drafts = 0
    if not site.is_dir():
        print(f'ERREUR {site} : dossier de rendu absent')
        failures += 1
    for formation in schema['x-formations']:
        base = root / formation
        for source in sorted(base.rglob('index.qmd')):
            if source.parent == base:
                continue
            relative = source.relative_to(root)
            try:
                metadata, _, _ = read_source(source)
                errors = validate(metadata, schema)
                if errors:
                    raise ValueError('; '.join(errors))
                if metadata['draft'] is True:
                    drafts += 1
                    continue
            except (OSError, ValueError, yaml.YAMLError) as exc:
                print(f'ERREUR {relative} : métadonnées illisibles ou invalides : {exc}')
                failures += 1
                continue
            published += 1
            output = site / relative.parent
            for extension, check in (('html', check_html), ('pdf', check_pdf)):
                path = output / f'index.{extension}'
                try:
                    result = check(path)
                    detail = f' ({result} page(s))' if extension == 'pdf' else ''
                    print(f'OK {path.relative_to(site)}{detail}')
                except Exception as exc:
                    # Un fichier PDF malformé peut provoquer plusieurs classes
                    # d'erreurs de lecture ; chacune doit faire échouer le contrôle.
                    print(f'ERREUR {path.relative_to(site)} : {exc}')
                    failures += 1
    print(f'{published} ressource(s) publiable(s), {drafts} brouillon(s) ignoré(s), {failures} erreur(s).')
    return 1 if failures else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(1)
