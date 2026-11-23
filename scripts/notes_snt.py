#!/usr/bin/env python3
"""Chiffrer les notes de SNT pour la rubrique « Évaluation » du site.

Lit le classeur de l'enseignant (une feuille par classe) et écrit
`snt/evaluation/notes.json`, où les notes de chaque élève sont chiffrées
(AES-256-GCM) avec une clé tirée de son prénom et de son code personnel
(PBKDF2-SHA256). Le fichier ne contient aucun nom en clair : la page
`snt/evaluation/` refait la même dérivation dans le navigateur de l'élève.

Chaque élève reçoit un code aléatoire de 8 caractères (XXXX-XXXX), gardé d'une fois
sur l'autre dans un fichier privé (par défaut `codes_snt.csv`, à côté du
classeur). Un élève ajouté au classeur reçoit un nouveau code ; les codes
existants ne changent jamais. Le script écrit aussi `coupons_snt.html`
(à côté du classeur) : un coupon par élève, à imprimer et à découper.

Le classeur, les codes et les coupons ne doivent JAMAIS être versionnés :
ils restent hors du dépôt (le script refuse un chemin dans le dépôt).

Format attendu de chaque feuille :
- une ligne d'en-têtes dont la première cellule vaut « N° » ;
- des colonnes « Nom » et « Prénom » ;
- une colonne par évaluation, puis une colonne « Moyenne » (facultative) ;
- une note est un nombre, « ABS », ou une cellule vide (pas encore notée).

Utilisation (dépendances locales : scripts/requirements-notes.txt) :

    .venv/bin/python scripts/notes_snt.py ~/bulletins-notes/Notes_SNT_Secondes.xlsx
"""
import argparse
import base64
import csv
from datetime import date
import hashlib
import html
import json
import os
from pathlib import Path
import re
import secrets
import sys
import unicodedata

try:
    import openpyxl
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise SystemExit('Dépendances manquantes : .venv/bin/pip install -r scripts/requirements-notes.txt') from exc

ROOT = Path(__file__).resolve().parents[1]
SORTIE = ROOT / 'snt' / 'evaluation' / 'notes.json'
ADRESSE = 'https://jbs-sti.github.io/snt/evaluation/'
ITERATIONS = 600_000
VERSION = 1
# Sans 0/O, 1/I/L : rien qui se confonde à la lecture d'un coupon.
# 31 caractères, 8 positions : 8,5 × 10^11 codes possibles ; avec PBKDF2 à
# 600 000 itérations, des années de calcul sur carte graphique par élève.
ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
LONGUEUR_CODE = 8


def normaliser_prenom(prenom):
    """Même règle que evaluation.js : sans accents, minuscules, lettres a-z seules."""
    texte = unicodedata.normalize('NFD', str(prenom))
    texte = re.sub('[̀-ͯ]', '', texte).lower()
    return re.sub('[^a-z]', '', texte)


def normaliser_code(code):
    """Même règle que evaluation.js : majuscules, lettres et chiffres seuls."""
    return re.sub('[^A-Z0-9]', '', str(code).upper())


def nouveau_code():
    code = ''.join(secrets.choice(ALPHABET) for _ in range(LONGUEUR_CODE))
    return f'{code[:4]}-{code[4:]}'


def deriver(prenom, code, sel, iterations):
    """64 octets : 32 pour la clé AES, 16 pour l'identifiant de l'entrée."""
    secret = f'{normaliser_prenom(prenom)}|{normaliser_code(code)}'.encode()
    bloc = hashlib.pbkdf2_hmac('sha256', secret, sel, iterations, dklen=64)
    return bloc[:32], bloc[32:48].hex()


def note(valeur):
    if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
        return None
    if isinstance(valeur, str):
        texte = valeur.strip().upper()
        if texte == 'ABS':
            return 'ABS'
        try:
            return round(float(texte.replace(',', '.')), 2)
        except ValueError:
            raise ValueError(f'note illisible : {valeur!r}')
    return round(float(valeur), 2)


def titre_colonne(valeur):
    lignes = [l.strip() for l in str(valeur).splitlines() if l.strip()]
    return ' · '.join(lignes)


