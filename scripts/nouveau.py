#!/usr/bin/env python3
"""Créer une ressource en brouillon à partir du gabarit du dépôt."""
import argparse
from datetime import date
from pathlib import Path
import re
import sys

from commun import ROOT, load_schema, read_source, validate, yaml

# Page d'index d'un domaine ou d'un chapitre. Elle ne porte aucun contenu :
# elle donne son titre français à la section dans la barre latérale (sans
# elle, Quarto affiche le nom du dossier, sans accent et mal capitalisé) et
# liste les ressources qu'elle contient.
SECTION = '''---
title: "{titre}"
description: "{description}"
format:
  html: default
listing:
  # Seules les ressources, pas les index de domaine ni de chapitre.
  contents: "{contenu}"
  type: grid
  categories: true
  sort: "order"
  fields: [title, description, categories]
---
'''


def creer_index(dossier, titre, description, contenu):
    """Créer l'index d'une section s'il manque ; renvoyer son chemin ou None."""
    index = dossier / 'index.qmd'
    dossier.mkdir(parents=True, exist_ok=True)
    try:
        # 'x' rend le refus d'écrasement atomique : un index déjà relu par
        # l'enseignant n'est jamais remplacé.
        with index.open('x', encoding='utf-8') as fichier:
            fichier.write(SECTION.format(titre=titre, description=description, contenu=contenu))
    except FileExistsError:
        return None
    return index


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
    titre_chapitre = chapitre[:2] + ' — ' + chapitre[3:].replace('-', ' ').capitalize()
    metadata.update(title=sujet.replace('-', ' ').capitalize(),
                    domaine=domaine, chapitre=titre_chapitre,
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
    # Index des sections traversées : la navigation reste automatique, mais
    # les titres sont déduits des noms de dossiers, donc sans accents.
    sections = []
    if args.formation != 'snt':
        sections.append((base, domaine.capitalize(),
                         f'Ressources du domaine {domaine} de la formation.', '*/*/index.qmd'))
    sections.append((base / chapitre, titre_chapitre,
                     f'Ressources du chapitre « {titre_chapitre} ».', '*/index.qmd'))
    for dossier, titre, description, contenu in sections:
        index = creer_index(dossier, titre, description, contenu)
        if index:
            print(f'Index de section créé : {index.relative_to(ROOT)} '
                  f'(titre « {titre} » : à relire, accents compris)')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(1)
