@AGENTS.md

## Protocole d'orchestration

Claude Code est chef de projet. Le sous-agent `redacteur` écrit, le
sous-agent `verificateur` contrôle, Codex relit et réécrit, l'enseignant
fusionne. Les consignes de Codex sont dans `docs/relecture-codex.md`.

### Avant de commencer

- Plan d'abord : si la tâche modifie plus de 3 fichiers, présenter le plan à
  l'enseignant et attendre son accord.
- Créer la branche depuis `main` : `cours/<formation>-<sujet>` pour le
  contenu, `infra/<sujet>` pour le reste. Ne jamais travailler sur `main`.
- Demander à l'enseignant la ressource de référence si elle n'est pas donnée.

### Déroulé d'une ressource

1. **Rédaction** : sous-agent `redacteur`, avec le chemin cible, le type et
   la ressource de référence.
2. **Vérification** : sous-agent `verificateur`. Si le verdict est
   À REPRENDRE, renvoyer les constats au `redacteur`, puis vérifier de
   nouveau. Après deux allers-retours sans CONFORME, s'arrêter et consulter
   l'enseignant.
3. **Commit du premier jet** sur la branche de travail, pour que les
   modifications de Codex apparaissent seules dans `git diff`.
4. **Relecture Codex** : créer `.review/` si besoin, puis lancer cette
   commande seule, sans pipe ni `&&` :

   ```bash
   codex exec -s workspace-write -o .review/codex.md "Lis docs/relecture-codex.md et applique-le au diff de la branche courante par rapport à main."
   ```

5. **Contrôle des modifications de Codex** :
   - `git status` : seuls des `index.qmd` de ressources du diff ont changé ;
     sinon, annuler les autres changements ;
   - pour chaque réécriture R ou P du rapport, comparer « Avant » au texte
     réellement retiré dans `git diff`, et juger l'exactitude technique et
     le respect de la syntaxe Quarto ;
   - annuler une à une les réécritures refusées ;
   - traiter les constats BLOQUANT de la partie A : correction par le
     `redacteur`, jamais par Codex.
6. **Tableau à l'enseignant**, dans la réponse et dans la PR :

   | ID | Niveau | Critère | Avant | Après | Décision du chef de projet |
   |---|---|---|---|---|---|

7. **Nouvelle vérification** par le `verificateur` : il faut CONFORME.
8. **Une seule relance de Codex** au plus, et seulement si l'étape 5 a
   entraîné des corrections de fond.
9. **Publication de la branche** : commit, `git push -u origin <branche>`,
   puis pull request vers `main` (`gh pr create --base main`). La
   description donne ce qui a été fait, ce qui reste incertain, ce que
   l'enseignant doit relire en priorité, le verdict du vérificateur et le
   tableau des réécritures.
10. **Journal** : ajouter une entrée à `JOURNAL.md`, dans le même commit.

### Interdits

- Jamais de commit ni de push sur `main`, jamais de `git push --force`.
- Jamais de fusion de pull request : l'enseignant fusionne.
- Jamais de passage de `draft: true` à `false`.
- Jamais de commande Codex en mode `danger-full-access` ou sans bac à sable.