def lire_feuille(ws):
    """Rend (élèves, titres des évaluations)."""
    lignes = list(ws.iter_rows(values_only=True))
    entete = next((i for i, l in enumerate(lignes) if l and l[0] == 'N°'), None)
    if entete is None:
        raise ValueError('ligne d\'en-têtes « N° » introuvable')
    titres = [str(v).strip() if v is not None else '' for v in lignes[entete]]
    bas = [normaliser_prenom(t) for t in titres]
    try:
        c_nom, c_prenom = bas.index('nom'), bas.index('prenom')
    except ValueError:
        raise ValueError('colonnes « Nom » et « Prénom » introuvables')
    c_moy = next((i for i, t in enumerate(bas) if t.startswith('moyenne')), None)
    # Une éventuelle colonne de date de naissance n'est pas une évaluation.
    ignorees = {0, c_nom, c_prenom, c_moy} | {i for i, t in enumerate(bas) if 'naissance' in t}
    c_evals = [i for i, t in enumerate(titres) if t and i not in ignorees]
    evaluations = [titre_colonne(lignes[entete][i]) for i in c_evals]

    eleves = []
    for numero, ligne in enumerate(lignes[entete + 1:], entete + 2):
        ligne = list(ligne) + [None] * (len(titres) - len(ligne))
        nom, prenom = ligne[c_nom], ligne[c_prenom]
        if not (isinstance(nom, str) and nom.strip() and isinstance(prenom, str) and prenom.strip()):
            continue
        try:
            notes = [note(ligne[i]) for i in c_evals]
        except ValueError as exc:
            raise ValueError(f'ligne {numero} : {exc}')
        chiffrees = [n for n in notes if isinstance(n, float)]
        moyenne = ligne[c_moy] if c_moy is not None else None
        if not isinstance(moyenne, (int, float)):
            moyenne = sum(chiffrees) / len(chiffrees) if chiffrees else None
        eleves.append({'nom': nom.strip(), 'prenom': prenom.strip(), 'notes': notes,
                       'moyenne': None if moyenne is None else round(float(moyenne), 2)})
    return eleves, evaluations


def moyenne_classe(eleves, j):
    valeurs = [e['notes'][j] for e in eleves if isinstance(e['notes'][j], float)]
    return round(sum(valeurs) / len(valeurs), 2) if valeurs else None


def cle_eleve(classe, nom, prenom):
    return (classe.strip(), normaliser_prenom(nom), normaliser_prenom(prenom))


def lire_codes(chemin):
    if not chemin.exists():
        return {}
    with chemin.open(encoding='utf-8-sig', newline='') as f:
        return {cle_eleve(l['classe'], l['nom'], l['prenom']): l
                for l in csv.DictReader(f, delimiter=';')}


def ecrire_codes(chemin, codes):
    lignes = sorted(codes.values(), key=lambda l: (l['classe'], l['nom'], l['prenom']))
    with chemin.open('w', encoding='utf-8-sig', newline='') as f:
        ecrivain = csv.DictWriter(f, fieldnames=['classe', 'nom', 'prenom', 'code'], delimiter=';',
                                  lineterminator='\n')
        ecrivain.writeheader()
        ecrivain.writerows({k: l[k] for k in ('classe', 'nom', 'prenom', 'code')} for l in lignes)
    chemin.chmod(0o600)


