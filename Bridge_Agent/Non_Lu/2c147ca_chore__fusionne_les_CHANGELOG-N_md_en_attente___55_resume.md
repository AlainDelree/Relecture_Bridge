## Nature du changement
Fusion de quatre fichiers `CHANGELOG-N.md` temporaires (issues #556, #575, #585, #586) dans le `CHANGELOG.md` principal, puis suppression des fichiers sources. Opération purement documentaire : aucune ligne de code de production ni de test n'est touchée par ce commit, seul le contenu des changelogs est déplacé.

## Intention probable
Consolider dans le changelog central les entrées accumulées en fichiers séparés (un par issue/worktree) une fois les travaux mergés, conformément à la convention §10 de `BRIDGE_AGENT_DOC.md`.

## Points d'attention
- Le bloc fusionné pour #556 conserve son en-tête d'origine `# CHANGELOG-556 — entrées à fusionner dans CHANGELOG.md` (titre de niveau `#`) au milieu du `CHANGELOG.md` : incohérence de structure Markdown à corriger avant de pousser (le texte « à fusionner » n'a plus lieu d'être une fois fusionné).
- Ordre chronologique non respecté dans le fichier final : les entrées apparaissent #585 (22 sept.), #586 (22 sept.), #575 (19 sept.), #556 (15 sept.), puis #584 (22 sept.) — mélange qui casse l'ordre antéchronologique attendu et sépare les deux entrées du 22 septembre.
- Contenu documentaire uniquement : les entrées décrivent du code sensible déjà mergé ailleurs (transit de tokens GH/OAuth chiffrés RSA #556, retrait d'une route POST non protégée `/diag-visibilite` #585), mais aucun secret en clair n'apparaît ici et ce commit ne modifie pas ce code.
