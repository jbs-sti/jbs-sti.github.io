# AGENTS.md — Règles pour les agents (Codex, Claude Code)

Ce fichier est la source de vérité unique pour tout agent travaillant sur ce dépôt.
Lis-le en entier avant chaque tâche. Les décisions d'architecture et leurs raisons
sont dans `docs/architecture.md`.

## Le projet

Site de cours statique pour SNT (seconde), BTS CIEL 1 et BTS CIEL 2.
Généré avec **Quarto** (projet `website`), publié sur GitHub Pages à
https://jbs-sti.github.io/ par GitHub Actions.

Exigence centrale : **chaque ressource est écrite une seule fois** (`index.qmd`)
et produit automatiquement **une page HTML et un PDF A4**.

## Commandes

| Action | Commande |
|---|---|
| Prévisualiser le site | `quarto preview` |
| Construire tout le site | `quarto render` |
| Construire une seule ressource | `quarto render <chemin>/index.qmd` |
| Vérifier l'installation | `quarto check` |

Ne versionne jamais `_site/` ni `.quarto/` : ils sont générés.

## Organisation des fichiers

```
<formation>/<domaine>/<NN-chapitre>/<type>-<sujet>/index.qmd
```

- `formation` : `snt`, `bts1`, `bts2`. En SNT, pas de niveau `domaine` : les thèmes
  du programme servent de chapitres.
- `domaine` : `reseaux`, `programmation`, `cybersecurite`, `systemes`, `electronique`.
- `NN-chapitre` : préfixe numérique sur deux chiffres pour l'ordre (`04-couche-liaison`).
- `type` : `cours`, `tp`, `exercices`, `fiche`.
- `sujet` : minuscules, sans accents, mots séparés par des tirets (`dhcp`, `arp-wireshark`).

Chaque dossier de ressource contient :
- `index.qmd` : la source unique ;
- `img/` : images et schémas (SVG de préférence) ;
- `fichiers/` : fichiers téléchargeables (.py, .pkt, .csv…).

## Métadonnées obligatoires d'une ressource

```yaml
---
title: "Le protocole ARP"
description: "Une phrase qui résume la ressource."
type: cours            # cours | tp | exercices | fiche
domaine: reseaux
chapitre: "04 — Couche liaison"
categories: [cours, reseaux]
mots-cles: [ARP, adresse MAC, IPv4, cache ARP]
objectifs:
  - "Expliquer le rôle d'ARP dans un réseau local."
prerequis:
  - "Adressage IPv4"
duree: "2 h"
order: 10
date-modified: 2026-10-14
draft: true
---
```

Une ressource nouvelle est toujours créée avec `draft: true`. Seul l'enseignant
la passe à `false` après relecture.

## Règles de rédaction

- Français correct, registre adapté au niveau (SNT : élèves de 15 ans ; BTS : post-bac).
- Partir des gabarits de `_templates/` et respecter l'ordre de leurs sections.
- Exactitude technique avant tout. Pour toute configuration réseau, indiquer la
  plateforme visée (Packet Tracer, IOS, Debian…). Ne jamais inventer une commande,
  une option ou un numéro de port : en cas de doute, l'écrire dans la description
  de la pull request.
- Blocs de code toujours annotés avec leur langage (`python`, `bash`, `sql`, `text`
  pour Cisco IOS tant qu'aucune coloration dédiée n'existe).
- Le code d'exemple n'est jamais exécuté au rendu.

## Règle HTML / PDF

Le contenu doit être identique dans les deux formats. Tout bloc réservé au web
(vidéo, quiz, simulateur, animation) doit être accompagné de son équivalent PDF :

```markdown
::: {.content-visible when-format="html"}
<!-- élément interactif -->
:::

::: {.content-visible unless-format="html"}
<!-- équivalent imprimable : QR code + lien, version statique, corrigé… -->
:::
```

## Schémas

- Format SVG, lisible **en noir et blanc** : contraste par la luminosité, traits
  pleins ou pointillés, motifs, étiquettes textuelles. Jamais d'information portée
  par la seule couleur.
- Mermaid autorisé pour les diagrammes de séquence et les organigrammes simples.
- Texte alternatif obligatoire sur chaque image (`fig-alt`).

## Vidéos et vie privée

- Aucune vidéo dans le dépôt : PeerTube, Vimeo ou YouTube en mode `youtube-nocookie`.
- Aucun traqueur, aucun script de mesure d'audience.
- Aucun fichier de plus de 5 Mo sans accord de l'enseignant.

## Git et collaboration entre agents

- Une tâche = une branche = une pull request. Jamais de commit direct sur `main`.
- Noms de branches : `cours/<formation>-<sujet>` pour le contenu,
  `infra/<sujet>` pour la configuration, le thème, les scripts ou la CI.
- **Une tâche de contenu ne modifie que le dossier de sa ressource.** Elle ne touche
  jamais : `_quarto.yml`, `_brand.yml`, `_extensions/`, `_templates/`, `_schemas/`,
  `scripts/`, `.github/`, `AGENTS.md`, `docs/`.
- Ces fichiers partagés ne changent que dans une branche `infra/…`.
- La navigation se met à jour automatiquement : n'édite aucun menu ni aucun index
  pour ajouter une ressource.
- Avant d'ouvrir la pull request : `quarto render` sans erreur, et vérification
  que la ressource existe en HTML et en PDF dans `_site/`.
- Description de la PR : ce qui a été fait, ce qui reste incertain, ce que
  l'enseignant doit relire en priorité.

## Ce que tu ne fais jamais

- Fusionner une pull request ou pousser sur `main`.
- Ajouter une dépendance (paquet npm, pip, extension Quarto) sans l'avoir proposée
  et justifiée dans la PR.
- Supprimer ou renommer une ressource existante sans demande explicite.
- Copier du contenu protégé (manuels, sites tiers) ou des images sans licence libre.
