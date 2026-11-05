## Issue #132 — 2026-11-05

- `relecture_web/templates/base.html` : bouton « Copier » dans la fenêtre
  de résultat globale (`#modal-resultat-push`), à côté de « Vu »/« Fermer »,
  pour un refus comme pour un succès avec sortie non vide — jamais un
  acquittement. Réutilise le mécanisme de copie existant (📋), avec repli
  `execCommand` inchangé, un libellé de succès configurable par bouton
  (« Copié ✓ » ici, « ✓ » ailleurs, inchangé) et un retour « ✗ » discret en
  cas d'échec réel de copie.
- `relecture_web/templates/projet.html` : même bouton « Copier » sur le
  bloc de sortie du panneau « Dernier push », pour un push abouti comme
  pour un échec — absent si la sortie est vide.
- `relecture_web/push_arriere_plan.py` : `entete_copie`/`contenu_copie`
  (en-tête projet/résultat/branches/heure de fin, puis la sortie déjà
  filtrée/tronquée) pour le panneau ; `entree_pour_copie` pour la nouvelle
  route dédiée (champs restreints, jamais `repertoire` ni `pid`).
- `relecture_web/app.py` : nouvelle route `GET
  /push/<nom_projet>/sortie_pousse` (lecture seule), interrogée par la
  fenêtre de résultat globale à son ouverture pour récupérer la sortie
  d'un succès qu'elle ne reçoit jamais par le sondage habituel
  (`etats_a_signaler` exclut déjà un push abouti vu) — jamais ajoutée au
  sondage global lui-même.
- `relecture_web/static/style.css` : variante pleine taille du bouton
  copier, `word-break: break-word` sur la zone de sortie de la fenêtre de
  résultat (les lignes trop longues passent désormais à la ligne au lieu
  d'être coupées, défilement vertical inchangé).
- Tests ajoutés dans `test_push_arriere_plan.py` (bouton présent/absent
  selon la sortie, contenu copié, copier ne change pas `vu`) et
  `test_affichage_global_push.py` (nouvelle route : champs renvoyés,
  champs vides hors push abouti, aucun champ interne exposé, aucune
  modification d'état, absence du sondage global).
