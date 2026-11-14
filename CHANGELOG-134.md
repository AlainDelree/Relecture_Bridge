## Issue #134 — 2026-11-14

- `relecture_web/git_info.py` : verrou de push par branche — nouveau
  fichier d'état local `autorisations_push.log` (ignoré par git, même
  principe que `bruit_projets.log`), qui ne contient que les branches
  **autorisées** par projet (toute branche absente, y compris la branche
  principale, est verrouillée). Nouvelles fonctions `lire_autorisations_
  push`, `branche_push_autorisee`, `autoriser_push_branche`,
  `verrouiller_push_branche` (reverrouillage explicite ou nettoyage à la
  disparition d'une branche) et `nettoyer_autorisations_push_disparues`
  (nettoyage à chaque affichage de la page projet) — dégradation
  systématique vers la prudence (fichier absent/illisible, ligne mal
  formée ignorée seule) et écriture impossible toujours signalée par un
  retour `False`, sans jamais faire croire à un changement d'état.
- `relecture_web/app.py` : nouvelle route `POST /projet/<nom_projet>/
  branche/<nom_branche>/verrou-push` (`basculer_verrou_push_route`), sans
  confirmation. `pousser_branches_route` refuse désormais toute requête
  dont la sélection contient une branche verrouillée — AVANT la
  séparation entre push synchrone et push en arrière-plan, pour couvrir
  les deux chemins d'un seul garde-fou, tout ou rien. `projet_route`
  nettoie les autorisations de branches disparues et expose `push_
  autorise` par branche au template. Nettoyage de l'autorisation ajouté
  après chaque suppression réelle de branche (« Supprimer la/les
  branche(s) fusionnée(s) » et sa variante forcée, « Merger et
  supprimer », « Rejeter » et sa variante forcée, suppression des
  branches de récupération).
- `relecture_web/templates/projet.html` : cadenas par branche (🔒
  verrouillée / 🔓 push autorisé), distinct de la case à cocher, à droite
  de chaque ligne ; bouton Push grisé côté navigateur dès qu'une branche
  verrouillée fait partie de la sélection courante, avec un message
  nommant les branches concernées, recalculé sans rechargement de page.
- `relecture_web/static/style.css` : styles du cadenas et du message
  d'indisponibilité du bouton Push.
- `.gitignore` : nouvelle entrée `relecture_web/autorisations_push.log`.
- Tests ajoutés dans `relecture_web/test_verrou_push_branches.py`
  (lecture/écriture du fichier, refus serveur tout-ou-rien y compris pour
  un projet équipé d'un crochet pre-push, bascule du cadenas, nettoyage à
  la suppression et à l'affichage de la page projet) ; `test_push_
  arriere_plan.py` et `test_nettoyage_auto_apres_push.py` adaptés pour
  déverrouiller explicitement les branches qu'ils poussent (le verrou par
  défaut concerne tous les projets, y compris ceux déjà couverts par ces
  tests antérieurs à cette issue).
- `RELECTURE_WEB_DOC.md` : mise à jour de la ligne « Push » et nouvelle
  ligne « Verrou de push par branche » (§9) décrivant le cadenas, son
  fichier, ses dégradations et la limite documentée (branche recréée en
  terminal sous le même nom avant le prochain affichage de la page).

---
