## Nature du changement
Dans `bloc-formes.html`, modification du style CSS des cellules occupées (`polygon.cell.occ`) : contour renforcé et effet lumineux `drop-shadow`. Ajout d'un style `.rotate-btn` et d'un bouton « ⟳ Tourner » (désactivé par défaut) sous la réserve, plus mise à jour du texte d'aide en pied de page mentionnant la rotation.

## Intention probable
Préparer l'interface avant l'issue #27 (rotation/lisibilité) : améliorer la visibilité des pièces posées et introduire l'élément d'UI pour tourner une pièce, comme le suggère le message de commit.

## Points d'attention
- Le bouton `rotateBtn` est ajouté à l'état `disabled` sans logique JS associée dans ce diff : c'est un travail en cours (« avant-issue27 »), veiller à ce que la fonctionnalité de rotation soit bien implémentée dans un commit suivant avant toute mise en production.
- Aucun élément de sécurité, secret ou identifiant concerné ; changement purement cosmétique/UI.
