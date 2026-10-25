@AGENTS.md

## Protocole d'orchestration

Claude Code est chef de projet et vérificateur ; l'enseignant fusionne.
Chaque ressource est écrite par un modèle et relue par l'autre :

| Type | Rédaction | Relecture et réécriture | Vérification |
|---|---|---|---|
| cours, fiche, exercices | Codex (`docs/redaction-codex.md`) | sous-agent `relecteur` | sous-agent `verificateur` |
| tp | sous-agent `redacteur` | Codex (`docs/relecture.md`) | sous-agent `verificateur` |

Les deux relecteurs appliquent les mêmes consignes, `docs/relecture.md`.
Les cours suivent la méthode « premier principe, exemple concret, méthode »
décrite dans `docs/redaction-codex.md` : courts, simples, illustrés.

### Mémoire de session

- **Au démarrage** : lire la section « État actuel » de `JOURNAL.md` et
  lancer `git log --oneline -10`, puis résumer à l'enseignant, en trois
  lignes, où en est le projet. Ne rien modifier avant ce résumé.
- **En fin de tâche** : mettre à jour « État actuel » (en cours, à faire,
  décisions durables) en plus de l'entrée d'historique, dans le même commit.

### Avant de commencer

- Plan d'abord : si la tâche modifie plus de 3 fichiers, présenter le plan à
  l'enseignant et attendre son accord.
- Créer la branche depuis `main` : `cours/<formation>-<sujet>` pour le
  contenu, `infra/<sujet>` pour le reste. Ne jamais travailler sur `main`.
- Demander à l'enseignant la ressource de référence si elle n'est pas donnée.

### Déroulé d'une ressource

1. **Consigne** : créer `.review/` si besoin et écrire `.review/consigne.md` :
   chemin cible, formation, type, ressource de référence, sources (fichiers
   de l'enseignant), contenu attendu, plateforme, métadonnées imposées
   (`order`, `duree`, prérequis, liens permis ou interdits), ressources qui
   dépendent de celle-ci (titres, exemples, vocabulaire à garder).
2. **Rédaction** :
   - **cours, fiche, exercices** : lancer Codex, seul, sans pipe ni `&&`,
     avec un délai d'exécution de 10 minutes (le délai par défaut coupe les
     rédactions longues) :

     ```bash
     codex exec -s workspace-write -o .review/codex.md "Lis docs/redaction-codex.md et rédige la ressource décrite dans .review/consigne.md."
     ```

   - **tp** : sous-agent `redacteur`, avec la même consigne.

   Puis contrôler `git status` : seul le dossier de la ressource (et les
   index créés par `scripts/nouveau.py`) a changé ; sinon, annuler le reste.
3. **Vérification** : sous-agent `verificateur`. Si le verdict est
   À REPRENDRE, renvoyer les constats au rédacteur de la ressource. Pour
   Codex, les écrire dans `.review/constats.md` et lancer, seul et avec le
   même délai :

   ```bash
   codex exec -s workspace-write -o .review/codex.md "Lis docs/redaction-codex.md et corrige la ressource selon .review/constats.md."
   ```

   puis vérifier de nouveau. Après deux allers-retours sans CONFORME,
   s'arrêter et consulter l'enseignant.
4. **Commit du premier jet** sur la branche de travail, pour que les
   modifications du relecteur apparaissent seules dans `git diff`.
5. **Relecture croisée**, d'après `docs/relecture.md`, sur le diff de la
   branche par rapport à `main` :
   - ressource écrite par Codex : sous-agent `relecteur` ;
   - ressource écrite par Claude (tp) : Codex, seul et avec le même délai :

     ```bash
     codex exec -s workspace-write -o .review/codex.md "Lis docs/relecture.md et applique-le au diff de la branche courante par rapport à main."
     ```

6. **Contrôle des modifications du relecteur** :
   - `git status` : seuls des `index.qmd` de ressources du diff ont changé ;
     sinon, annuler les autres changements ;
   - pour chaque réécriture R ou P du rapport, comparer « Avant » au texte
     réellement retiré dans `git diff`, et juger l'exactitude technique et
     le respect de la syntaxe Quarto ;
   - annuler une à une les réécritures refusées ;
   - traiter les constats BLOQUANT de la partie A : correction par le
     rédacteur de la ressource, jamais par le relecteur.
7. **Tableau à l'enseignant**, dans la réponse et dans la PR :

   | ID | Niveau | Critère | Avant | Après | Décision du chef de projet |
   |---|---|---|---|---|---|

8. **Nouvelle vérification** par le `verificateur` : il faut CONFORME.
9. **Une seule relance du relecteur** au plus, et seulement si l'étape 6 a
   entraîné des corrections de fond.
10. **Publication de la branche** : commit, `git push -u origin <branche>`,
    puis pull request vers `main` (`gh pr create --base main`). La
    description donne ce qui a été fait, ce qui reste incertain (section
    « Incertitudes » du rapport du rédacteur comprise), ce que l'enseignant
    doit relire en priorité, le verdict du vérificateur et le tableau des
    réécritures.
11. **Journal** : ajouter une entrée à `JOURNAL.md`, dans le même commit.

### Si Codex est indisponible

Si Codex échoue (limite d'usage, panne), attendre qu'il redevienne
disponible pour les cours : leur style est confié à Codex. Pour une
relecture de TP, le sous-agent `relecteur` peut le remplacer. Le signaler
dans la PR et dans le journal.

### Interdits

- Jamais de commit ni de push sur `main`, jamais de `git push --force`.
- Jamais de fusion de pull request : l'enseignant fusionne.
- Jamais de passage de `draft: true` à `false`.
- Jamais de commande Codex en mode `danger-full-access` ou sans bac à sable.
- Jamais de modification des ancres : tests (`scripts/tests/`), schéma
  (`_schemas/`), scripts de vérification et workflows CI. Si un contrôle
  échoue, c'est la ressource qu'on corrige, pas le contrôle. Une évolution
  de ces fichiers se fait par l'enseignant, sur une branche `infra/`.
