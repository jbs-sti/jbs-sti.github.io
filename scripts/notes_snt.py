#!/usr/bin/env python3
"""Chiffrer les notes de SNT pour la rubrique « Évaluation » du site.

Lit le classeur de l'enseignant (une feuille par classe) et écrit
`snt/evaluation/notes.json`, où les notes de chaque élève sont chiffrées
(AES-256-GCM) avec une clé tirée de son prénom et de sa date de naissance
(PBKDF2-SHA256). Le fichier ne contient aucun nom en clair : la page
`snt/evaluation/` refait la même dérivation dans le navigateur de l'élève.

Le classeur ne doit JAMAIS être versionné : il reste hors du dépôt.

Format attendu de chaque feuille :
- une ligne d'en-têtes dont la première cellule vaut « N° » ;
- des colonnes « Nom », « Prénom » et une colonne dont l'en-tête contient
  « naissance » (date Excel, ou texte jj/mm/aaaa ou jjmmaaaa) ;
- une colonne par évaluation, puis une colonne « Moyenne » (facultative) ;
- une note est un nombre, « ABS », ou une cellule vide (pas encore notée).

Utilisation (dépendances locales : scripts/requirements-notes.txt) :

    .venv/bin/python scripts/notes_snt.py ~/bulletins-notes/Notes_SNT_Secondes.xlsx

Limite connue : une date de naissance n'est pas un secret (environ
730 dates possibles pour une classe de seconde). La dérivation lente
ralentit les essais sans les empêcher.
"""
import argparse
import base64
import hashlib
from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

try:
    import openpyxl
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise SystemExit('Dépendances manquantes : .venv/bin/pip install -r scripts/requirements-notes.txt') from exc

ROOT = Path(__file__).resolve().parents[1]
SORTIE = ROOT / 'snt' / 'evaluation' / 'notes.json'
ITERATIONS = 600_000
VERSION = 1


def normaliser_prenom(prenom):
    """Même règle que evaluation.js : sans accents, minuscules, lettres a-z seules."""
    texte = unicodedata.normalize('NFD', str(prenom))
    texte = re.sub('[̀-ͯ]', '', texte).lower()
    return re.sub('[^a-z]', '', texte)


def normaliser_date(valeur):
    """Rend la date au format jjmmaaaa, ou None si illisible."""
    if isinstance(valeur, (datetime, date)):
        return valeur.strftime('%d%m%Y')
    if valeur is None:
        return None
    chiffres = re.sub(r'\D', '', str(valeur))
    if len(chiffres) != 8:
        return None
    try:
        datetime.strptime(chiffres, '%d%m%Y')
    except ValueError:
        return None
    return chiffres


def deriver(prenom, naissance, sel, iterations):
    """64 octets : 32 pour la clé AES, 16 pour l'identifiant de l'entrée."""
    secret = f'{normaliser_prenom(prenom)}|{naissance}'.encode()
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
    """Rend (élèves, titres des évaluations, avertissements)."""
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
    c_naiss = next((i for i, t in enumerate(bas) if 'naissance' in t), None)
    if c_naiss is None:
        raise ValueError('colonne « Date de naissance » introuvable')
    c_moy = next((i for i, t in enumerate(bas) if t.startswith('moyenne')), None)
    c_evals = [i for i, t in enumerate(titres)
               if t and i not in (0, c_nom, c_prenom, c_naiss, c_moy)]
    evaluations = [titre_colonne(lignes[entete][i]) for i in c_evals]

    eleves, avert = [], []
    for numero, ligne in enumerate(lignes[entete + 1:], entete + 2):
        ligne = list(ligne) + [None] * (len(titres) - len(ligne))
        nom, prenom = ligne[c_nom], ligne[c_prenom]
        if not (isinstance(nom, str) and nom.strip() and isinstance(prenom, str) and prenom.strip()):
            continue
        naissance = normaliser_date(ligne[c_naiss])
        if not naissance:
            # Gardé pour la moyenne de classe, mais sans accès à ses notes.
            avert.append(f'ligne {numero} : date de naissance absente ou illisible, élève sans accès')
        try:
            notes = [note(ligne[i]) for i in c_evals]
        except ValueError as exc:
            raise ValueError(f'ligne {numero} : {exc}')
        chiffrees = [n for n in notes if isinstance(n, float)]
        moyenne = ligne[c_moy] if c_moy is not None else None
        if not isinstance(moyenne, (int, float)):
            moyenne = sum(chiffrees) / len(chiffrees) if chiffrees else None
        eleves.append({'nom': nom.strip(), 'prenom': prenom.strip(), 'naissance': naissance,
                       'notes': notes, 'moyenne': None if moyenne is None else round(float(moyenne), 2)})
    return eleves, evaluations, avert


