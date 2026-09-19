## Nature du changement
Refonte de l'algorithme de génération des zones de score dans `bloc-formes.html`. On passe d'un modèle où un triangle pouvait appartenir à 0, 1 ou 2 zones (`cellZones` en tableau de listes) à un pavage complet où chaque triangle appartient à exactement une zone (`cellZone` en tableau d'index). Introduction d'un tirage pondéré de tailles cibles (`pickTargetSize`), d'une boucle de remplissage jusqu'à épuisement, d'une fusion des fragments trop petits, et d'une renumérotation finale. Suppression du code de dégradés SVG (`ensureGradient`, `defs`) devenu inutile, et simplification de `baseFillFor` et `render`.

## Intention probable
Corriger l'issue 28 (« zones sans chevauchement ») : garantir un plateau entièrement pavé sans triangles orphelins ni zones qui se recouvrent, en supprimant du même coup la logique de dégradé de couleurs liée au chevauchement.

## Points d'attention
- La boucle `while (remainingCells > 0)` s'appuie sur un `break` de sécurité si `growZone` renvoie `null` ; vérifier qu'aucun cas de boucle infinie n'est possible (par ex. `remainingCells` qui ne décroît pas alors qu'il reste des cellules libres inatteignables).
- La fusion des fragments suppose qu'une zone trop petite a toujours au moins une zone voisine ; le commentaire admet un cas « ne devrait pas arriver » — un fragment isolé resterait sous `MIN_ZONE_SIZE` sans être fusionné.
- `baseFillFor` fait désormais un accès direct `zones[cellZone[id]]` : si un triangle restait à `-1` (non couvert), cela produirait un `undefined.color` et une erreur runtime ; s'assurer que le pavage couvre bien 100 % des triangles.
- Changement purement front-end/HTML, sans secret ni logique d'authentification ; pas de dépendance d'ordre avec d'autres commits identifiée.
