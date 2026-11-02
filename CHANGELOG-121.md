## Issue #121 — 2026-11-02

- `relecture_web` : `test_bruit_fichiers_ignores_projets.py` ne lit plus le
  vrai `bruit_projets.log` (fichier local ignoré par git, absent d'un
  nouveau worktree) pour vérifier les deux entrées initiales de
  relecture_bridge — il fabrique désormais lui-même un fichier temporaire
  via le même mécanisme de redirection que les autres tests du module.
  Au passage, `test_fusion_changelog_distant.py` redirige maintenant lui
  aussi `git_info.CHEMIN_JOURNAL_FUSION_CHANGELOG` vers un fichier
  temporaire : il écrivait jusqu'ici dans le vrai
  `relecture_web/changelog_fusion.log` à chaque exécution de la suite.
