## Nature du changement
Refonte de la structure des pièces dans `bloc-formes.html` : chaque pièce expose désormais une liste d'`orientations` (cells + parity) au lieu d'un unique jeu de cases. Le Losange gagne 4 orientations, tandis que Triangle, Hexagone et Étoile n'en ont qu'une. Ajout d'un `rotationIndex` par pièce, d'une fonction `currentVariant()`, d'un bouton `rotateBtn` qui fait tourner la pièce sélectionnée, et d'un suivi `lastHover` pour rafraîchir l'aperçu après rotation. `computeTargetCells`, `showPreview` et l'icône SVG lisent maintenant la variante active.

## Intention probable
Permettre la rotation des pièces (surtout le Losange à 4 orientations) et garder l'aperçu à jour après rotation, conformément au message de commit sur la rotation et la vérification de lisibilité.

## Points d'attention
- Le bouton `rotateBtn` et le wrapper `.piece-icon-wrap` supposent un élément `#rotateBtn` présent dans le HTML : vérifier que le markup et le style CSS correspondants existent bien (sinon `rotateBtn` sera `null` et le `addEventListener` plantera au chargement).
- Le `rotationIndex` d'une pièce persiste entre deux sélections : une pièce reposée conserve sa dernière orientation, comportement à confirmer comme voulu.
- L'affichage du nombre d'unités (`units`) est figé sur `orientations[0]` ; cohérent tant que toutes les orientations d'une même pièce ont le même nombre de cases (c'est le cas ici).
