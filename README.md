# Supports de cours SNT et BTS CIEL

Le site est construit avec Quarto. Une ressource est écrite dans un seul
`index.qmd` et fournit une page HTML et un PDF A4. Lire [AGENTS.md](AGENTS.md)
avant de contribuer, et [l’architecture](docs/architecture.md) pour les choix techniques.

## Installer les outils des scripts

Python 3.10 ou supérieur et Quarto sont nécessaires. Dans un environnement Python
isolé, installer les dépendances figées :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
```

PyYAML est utilisé pour lire des métadonnées YAML réelles (listes, chaînes,
commentaires) avec un chargeur sûr qui refuse les clés dupliquées. Un parseur
YAML maison serait fragile. La validation du sous-ensemble JSON Schema utilisé
reste en bibliothèque standard : aucune dépendance `jsonschema`.
Ne pas versionner l’environnement `.venv`.

## Créer une ressource

Depuis le dépôt, en utilisant le Python de cet environnement :

```bash
.venv/bin/python scripts/nouveau.py bts1 reseaux 04-couche-liaison arp --type cours
.venv/bin/python scripts/nouveau.py snt 01-internet adresses-ip --type fiche
```

Le script fonctionne aussi depuis un autre répertoire : sa racine est celle de
son propre dépôt. Les types sont `cours`, `tp`, `exercices` et `fiche`.
Pour BTS, les domaines autorisés sont `reseaux`, `programmation`,
`cybersecurite`, `systemes` et `electronique`.
Pour SNT, le thème remplace le chapitre et le niveau domaine est absent du chemin ;
la métadonnée `domaine` vaut `snt` et les catégories contiennent le type et `snt`.

Le chapitre/thème commence par deux chiffres (`04-couche-liaison`). Le sujet est
sans accent, en minuscules, avec des tirets entre les mots. Le script crée
`<formation>/<domaine>/<NN-chapitre>/<type>-<sujet>/index.qmd` pour BTS,
et `<formation>/<NN-theme>/<type>-<sujet>/index.qmd` pour SNT,
ainsi que les dossiers `img/` et `fichiers/`.
Un dossier de ressource existant provoque un échec, sans écrasement.

Si le domaine ou le chapitre n’a pas encore d’`index.qmd`, le script en crée un :
cette page sans contenu liste les ressources de la section et lui donne son titre
dans la barre latérale. Son titre est déduit du nom du dossier, donc sans accents :
il est à relire. Un index déjà présent n’est jamais réécrit.

Le titre, chapitre, catégories, mot-clé, date et type sont préremplis. La
description, les objectifs et la durée restent à préciser ; le titre généré
est à relire. `draft: true` est systématique. Seul l’enseignant publie le
brouillon après relecture. Les quatre gabarits sont dans [_templates/](_templates/).
Les gabarits définissent la langue française et reprennent un réglage local de
contraste des cellules d’en-tête PDF, nécessaire avec le thème actuel.
Le gabarit cours suit le cours ARP de référence ; les trois autres sont des
adaptations pédagogiques à relire avant leur généralisation.

## Vérifier les sources

```bash
.venv/bin/python scripts/verifier_sources.py
.venv/bin/python scripts/verifier_sources.py --racine /chemin/vers/un/depot
.venv/bin/python -m unittest discover -s scripts/tests -v
```

Le schéma commun est [_schemas/ressource.schema.json](_schemas/ressource.schema.json).
Le validateur contrôle les métadonnées obligatoires, leur cohérence avec le
chemin, les images Markdown directes ou par référence et les images HTML locales,
les fichiers des formations dépassant **5 000 000 octets**, les langages des
blocs de code, les blocs exécutables et les iframes YouTube sans `youtube-nocookie`.
Les index de formation sont exclus du contrôle des ressources.
Le programme affiche le chemin et, lorsque possible, la ligne concernée.
Il retourne `0` en cas de succès et `1` en cas d’erreur (`2` pour un usage invalide).

Un bloc `.content-visible when-format="html"` doit être accompagné d’un bloc
`.content-visible unless-format="html"` adjacent au même niveau, avec un contenu
imprimable non vide. Les deux ordres sont acceptés. Les blocs peuvent être imbriqués.
Les commentaires et exemples de code sont ignorés pour l’analyse du contenu.

Ce contrôle statique utilise un sous-ensemble documenté de Markdown/Quarto : les
images construites par un filtre, un shortcode, CSS ou JavaScript ne sont pas
résolues. Les URLs d’images distantes ne sont pas téléchargées. Une association
HTML/PDF est vérifiée structurellement ; sa pertinence pédagogique et l’égalité
du contenu exigent une relecture. Les formes conditionnelles autres que ces
deux blocs doivent être relues manuellement. Aucun script ne juge le contraste,
les licences ou l’exactitude technique. Le plafond de taille est strict ; une
exception autorisée par l’enseignant reste à documenter et à traiter séparément.

Le sous-ensemble JSON Schema pris en charge comprend `type`, `required`,
`properties`, `additionalProperties` booléen, `enum`, `minLength`, `pattern`,
`format: date`, `items`, `minItems`, `uniqueItems` et `minimum`. Les annotations
usuelles et les extensions `x-` sont autorisées ; toute autre contrainte est
refusée pour éviter une validation silencieusement incomplète.

## Construire et proposer une modification

```bash
quarto render
```

Vérifier dans `_site/` les sorties HTML et PDF de la ressource.
Pour relire le HTML d’un brouillon, utiliser :

```bash
quarto preview <chemin>/index.qmd --no-browser
```

Avec `draft: true`, le rendu normal produit une page HTML vide ; la
[prévisualisation Quarto](https://quarto.org/docs/websites/website-drafts.html)
permet de lire le contenu sans passer le brouillon à `false`. Les gabarits,
placés dans un dossier commençant par `_`, ne sont pas des pages du site.
Ne jamais versionner `_site/`, `.quarto/` ni les caches Python.
Une tâche correspond à une branche et une PR : `cours/<formation>-<sujet>` pour
le contenu, `infra/<sujet>` pour les outils. Ne pas pousser sur `main` ni fusionner
les PR. Les contrôles de publication sont décrits ci-dessous.

## Contrôler les sorties et la publication

Après le rendu, lancer :

```bash
.venv/bin/python scripts/verifier_site.py
```

Le script reprend les métadonnées du schéma commun. Pour chaque ressource avec
`draft: false`, il exige `_site/<chemin-de-la-ressource>/index.html` et `index.pdf`.
La page HTML doit avoir du contenu dans son corps ; le PDF doit être lisible en
mode strict, non chiffré, avec au moins une page et des dimensions valides.
Les flux de contenu des pages sont décodés. Les métadonnées invalides font
échouer le contrôle ; les sorties des brouillons ne sont pas exigées.
Le retour est `0` si tout est valide, `1` sinon (`2` pour un usage invalide).
Pour un autre dépôt ou dossier de sortie :

```bash
.venv/bin/python scripts/verifier_site.py --racine /chemin/depot --site /chemin/rendu
```

La dépendance `pypdf` est nécessaire : la bibliothèque standard ne permet pas
une lecture fiable de la structure et des pages PDF. Une recherche de `%PDF`
ou de `/Page` dans les octets serait insuffisante. Le contrôle vérifie la
lisibilité structurelle et les pages ; il ne remplace pas la relecture du contenu,
la vérification visuelle ni une certification de conformité à toutes les normes PDF.

Sur chaque PR, `.github/workflows/verifier.yml` lance les tests, le contrôle des
sources, `quarto render --no-execute`, puis le contrôle des sorties. Le job porte
le nom stable **Vérifier les ressources**, à sélectionner dans la protection de
branche. Les PDF sont joints dans l’artefact `pdf-relecture-pr-<numéro>`, conservé
14 jours. Les PDF déjà produits restent récupérables après un échec de contrôle
ou de rendu ; leur présence en artefact ne signifie pas que le contrôle a réussi.
Ce workflow possède seulement la permission `contents: read` et ne déploie rien.

Le workflow de publication suit les mêmes contrôles. Il envoie l’artefact Pages
uniquement si toutes les étapes réussissent ; le job de déploiement dépend du
succès du job de construction. Un lancement manuel hors `main` ne publie rien.
Les permissions `pages: write` et `id-token: write` sont limitées au déploiement.

Versions fixées : Quarto **1.10.19**, Python **3.12.15**, PyYAML **6.0.3** et
pypdf **6.20.1**. Typst est fourni par cette version de Quarto. Toutes les actions
GitHub sont épinglées par SHA ; les deux workflows utilisent `ubuntu-24.04`.
L’image Ubuntu hébergée reçoit encore les mises à jour de GitHub : ces réglages
fixent les outils principaux, sans garantir une image système immuable.
Toute mise à jour des versions doit être proposée dans une PR et validée par
les tests et le rendu.

## Protéger main sur GitHub (réglages manuels)

Après intégration des workflows dans `main` et une exécution réussie du contrôle,
ouvrir **Settings → Branches → Add classic branch protection rule**, avec le
motif **main**. Régler :

- **Require a pull request before merging**.
- **Require status checks to pass before merging** : choisir **Vérifier les ressources**,
  avec **GitHub Actions** comme application attendue lorsque l’interface le propose.
- **Require branches to be up to date before merging**.
- **Do not allow bypassing the above settings**, pour appliquer la règle aussi
  aux administrateurs ; ne pas ajouter d’exception de contournement.
- Laisser **Allow force pushes** et **Allow deletions** désactivés, puis enregistrer.

Le contrôle doit avoir été exécuté récemment pour apparaître dans la liste.
Une approbation humaine peut être ajoutée si un autre enseignant peut relire les
PR ; elle n’est pas nécessaire au verrou automatique demandé ici.
Voir la [documentation officielle GitHub sur les protections de branche](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule).

Dans **Settings → Pages**, conserver **GitHub Actions** comme source. Ces
réglages ne sont pas modifiés automatiquement par les scripts ou workflows.
