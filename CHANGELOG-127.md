# CHANGELOG-127 — à fusionner dans CHANGELOG.md

## Issue #127 — 2026-11-04

- `relecture_web` : le panneau « Dernier push » de la page projet affiche
  désormais, pour un push abouti (`etat == "pousse"`), un bloc repliable
  « Sortie du push (tests du crochet) » fermé par défaut, contenant la fin
  de la sortie déjà conservée par le moteur (issue #122) — donc les lignes
  de comptage des tests que le crochet imprime. Absent si la sortie est
  vide. Aucun changement à l'affichage d'un échec (même bloc, mêmes
  libellés, même mise en page).
- Le panneau d'un push abouti reste affiché malgré `vu=True` (déjà posé
  automatiquement à la réussite, qui continue de suffire à ce qu'un succès
  ne soit jamais signalé dans la barre latérale, la route de sondage ou la
  fenêtre globale, issue #123) jusqu'au push suivant ou jusqu'à la
  fermeture explicite d'un nouveau bouton « Masquer »
  (`POST /projet/<nom>/push/masquer`, `push_arriere_plan.marquer_masque`) —
  exception délibérée au principe « un résultat acquitté disparaît du
  panneau » posé par l'issue #125, documentée dans le code
  (`push_arriere_plan.entree_affichable`) et dans `RELECTURE_WEB_DOC.md`.
  Champ dédié `masque`, séparé de `vu` volontairement : aucun effet sur la
  barre latérale, la fenêtre globale ou le titre de l'onglet, qui
  n'exposent ni ne lisent ce champ.
- Filtrage des secrets (`push_arriere_plan._filtrer_secrets`), appliqué
  par `_tronquer_sortie` avant toute troncature donc avant tout affichage
  ou écriture dans l'état persistant, succès comme échecs : identifiants
  (utilisateur et mot de passe/jeton) dans une URL de dépôt, jetons GitHub
  reconnaissables par leur préfixe (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/
  `github_pat_`), valeur d'une ligne `Authorization:` — remplacés par un
  marqueur neutre sans toucher au reste de la ligne. Limite assumée et
  documentée : ce filet de sécurité ne devine pas un secret de forme
  arbitraire ; la vraie protection reste que le crochet et les tests
  n'impriment eux-mêmes aucun secret.
- Format du fichier d'état inchangé pour la compatibilité : le nouveau
  champ `masque` est optionnel, absent sur un fichier existant d'avant
  cette issue, sans erreur.
- Reprise de l'issue #126 (non fusionnée : sa branche `worktree-issue-126`
  a été réalisée avant #125 et aurait conflit avec elle sur le même code)
  — travail relu puis adapté à `main` tel qu'il contient désormais #125,
  sans fusionner ni modifier la branche #126.
- Tests ajoutés dans `test_push_arriere_plan.py` : bloc affiché pour un
  push abouti avec sortie (et fermé par défaut), absent si sortie vide,
  échec inchangé, non masqué par l'ancien bouton/route « Vu » puis masqué
  par le nouveau bouton « Masquer », réapparition au push suivant, aucun
  effet sur la barre latérale/la route de sondage, plusieurs formes de
  filtrage de secrets (URL avec et sans mot de passe, jeton GitHub
  classique et fine-grained, en-tête Authorization) sans altérer une
  sortie ordinaire, vérifiées aussi bien en unitaire que sur la sortie
  réelle d'un push de bout en bout. Suite complète verte (297 tests).