def ecrire_coupons(chemin, classes):
    """Une page imprimable : un coupon par élève, une classe par page."""
    blocs = []
    for classe, eleves in classes:
        coupons = ''.join(
            '<div class="coupon">'
            f'<p class="nom">{html.escape(e["prenom"])} {html.escape(e["nom"])} — {html.escape(classe)}</p>'
            '<p>Tes notes de SNT : <strong>jbs-sti.github.io</strong> › SNT › Évaluation</p>'
            f'<p>Prénom : <strong>{html.escape(e["prenom"])}</strong> · Code : '
            f'<strong class="code">{html.escape(e["code"])}</strong></p>'
            '<p class="petit">Garde ce code pour toi : il ne change pas de l\'année.</p>'
            '</div>' for e in eleves)
        blocs.append(f'<section><h1>SNT — {html.escape(classe)}</h1>{coupons}</section>')
    chemin.write_text(f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Codes SNT</title>
<style>
body {{ font-family: sans-serif; margin: 1cm; }}
section {{ page-break-after: always; }}
h1 {{ font-size: 14pt; }}
.coupon {{ border: 1px dashed #000; padding: 0.3cm 0.5cm; margin-bottom: 0.25cm; break-inside: avoid; }}
.coupon p {{ margin: 0.1cm 0; }}
.nom {{ font-weight: bold; }}
.code {{ font-family: monospace; font-size: 15pt; letter-spacing: 0.15em; }}
.petit {{ font-size: 8pt; }}
</style></head><body>
{''.join(blocs)}
</body></html>
""", encoding='utf-8')
    chemin.chmod(0o600)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('classeur', type=Path, help='classeur .xlsx des notes (hors du dépôt)')
    parser.add_argument('--codes', type=Path, help='fichier privé des codes (défaut : codes_snt.csv à côté du classeur)')
    parser.add_argument('--coupons', type=Path, help='coupons à imprimer (défaut : coupons_snt.html à côté du classeur)')
    parser.add_argument('--sortie', type=Path, default=SORTIE)
    parser.add_argument('--iterations', type=int, default=ITERATIONS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    classeur = args.classeur.resolve()
    codes_csv = (args.codes or classeur.with_name('codes_snt.csv')).resolve()
    coupons = (args.coupons or classeur.with_name('coupons_snt.html')).resolve()
    for nom, chemin in (('le classeur', classeur), ('le fichier des codes', codes_csv), ('les coupons', coupons)):
        if ROOT in chemin.parents:
            parser.error(f'{nom} est dans le dépôt ({chemin}) : choisissez un chemin hors du dépôt')

    wb = openpyxl.load_workbook(classeur, data_only=True)
    codes = lire_codes(codes_csv)
    utilises = {normaliser_code(l['code']) for l in codes.values()}
    sel = os.urandom(16)
    entrees, erreurs, classes, nouveaux = {}, [], [], 0
    for ws in wb.worksheets:
        try:
            eleves, evaluations = lire_feuille(ws)
        except ValueError as exc:
            erreurs.append(f'{ws.title} : {exc}')
            continue
        moyennes = [moyenne_classe(eleves, j) for j in range(len(evaluations))]
        for e in eleves:
            cle = cle_eleve(ws.title, e['nom'], e['prenom'])
            if cle not in codes:
                code = nouveau_code()
                while code in utilises:
                    code = nouveau_code()
                utilises.add(code)
                codes[cle] = {'classe': ws.title, 'nom': e['nom'], 'prenom': e['prenom'], 'code': code}
                nouveaux += 1
            e['code'] = codes[cle]['code']
            cle_aes, ident = deriver(e['prenom'], e['code'], sel, args.iterations)
            if ident in entrees:
                erreurs.append(f'{ws.title} : identifiant en double pour {e["prenom"]} {e["nom"]}')
                continue
            contenu = {
                'classe': ws.title, 'nom': e['nom'], 'prenom': e['prenom'],
                'evaluations': [{'titre': t, 'note': n, 'moyenne_classe': m}
                                for t, n, m in zip(evaluations, e['notes'], moyennes)],
                'moyenne': e['moyenne'],
            }
            iv = os.urandom(12)
            donnees = AESGCM(cle_aes).encrypt(iv, json.dumps(contenu, ensure_ascii=False).encode(), ident.encode())
            entrees[ident] = {'iv': base64.b64encode(iv).decode(), 'donnees': base64.b64encode(donnees).decode()}
        classes.append((ws.title, eleves))
        print(f'{ws.title} : {len(eleves)} élève(s) chiffré(s)')
    if erreurs:
        for e in erreurs:
            print(f'ERREUR {e}', file=sys.stderr)
        return 1

    ecrire_codes(codes_csv, codes)
    ecrire_coupons(coupons, classes)
    # Entrées triées par identifiant (pseudo-aléatoire) : leur position ne
    # révèle ni la classe ni l'ordre alphabétique du classeur.
    sortie = {'version': VERSION, 'mise_a_jour': date.today().isoformat(),
              'kdf': {'nom': 'PBKDF2-SHA256', 'iterations': args.iterations,
                      'sel': base64.b64encode(sel).decode()},
              'entrees': dict(sorted(entrees.items()))}
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(sortie, indent=1) + '\n', encoding='utf-8')
    print(f'{len(entrees)} élève(s) au total, dont {nouveaux} nouveau(x) code(s).')
    print(f'Notes chiffrées : {args.sortie}')
    print(f'Codes (privé)   : {codes_csv}')
    print(f'Coupons         : {coupons}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
