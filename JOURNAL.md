# Journal d'orchestration

Une entrée par tâche, la plus récente en haut. Voir le protocole dans
`CLAUDE.md`.

## État actuel

À tenir à jour à la fin de chaque tâche. Relu au début de chaque session.

**En cours**

- (rien)

**À faire**

- `bts1/reseaux/06-services-reseau/cours-dhcp` et
  `bts1/reseaux/04-couche-liaison/cours-arp` (brouillons) : supprimer le bloc
  `format:` avant publication, sinon le HTML ne sera pas produit (voir PR #18).
- `snt/02-internet/fiche-adressage-ip` : encore en `draft: true`.
- Entrée `infra/ci-latex` : numéro de pull request à renseigner.
- Décider d'un garde-fou côté PR sur les ancres (CODEOWNERS ou contrôle CI
  des chemins), branche `infra/` par l'enseignant.
- `bts1/reseaux/05-couche-transport/cours-tcp-udp` (brouillon) : relire le PDF
  produit par la CI (tableaux larges, exercice 6) ; trancher « aléatoires »
  contre « difficiles à prédire » (encadré Wireshark, légende du SVG).

**Décisions durables**

- Le site vouvoie le lecteur.
- Une ressource n'a pas de bloc `format:` : elle hérite des formats du
  projet (html, vintage-pdf).
- Codex relit en `workspace-write` après commit du premier jet ; le chef de
  projet contrôle ses changements dans `git diff`.
- Les ancres (tests, schéma, scripts de vérification, CI) ne sont jamais
  modifiées par un agent.

## Historique

<!-- Modèle d'entrée :

### AAAA-MM-JJ — <branche>

- Ressource : <chemin>/index.qmd (référence imitée : <chemin>)
- Vérificateur : CONFORME après <n> passage(s)
- Codex : <n> constats A (dont <n> BLOQUANT), <n> réécritures appliquées
- Réécritures gardées : R1, R3… ; annulées : R2 (raison)…
- Relance Codex : oui / non
- Pull request : #21
- Points à relire par l'enseignant : …

-->

### 2026-10-23 — cours/bts1-tcp-udp

- Ressource : bts1/reseaux/05-couche-transport/cours-tcp-udp/index.qmd (référence imitée : bts2/reseaux/02-subnetting-vlsm/cours-subnetting-vlsm), avec 4 SVG et l'index du nouveau chapitre 05
- Vérificateur : CONFORME après 2 passages (6 constats de rédaction au 1er) ; CONFORME après chaque relecture Codex
- Codex (1re relecture) : 6 constats A (dont 4 BLOQUANT), aucune réécriture ; tous corrigés par le rédacteur
- Codex (relance) : 3 constats A (dont 1 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur
- Réécritures gardées : R1 (relance) ; annulées : aucune
- Relance Codex : oui (corrections de fond : règle de l'ack, fiabilité, numéros initiaux)
- Pull request : #<numéro>
- Points à relire par l'enseignant : rendu PDF (Quarto absent en local), encadré des numéros initiaux (simplification de la RFC 9293), sortie `ss -tuln` reconstituée, domaine fictif `intranet.lycee.lan`, « aléatoires » restant à deux endroits

### 2026-10-23 — infra/ancres-memoire

- Ressource : aucune (orchestration)
- Fait : règles `deny` sur les ancres dans `.claude/settings.json` ; section
  « Mémoire de session » et interdit sur les ancres dans `CLAUDE.md` ; délai
  de 10 min pour Codex ; section « État actuel » dans ce journal ;
  `deny` étendu à `scripts/commun.py` (importé par les deux vérificateurs)
  et à `.claude/settings.json` (un agent ne lève pas ses propres interdits)
- Vérificateur, Codex : sans objet
- Points à relire par l'enseignant : le `deny` ne couvre que les outils
  d'édition, pas le shell ni Codex ; garde-fou côté PR (CODEOWNERS ou
  contrôle CI des chemins) laissé à votre décision
- Pull request : #20

### 2026-10-23 — cours/bts2-subnetting-format

- Ressource : bts2/reseaux/02-subnetting-vlsm/cours-subnetting-vlsm/index.qmd
- Cause : bloc `format: vintage-typst` recopié de cours-dhcp ; une page qui déclare `format:` ne produit que les formats listés, d'où l'absence du HTML et l'échec de la publication après la PR #17
- Correctif : suppression du bloc ; le cours hérite des formats du projet (html, vintage-pdf), comme le TP 3
- Vérificateur, Codex : sans objet (métadonnées de format seulement)
- Pull request : #18
- Points à relire par l'enseignant : cours-dhcp et cours-arp (brouillons) portent le même bloc et auront le même problème à leur publication

### 2026-10-23 — cours/bts2-subnetting

- Ressource : bts2/reseaux/02-subnetting-vlsm/cours-subnetting-vlsm/index.qmd (référence imitée : bts1/reseaux/06-services-reseau/cours-dhcp)
- Supprimé à la demande de l'enseignant : cours-pourquoi-30 ; prérequis du TP 3 renommé
- Sources : sujets E4 BTS SN IR 2023 et 2024, BTS CIEL IR 2026 (miroirs, Eduscol inaccessible) ; référentiel non consulté
- Vérificateur : CONFORME après 2 passages (octet significatif mal défini au 1er) ; CONFORME après Codex
- Codex : 5 constats A (dont 1 BLOQUANT), 3 réécritures appliquées
- Réécritures gardées : R1, R2, R3 ; constats A1, A2, A3 corrigés, A5 en partie ; A4 (/31) refusé (hors périmètre)
- Relance Codex : non (corrections de forme)
- Pull request : #16
- Points à relire par l'enseignant : rendu PDF (Quarto absent en local), mentions des sujets E4, absence du sujet 2025 et du référentiel

### 2026-10-23 — infra/ci-latex

- Ressource : aucune (CI : .github/workflows/verifier.yml et publier.yml)
- Cause : les PDF passent par lualatex depuis la PR #14, mais les runners n'avaient pas de TeX ; vérification de la PR #14 et publications #12 et #14 en échec
- Correctif : installation de TeX Live par apt, contrôle kpsewhich des fichiers requis
- Vérificateur, Codex : sans objet (infrastructure)
- Pull request : à renseigner
- Points à relire par l'enseignant : liste des paquets TeX Live (non testée en local, la CI de la PR fait foi)
