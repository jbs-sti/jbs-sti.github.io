# Relecture — consignes

Ce document s'adresse au relecteur d'une ressource, lancé par le chef de
projet (Claude Code) après le commit du premier jet. La relecture est
croisée :

- ressource écrite par Codex (cours, fiche, exercices) : relue par le
  sous-agent `relecteur` de Claude Code ;
- ressource écrite par Claude (tp) : relue par Codex, avec la commande

  ```bash
  codex exec -s workspace-write -o .review/codex.md "Lis docs/relecture.md et applique-le au diff de la branche courante par rapport à main."
  ```

Il ne remplace pas `AGENTS.md`, qui reste la règle générale du dépôt.

## Rôle

Vous êtes relecteur externe. Vous contrôlez les ressources modifiées et vous
**appliquez vous-même** les réécritures qui rendent le texte plus pédagogique
et plus fluide. Le chef de projet vérifie ensuite l'exactitude de chaque
modification et annule celles qu'il refuse.

## Périmètre

- Lisez `git diff main` et `git status` pour trouver les ressources concernées.
- Vous ne modifiez **que** les fichiers `index.qmd` de ces ressources.
  Aucun autre fichier : ni images, ni scripts, ni configuration.
- Ne lancez ni `quarto render`, ni les scripts, ni aucune commande git qui
  écrit (`add`, `commit`, `checkout`, `restore`…). Le rendu et les
  contrôles sont faits après vous.

## Partie A — Contrôle (signalement seul)

Signalez, **sans les corriger**, les erreurs de fond :

- **BLOQUANT** : erreur technique (port, commande, calcul, nom de message,
  champ), contradiction interne, information fausse ou dangereuse,
  non-respect d'une règle de `AGENTS.md` (métadonnées, `draft`, équivalent
  PDF, `fig-alt`, langage des blocs de code).
- **À CORRIGER** : imprécision, plateforme non indiquée, terme ambigu,
  source manquante, niveau inadapté.

Format, un constat par ligne :

```text
A1 [BLOQUANT] chemin/index.qmd:42 — constat — justification ou calcul refait
```

Les fautes d'orthographe et d'accord peuvent être corrigées directement :
listez-les comme réécritures R avec le critère « orthographe ».

## Partie B — Réécritures (appliquées)

### Critères observables

Une réécriture n'est permise que si elle répond à au moins un critère.

**Pédagogie**

- *terme non défini* : un terme technique est employé avant d'être expliqué ;
- *abstraction sans exemple* : une notion générale n'est illustrée par aucun
  cas concret à proximité ;
- *deux idées par phrase* : la phrase porte deux informations indépendantes ;
- *utilité non dite* : le lecteur ne sait pas à quoi sert la notion.

**Fluidité**

- *plus de 25 mots* : la phrase dépasse 25 mots ;
- *passif inutile* : l'agent est connu et le passif alourdit la phrase ;
- *enchaînement absent* : rien ne relie la phrase ou le paragraphe au précédent ;
- *empilement de noms abstraits* : au moins trois noms abstraits à la suite
  (« la vérification de la cohérence de l'attribution… »).

### Niveaux et plafonds

- **R** = une phrase : **10 au maximum** pour tout le diff.
- **P** = un paragraphe : **2 au maximum** pour tout le diff.

Ce sont des plafonds, pas des objectifs. Ne réécrivez rien pour atteindre un
quota : « Aucune réécriture » est une réponse valable.

### Interdits

- Changer le sens technique : valeurs, ports, commandes, noms de messages,
  ordre des étapes, conditions, nuances (« normalement », « peut »).
- Toucher à la syntaxe Quarto : en-tête YAML, `:::`, attributs `{…}`,
  blocs de code, liens, images, `fig-alt`, tableaux (structure).
- Passer au tutoiement : le site **vouvoie** le lecteur.
- Modifier un texte qui n'est pas dans le diff.

## Rapport final (votre dernier message)

Votre dernier message est votre rapport au chef de projet (Codex :
enregistré dans `.review/codex.md`). Il suit exactement ce plan :

```markdown
# Rapport de relecture

## A. Contrôle
A1 [BLOQUANT] chemin:ligne — constat — justification
(ou « Aucun constat. »)

## B. Réécritures appliquées

### R1 — chemin:ligne — critère
Avant :
> texte actuel recopié À L'IDENTIQUE, caractère pour caractère
Après :
> nouveau texte
Exactitude : ce qui pourrait changer le sens technique, ou « sens inchangé ».

(… R2 à R10, P1, P2 …)
(ou « Aucune réécriture. »)

## C. Question au chef de projet
Pour chaque réécriture, confirmez-vous que le texte modifié reste
techniquement exact ? Liste : R1, R2, …
```
