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
- `bts2/reseaux/04-acl/cours-acl` (brouillon) : fusionner la PR du TP OSPF
  avant (lien vers le TP 4) ; relire le PDF de la CI ; confirmer dans Packet
  Tracer les sorties `show access-lists` et `show ip interface`, `ssh -l`
  depuis un PC, et le cas d'une ACL appliquée mais inexistante. Petite PR à
  faire : la phrase « un paquet dont la source est usurpée est détruit »
  (l. 495) est fausse si la source usurpée est dans le VLAN 30 (constat
  Codex) ; reprendre aussi la réécriture R2 de Codex (l. 587).
- `bts2/reseaux/04-acl/tp-acl` (brouillon) : relire le PDF de la CI ;
  confirmer en salle que R1 perd aussi FW pendant la panne (INIT), et le
  comportement de `ipconfig /renew` (T1).
- `bts2/reseaux/03-routage-dynamique/cours-ospf` (brouillon) : relire le PDF
  de la CI ; confirmer dans Packet Tracer les sorties `show` (reconstituées).
- `bts2/reseaux/01-vlan-inter-vlan/fiche-vlan-inter-vlan` (brouillon) :
  décider de la longueur (≈ 4 pages, encadré 3560 à garder ou non).
- `bts2/reseaux/03-routage-dynamique/tp-ospf` (brouillon) : relire le PDF de
  la CI ; confirmer en salle l'apparition de `O*E2` (Null0 +
  `default-information originate`), le format de `%OSPF-5-ADJCHG` et le
  recalcul du coût après `bandwidth 100000`.
- Chapitre 02 en deux blocs (décision de l'enseignant) : subnetting (cours
  actuel recentré, même dossier ; fiche méthode ; exercices 1 et 2 ; TP
  subnetting + DHCP serveur, routeur et relais), puis VLSM (cours à partir du
  beamer de l'enseignant, exemple de classe C d'abord, 10.6.0.0/15 en
  exercice ; fiche ; exercices 1 et 2 ; TP 3 actuel). Les TP sont renumérotés
  (subnetting = TP 3, VLSM = TP 4, OSPF = TP 5, ACL = TP 6).
- Ensuite : NAT/PAT, pare-feu et DMZ (ASA 5506-X).

**Décisions durables**

- Le site vouvoie le lecteur.
- Une ressource n'a pas de bloc `format:` : elle hérite des formats du
  projet (html, vintage-pdf).
- Codex relit en `workspace-write` après commit du premier jet ; le chef de
  projet contrôle ses changements dans `git diff`.
- Les ancres (tests, schéma, scripts de vérification, CI) ne sont jamais
  modifiées par un agent.
- Progression BTS2 réseaux, validée par l'enseignant : 01 VLAN et inter-VLAN
  (fait en classe), 02 VLSM, 03 routage dynamique (OSPF monozone), 04 ACL,
  05 NAT/PAT, 06 pare-feu et DMZ, 07 VPN, 08 redondance, 09 supervision,
  10 IPv6. Le routage statique est fait en classe. Plateforme : Packet Tracer.
- Référentiel BTS CIEL (arrêté du 25 janvier 2023) consulté le 2026-10-24 sur
  le PDF Eduscol (referentiels-professionnels.eduscol.education.fr) : ACL et
  pare-feu en C06 (p. 38) et C09 (p. 40), niveau 3 ; NAT/PAT et VPN en C09.
