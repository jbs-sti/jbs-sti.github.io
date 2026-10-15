#!/usr/bin/env python3
"""Vérifier les ressources Quarto, sans exécuter leurs exemples de code."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from commun import ROOT, index_de_section, load_schema, read_source, validate, yaml

MAX_SIZE = 5_000_000

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
    def handle_starttag(self, tag, attrs):
        if tag in ('img', 'image'):
            attrs = dict(attrs)
            source = attrs.get('src') or attrs.get('href') or attrs.get('xlink:href')
            if source:
                self.sources.append(source)


def check_body(body, path, root, first_line):
    errors = []
    def error(line, message):
        errors.append(f'ligne {line} : {message}')
    # Ignorer les commentaires et exemples de code lors des contrôles de contenu.
    body = re.sub(r'<!--.*?-->', lambda m: '\n' * m.group().count('\n'), body, flags=re.S)
    visible = []
    fence = None
    stack = []
    siblings = {}
    for line_no, line in enumerate(body.splitlines(), first_line):
        code = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            for _, entry in stack:
                entry['content'].append(line)
            if code and code[1][0] == fence[0] and len(code[1]) >= len(fence) and not code[2].strip():
                fence = None
            visible.append('')
            continue
        if code:
            for _, entry in stack:
                entry['content'].append(line)
            fence = code[1]
            info = code[2].strip()
            if info == '{=html}' and not any(entry['mode'] == 'html' for _, entry in stack):
                error(line_no, 'bloc brut HTML : le placer dans une paire HTML/PDF conditionnelle')
            if not info:
                error(line_no, 'bloc de code sans langage')
            elif info.startswith('{') and not re.match(r'^\{(?:\.\w+|=\w+)\b', info):
                error(line_no, 'bloc exécutable : utiliser un langage simple (python, bash, text…)')
            visible.append('')
            continue
        div = re.match(r'^\s*(:{3,})(.*)$', line)
        if div:
            attrs = div[2].strip()
            if not attrs:
                if not stack:
                    error(line_no, 'fermeture de bloc ::: sans ouverture')
                else:
                    stack.pop()
            else:
                parent = tuple(item[0] for item in stack)
                mode = None
                if '.content-visible' in attrs:
                    if re.search(r'(?<![\w-])when-format\s*=\s*["\']?html\b', attrs):
                        mode = 'html'
                    elif re.search(r'(?<![\w-])unless-format\s*=\s*["\']?html\b', attrs):
                        mode = 'pdf'
                entry = {'mode':mode, 'line':line_no, 'content':[]}
                siblings.setdefault(parent, []).append(entry)
                stack.append((line_no, entry))
        else:
            for _, entry in stack:
                entry['content'].append(line)
        visible.append(line)
    if fence:
        error(first_line, 'bloc de code non fermé')
    for line_no, _ in stack:
        error(line_no, 'bloc ::: non fermé')
    # Paire de blocs adjacents au même niveau ; accepter les deux ordres.
    for entries in siblings.values():
        used = set()
        for i, entry in enumerate(entries):
            if entry['mode'] != 'html':
                continue
            partner = next((j for j in (i+1, i-1) if 0 <= j < len(entries)
                            and j not in used and entries[j]['mode'] == 'pdf'), None)
            if partner is None:
                error(entry['line'], 'bloc HTML sans équivalent PDF adjacent au même niveau')
            else:
                used.add(partner)
                if not any(line.strip() for line in entries[partner]['content']):
                    error(entries[partner]['line'], 'équivalent PDF vide')
    text = '\n'.join(visible)
    references = dict(re.findall(r'^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?', text, re.M))
    images = []
    for match in re.finditer(r'!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:[^\n]*?)\)', text):
        images.append(match[2] or match[3])
    for match in re.finditer(r'!\[([^\]]*)\](?:\[([^\]]*)\])?', text):
        if text[match.end():].startswith('('):
            continue
        key = match[2] or match[1]
        if key not in references:
            error(first_line + text[:match.start()].count('\n'), f'référence image non définie : {key}')
        else:
            images.append(references[key])
    parser = Images()
    parser.feed(text)
    images.extend(parser.sources)
    for source in images:
        url = urlsplit(source)
        if url.scheme or url.netloc:
            continue
        decoded = unquote(url.path)
        target = root / decoded.lstrip('/') if decoded.startswith('/') else path.parent / decoded
        if not target.is_file():
            error(first_line, f'image locale absente : {source}')
    for match in re.finditer(r'<iframe\b[^>]*>', text, re.I | re.S):
        if re.search(r'(?:www\.)?youtube\.com', match.group(), re.I):
            error(first_line + text[:match.start()].count('\n'), 'iframe YouTube : utiliser youtube-nocookie.com')
    return errors


def check_resource(path, root, schema):
    errors = []
    rel = path.relative_to(root)
    parts = rel.parts
    formation = parts[0]
    expected = 4 if formation == 'snt' else 5
    if len(parts) != expected:
        errors.append('chemin : nombre de niveaux incorrect')
    else:
        domaine = 'snt' if formation == 'snt' else parts[1]
        chapitre, folder = parts[-3:-1]
        if domaine not in schema['properties']['domaine']['enum'] or (formation != 'snt' and domaine == 'snt'):
            errors.append('chemin : domaine non autorisé')
        if not re.fullmatch(schema['x-chapitre-pattern'], chapitre):
            errors.append('chemin : chapitre attendu NN-nom-sans-accents')
        kinds = schema['properties']['type']['enum']
        kind = next((k for k in kinds if folder.startswith(k + '-')), None)
        if not kind or not re.fullmatch(schema['x-sujet-pattern'], folder[len(kind)+1:]):
            errors.append('chemin : dossier attendu <type>-<sujet>')
    try:
        metadata, body, first_line = read_source(path)
        errors.extend(validate(metadata, schema))
        if isinstance(metadata, dict) and len(parts) == expected:
            if metadata.get('domaine') != domaine:
                errors.append('domaine incohérent avec le chemin')
            if metadata.get('type') != kind:
                errors.append('type incohérent avec le chemin')
            if not str(metadata.get('chapitre', '')).startswith(chapitre[:2] + ' — '):
                errors.append('chapitre incohérent : attendu « NN — Titre »')
            categories = metadata.get('categories', [])
            if isinstance(categories, list) and (kind not in categories or domaine not in categories):
                errors.append('categories doit contenir le type et le domaine')
        errors.extend(check_body(body, path, root, first_line))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f'lecture : {exc}')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--racine', type=Path, default=ROOT, help='dépôt à vérifier (défaut : dépôt du script)')
    args = parser.parse_args(argv)
    root = args.racine.resolve()
    if not root.is_dir():
        parser.error('racine inexistante')
    schema = load_schema()
    count = failures = 0
    for formation in schema['x-formations']:
        base = root / formation
        if not base.exists():
            continue
        # Détecter aussi les dossiers de ressource privés de leur source unique.
        depth = 2 if formation == 'snt' else 3
        kinds = schema['properties']['type']['enum']
        for folder in sorted(base.rglob('*')):
            if (folder.is_dir() and len(folder.relative_to(base).parts) == depth
                    and any(folder.name.startswith(kind + '-') for kind in kinds)
                    and not (folder / 'index.qmd').is_file()):
                print(f'ERREUR {folder.relative_to(root)} : index.qmd absent')
                failures += 1
        for path in sorted(base.rglob('index.qmd')):
            if index_de_section(path, base, schema):
                continue
            count += 1
            errors = check_resource(path, root, schema)
            for error in errors:
                print(f'ERREUR {path.relative_to(root)} : {error}')
            failures += len(errors)
    # Toute pièce jointe dans les formations est soumise au plafond, même hors img/.
    for formation in schema['x-formations']:
        for path in sorted((root / formation).rglob('*')):
            if path.is_file() and path.stat().st_size > MAX_SIZE:
                print(f'ERREUR {path.relative_to(root)} : fichier > 5 Mo ({path.stat().st_size} octets)')
                failures += 1
    print(f'{count} ressource(s) contrôlée(s), {failures} erreur(s).')
    return 1 if failures else 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'ERREUR : {exc}', file=sys.stderr)
        sys.exit(1)
