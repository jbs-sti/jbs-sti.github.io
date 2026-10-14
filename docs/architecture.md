# Architecture — décisions et raisons

Document de référence pour comprendre *pourquoi* le projet est construit ainsi.
Les règles opérationnelles sont dans `AGENTS.md`.

## Décisions

| Sujet | Décision | Raison principale |
|---|---|---|
| Générateur | Quarto, projet `website` | Une source `.qmd` produit nativement HTML et PDF |
| Moteur PDF | Typst (inclus dans Quarto) | Rapide, sans TeX Live, SVG natifs, bonne typographie |
| Recours PDF | LaTeX, ressource par ressource | Mises en page que Typst gère mal (tableaux complexes) |
| Hébergement | GitHub Pages, organisation `jbs-sti` | Gratuit, HTTPS, adresse https://jbs-sti.github.io/ |
| Publication | GitHub Actions (`.github/workflows/publier.yml`) | Build reproductible, déploiement atomique |
| Navigation | Barres latérales automatiques + pages *listing* | Ajouter une ressource ne modifie aucun fichier partagé |
| Recherche | Recherche intégrée de Quarto | Côté client, sans serveur ; Pagefind si insuffisante en français |
| Code d'exemple | Affiché, jamais exécuté | Pas de Python ni Jupyter en CI, build déterministe |
| Identité visuelle | Extension locale `_extensions/vintage/` + `_brand.yml` | Présentation séparée du contenu, en un seul endroit |

## Options écartées

- **MkDocs + Material** : fin de vie annoncée le 5 novembre 2026.
- **Zensical** : successeur prometteur mais jeune, sans sortie PDF.
- **Docusaurus, Astro** : PDF entièrement à construire, dépendances Node lourdes.
- **Impression du HTML par Chromium** : mauvaise mise en page papier.

## Identité visuelle

- Couleurs : vert profond `#1C322D`, crème `#F8F3EE`, or `#EBB552`,
  rose poudré `#F1CDBE`, gris `#A1A1AA`.
- Polices : Libre Baskerville (titres, texte), Inter semi-gras (étiquettes, badges),
  embarquées dans `_extensions/vintage/fonts/` (licence OFL).
- HTML : riche mais sobre, priorité à la lecture sur smartphone.
- PDF : A4, sobre, entièrement lisible en noir et blanc.
- Contraste : l'or sur crème est réservé aux éléments décoratifs, jamais au texte courant.
- Références visuelles : `design/reference/`.

## Arborescence cible

```
jbs-sti.github.io/
├── AGENTS.md            # règles pour tous les agents
├── CLAUDE.md            # contient : @AGENTS.md
├── _quarto.yml          # navbar, barres latérales, formats, recherche
├── _brand.yml           # couleurs et polices partagées HTML/PDF
├── index.qmd            # accueil
├── _extensions/vintage/ # thème SCSS, gabarit Typst, polices
├── _templates/          # gabarits cours, tp, exercices, fiche
├── _schemas/            # schéma des métadonnées
├── scripts/             # création de ressource, vérifications
├── design/reference/    # maquettes et modèles visuels
├── docs/                # ce document
├── snt/
├── bts1/
├── bts2/
└── .github/workflows/
```

## Limites de GitHub Pages

- Site publié : 1 Go maximum. Pas de vidéos dans le dépôt.
- Bande passante : limite souple de 100 Go par mois.
- Dépôt public : tout le contenu source est visible.

## Feuille de route

1. **Phase 0 — Socle** : site minimal publié. *Terminée.*
2. **Phase 1 — Structure et identité** : arborescence, navigation, thème HTML,
   gabarit PDF, cours étalon ARP validé en HTML et en PDF imprimé en N&B.
3. **Phase 2 — Industrialisation** : gabarits, script de création, vérifications,
   CI de contrôle sur pull request, protection de `main`.
4. **Phase 3 — Migration** des supports existants, formation par formation.
5. **Phase 4 — Confort** : recherche, QR codes automatiques.
6. **Phase 5 — Interactivité** : quiz, Python dans le navigateur, simulateurs.