- Les commandes IOS se vérifient dans la référence de Packet Tracer :
  `C:\Program Files\Cisco Packet Tracer 9.0.1\help\default\commandReference\`
  (2911 : `2900_universal_base_15.1.html`). Les sous-interfaces,
  `encapsulation dot1q <1-1005> [native]` et `passive-interface` sur une
  sous-interface sont documentés dans l'aide générale `CLI_routerIOS15.htm`.
- Les TP BTS2 durent 4 h, suivent le réseau fil rouge du TP 3 et demandent un
  compte rendu (questions et captures) ; aucun corrigé n'est publié.
- Pare-feu des TP : ASA 5506-X dans Packet Tracer.

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

### 2026-10-24 — cours/bts2-tp-acl

- Ressource : bts2/reseaux/04-acl/tp-acl/index.qmd (référence imitée : bts2/reseaux/03-routage-dynamique/tp-ospf), avec 1 SVG
- TP de 4 h sur le fil rouge : SSH, ACL standard + `access-class`, ACL étendue nommée pour les invités, numéros de séquence, panne OSPF provoquée sur FW, recette, bonus filtrage sans état ; Q1–Q26, C1–C18, aucun corrigé
- Vérificateur : À REPRENDRE au 1er passage (ligne corrective de la panne quasi donnée, et publiée dans le cours), CONFORME au 2e ; CONFORME après Codex
- Codex : 4 constats A (dont 2 BLOQUANT), 2 réécritures ; A2–A4 corrigés par le rédacteur ; A1 porte sur le cours ACL (hors diff), reporté dans « À faire »
- Réécritures gardées : R1 ; annulées : R2 (fichier hors du diff)
- Relance Codex : non (corrections ponctuelles)
- Pull request : #<numéro>
- Points à relire par l'enseignant : durée (4 h serrées), panne sur FW G0/1, `ipconfig /renew`, renumérotation à venir (TP 5 → TP 6)

### 2026-10-24 — cours/bts2-tp-ospf

- Ressource : bts2/reseaux/03-routage-dynamique/tp-ospf/index.qmd (référence imitée : bts2/reseaux/02-subnetting-vlsm/tp-application-vlsm), avec 1 SVG
- TP 4 de 4 h sur le fil rouge : liaison R1–FW ajoutée, router-id, interfaces passives, route par défaut diffusée, panne et convergence, coûts, bonus DR/BDR ; compte rendu (Q1–Q24, C1–C16), sans corrigé
- Commandes confirmées dans la référence de Packet Tracer 9.0.1 (2911, aide générale, minuteries, Fast Forward Time) ; `ping -t` écarté (non documenté)
- Vérificateur : CONFORME ; CONFORME après Codex
- Codex : 3 constats A (dont 1 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur
- Réécritures gardées : R1 ; annulées : aucune
- Relance Codex : non (corrections ponctuelles)
- Pull request : #29
- Points à relire par l'enseignant : rendu PDF, `O*E2` via Null0, messages `%OSPF-5-ADJCHG`, coût après `bandwidth 100000`, citation RFC 2328 §9.4

### 2026-10-24 — cours/bts2-fiche-vlan

- Ressource : bts2/reseaux/01-vlan-inter-vlan/fiche-vlan-inter-vlan/index.qmd (référence imitée : bts2/reseaux/02-subnetting-vlsm/cours-subnetting-vlsm), avec 1 SVG et l'index du nouveau chapitre 01
- Commandes 2960 et 3560 confirmées dans la référence de Packet Tracer ; `encapsulation dot1Q` du 2911 absente de toute référence de routeur (non documentée, à tester)
- Vérificateur : CONFORME après 2 passages (tableau des pannes faux au 1er) ; CONFORME après Codex
- Codex : 4 constats A (dont 1 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur
- Réécritures gardées : R1 ; annulées : aucune
- Relance Codex : non (précisions ponctuelles)
- Pull request : #27
- Points à relire par l'enseignant : longueur (≈ 4 pages), encadré 3560, `encapsulation dot1Q … native`, VLAN 99 natif et de gestion, URL NetAcad

### 2026-10-23 — cours/bts2-ospf

- Ressource : bts2/reseaux/03-routage-dynamique/cours-ospf/index.qmd (référence imitée : bts2/reseaux/02-subnetting-vlsm/cours-subnetting-vlsm), avec 3 SVG et l'index du nouveau chapitre 03
- Commandes IOS du cours confirmées dans la référence de Packet Tracer 9.0.1 (2911, IOS 15.1), ainsi que le module HWIC-2T ; sorties `show` reconstituées, non capturées
- Vérificateur : CONFORME au 1er passage (6 points À CORRIGER traités) ; CONFORME après chaque relecture Codex
- Codex (1re relecture) : 4 constats A (dont 1 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur, lien Cisco Design Guide supprimé
- Codex (relance) : 4 constats A (dont 1 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur
- Réécritures gardées : R1 (1re), R1 (relance) ; annulées : aucune
- Relance Codex : oui (correction de fond sur la distance administrative et la métrique)
- Pull request : #26
- Points à relire par l'enseignant : rendu PDF, sorties `show` à confirmer dans Packet Tracer, rôles DR/BDR dépendant de l'ordre de démarrage

### 2026-10-24 — cours/bts2-acl

- Ressource : bts2/reseaux/04-acl/cours-acl/index.qmd (référence imitée : bts2/reseaux/03-routage-dynamique/cours-ospf), avec 3 SVG et l'index du nouveau chapitre 04
- Plan contrôlé par rapport au référentiel (C06, C09, C10) à la demande de l'enseignant ; SSH préféré à Telnet (SSH au niveau 4 en C09)
- Commandes confirmées dans `CLI_routerIOS15.htm` (ACL numérotées et nommées, opérateurs de port, types ICMP) ; noms de ports et `established` non documentés, donc non utilisés
- Vérificateur : CONFORME au 1er passage (6 À CORRIGER traités) ; CONFORME après chaque relecture Codex
- Codex (1re relecture) : 4 constats A (dont 2 BLOQUANT), 1 réécriture ; tous corrigés par le rédacteur
- Codex (relance) : 4 constats A (dont 2 BLOQUANT), 1 réécriture ; A1 (lien vers le TP 4) refusé, la cible arrive avec la PR du TP OSPF ; les autres corrigés
- Réécritures gardées : R1 (1re, déplacée et condensée), R1 (relance) ; annulées : aucune
- Relance Codex : oui (correction de fond sur la ligne DHCP)
- Pull request : #30
- Points à relire par l'enseignant : ordre de fusion (PR du TP OSPF d'abord), sorties `show` reconstituées, lignes DHCP du corrigé de l'exercice 3, rendu PDF

### 2026-10-24 — cours/bts1-retrait-demos

- Fait : suppression, à la demande de l'enseignant, des ressources de démonstration `bts1/reseaux/02-adressage-ip/cours-exemple` et `bts1/reseaux/04-couche-liaison/tp-exemple` ; aucun script, test ni workflow n'en dépendait
- Index du chapitre `02-adressage-ip` conservé (chapitre désormais vide)
- Vérificateur, Codex : sans objet (suppression)
- Pull request : #28
- Points à relire par l'enseignant : garder ou retirer le chapitre 02 vide ; `Architecture.txt` mentionne encore les deux dossiers

### 2026-10-23 — cours/bts1-tcp-udp-publier

- Ressource : bts1/reseaux/05-couche-transport/cours-tcp-udp/index.qmd
- Fait : `draft: false`, par l'enseignant (commit, push et PR lancés par lui)
- Vérificateur, Codex : sans objet (métadonnée de publication)
- Pull request : #24
- Points à relire par l'enseignant : la page en ligne (tableaux larges, exercice 6, légende de la poignée de main)

### 2026-10-23 — infra/gitignore-zone-identifier

- Ressource : aucune (`.gitignore`)
- Fait : `*:Zone.Identifier` ignoré ; ces métadonnées Windows apparaissent sous WSL pour tout fichier téléchargé, et leur nom (avec `:`) casserait les clones sous Windows
- `ancres-memoire.patch` non versionné : identique au commit 9bd9445, déjà dans `main` (PR #19 et #20)
- Vérificateur, Codex : sans objet
- Pull request : #23
- Points à relire par l'enseignant : aucun

### 2026-10-23 — cours/bts1-tcp-udp-relecture

- Ressource : bts1/reseaux/05-couche-transport/cours-tcp-udp/index.qmd et img/poignee-de-main.svg
- Fait : « aléatoires » remplacé par « difficiles à prédire » (encadré Wireshark, légende du SVG), pour s'aligner sur l'encadré des numéros initiaux, à la demande de l'enseignant
- Vérificateur : CONFORME en 1 passage
- Codex : sans objet (changement de formulation sur deux lignes)
- Pull request : #22
- Points à relire par l'enseignant : aucun en dehors du PDF du cours

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