def moyenne_classe(eleves, j):
    valeurs = [e['notes'][j] for e in eleves if isinstance(e['notes'][j], float)]
    return round(sum(valeurs) / len(valeurs), 2) if valeurs else None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('classeur', type=Path, help='classeur .xlsx des notes (hors du dépôt)')
    parser.add_argument('--sortie', type=Path, default=SORTIE)
    parser.add_argument('--iterations', type=int, default=ITERATIONS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    classeur = args.classeur.resolve()
    if ROOT in classeur.parents:
        parser.error('le classeur est dans le dépôt : déplacez-le hors du dépôt avant de lancer le script')

    wb = openpyxl.load_workbook(classeur, data_only=True)
    sel = os.urandom(16)
    entrees, erreurs, total = {}, [], 0
    for ws in wb.worksheets:
        try:
            eleves, evaluations, avert = lire_feuille(ws)
        except ValueError as exc:
            erreurs.append(f'{ws.title} : {exc}')
            continue
        for a in avert:
            print(f'ATTENTION {ws.title}, {a}')
        moyennes = [moyenne_classe(eleves, j) for j in range(len(evaluations))]
        eleves_acces = [e for e in eleves if e['naissance']]
        for e in eleves_acces:
            cle, ident = deriver(e['prenom'], e['naissance'], sel, args.iterations)
            if ident in entrees:
                erreurs.append(f'{ws.title} : deux élèves ont le même prénom et la même date de naissance ({e["prenom"]})')
                continue
            contenu = {
                'classe': ws.title, 'nom': e['nom'], 'prenom': e['prenom'],
                'evaluations': [{'titre': t, 'note': n, 'moyenne_classe': m}
                                for t, n, m in zip(evaluations, e['notes'], moyennes)],
                'moyenne': e['moyenne'],
            }
            iv = os.urandom(12)
            donnees = AESGCM(cle).encrypt(iv, json.dumps(contenu, ensure_ascii=False).encode(), ident.encode())
            entrees[ident] = {'iv': base64.b64encode(iv).decode(), 'donnees': base64.b64encode(donnees).decode()}
            total += 1
        print(f'{ws.title} : {len(eleves_acces)} élève(s) chiffré(s) sur {len(eleves)}')
    if erreurs:
        for e in erreurs:
            print(f'ERREUR {e}', file=sys.stderr)
        return 1

    # Entrées triées par identifiant (pseudo-aléatoire) : leur position ne
    # révèle ni la classe ni l'ordre alphabétique du classeur.
    melange = dict(sorted(entrees.items()))
    sortie = {'version': VERSION, 'mise_a_jour': date.today().isoformat(),
              'kdf': {'nom': 'PBKDF2-SHA256', 'iterations': args.iterations,
                      'sel': base64.b64encode(sel).decode()},
              'entrees': melange}
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(sortie, indent=1) + '\n', encoding='utf-8')
    print(f'{total} élève(s) au total → {args.sortie.relative_to(ROOT) if ROOT in args.sortie.resolve().parents else args.sortie}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
