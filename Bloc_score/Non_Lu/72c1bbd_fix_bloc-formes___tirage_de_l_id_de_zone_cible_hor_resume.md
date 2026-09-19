## Nature du changement
Correction dans `bloc-formes.html` (fusion des zones résiduelles) : le tirage aléatoire de l'id de zone cible est extrait du prédicat de `zones.find()`. `randInt(options.length)` est désormais évalué une seule fois dans `targetId`, puis comparé aux ids, au lieu d'être réévalué à chaque élément testé.

## Intention probable
Éliminer un crash intermittent (`target undefined`) au chargement du plateau, causé par un tirage aléatoire réévalué à chaque comparaison qui pouvait ne correspondre à aucune zone existante.

## Points d'attention
- Rien de particulier à signaler.
