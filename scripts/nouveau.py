#!/usr/bin/env python3
"""Créer une ressource en brouillon à partir du gabarit du dépôt."""
import argparse
from datetime import date
from pathlib import Path
import re
import sys

from commun import ROOT, load_schema, read_source, validate, yaml


def main(argv=None):
    schema = load_schema()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('formation', choices=schema['x-formations'])
    parser.add_argument('segments', nargs='+', metavar='DOMAINE/CHAPITRE/SUJET')
    parser.add_argument('--type', required=True, choices=schema['properties']['type']['enum'])
    args = parser.parse_args(argv)
    if args.formation == 'snt':
        if len(args.segments) != 2:
            parser.error('SNT : snt <NN-theme> <sujet> --type <type> (sans domaine)')
        chapitre, sujet = args.segments
        domaine = 'snt'
        base = ROOT / 'snt'
    else:
        if len(args.segments) != 3:
            parser.error('BTS : <formation> <domaine> <NN-chapitre> <sujet> --type <type>')
        domaine, chapitre, sujet = args.segments
        if domaine not in schema['properties']['domaine']['enum'] or domaine == 'snt':
            parser.error('Domaine BTS non autorisé')
        base = ROOT / args.formation / domaine
    for value, pattern, label in [(chapitre, schema['x-chapitre-pattern'], 'chapitre'),
                                  (sujet, schema['x-sujet-pattern'], 'sujet')]:
        if not re.fullmatch(pattern, value):
            parser.error(f'{label} invalide : {value}')
    target = base / chapitre / f'{args.type}-{sujet}'
    # Refuser une sortie du dépôt via un lien symbolique préexistant.
    if not target.resolve().is_relative_to(ROOT.resolve()):
        parser.error('Le chemin sort du dépôt')
    template = ROOT / '_templates' / f'{args.type}.qmd'
    metadata, body, _ = read_source(template)
    metadata.update(title=sujet.replace('-', ' ').capitalize(),
                    domaine=domaine, chapitre=chapitre[:2] + ' — ' + chapitre[3:].replace('-', ' ').capitalize(),
                    categories=[args.type, domaine], **{'mots-cles':[sujet.replace('-', ' ')],
                    'date-modified':date.today().isoformat(), 'draft':True})
    errors = validate(metadata, schema)
    if errors:
        raise ValueError('\n'.join(errors))
    content = '---\n' + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False) + '---\n\n' + body
    # mkdir sans exist_ok rend le refus d'écrasement atomique.
    target.mkdir(parents=True)
    (target / 'img').mkdir()
    (target / 'fichiers').mkdir()
    (target / 'index.qmd').write_text(content, encoding='utf-8')
    print(f'Ressource créée : {target.relative_to(ROOT)}/index.qmd (draft: true)')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(1)
