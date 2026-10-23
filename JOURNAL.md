# Journal d'orchestration

Une entrée par tâche, la plus récente en haut. Voir le protocole dans
`CLAUDE.md`.

<!-- Modèle d'entrée :

## AAAA-MM-JJ — <branche>

- Ressource : <chemin>/index.qmd (référence imitée : <chemin>)
- Vérificateur : CONFORME après <n> passage(s)
- Codex : <n> constats A (dont <n> BLOQUANT), <n> réécritures appliquées
- Réécritures gardées : R1, R3… ; annulées : R2 (raison)…
- Relance Codex : oui / non
- Pull request : #<numéro>
- Points à relire par l'enseignant : …

-->

## 2026-10-23 — infra/ci-latex

- Ressource : aucune (CI : .github/workflows/verifier.yml et publier.yml)
- Cause : les PDF passent par lualatex depuis la PR #14, mais les runners n'avaient pas de TeX ; vérification de la PR #14 et publications #12 et #14 en échec
- Correctif : installation de TeX Live par apt, contrôle kpsewhich des fichiers requis
- Vérificateur, Codex : sans objet (infrastructure)
- Pull request : à renseigner
- Points à relire par l'enseignant : liste des paquets TeX Live (non testée en local, la CI de la PR fait foi)
