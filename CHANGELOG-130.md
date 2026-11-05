## Issue #130 — 2026-11-05

- `relecture_web/test_nettoyage_auto_apres_push.py` : `_attendre_fin_push`
  attend désormais la fin RÉELLE du fil d'exécution du push en arrière-plan
  (retrouvé via `threading.enumerate()` grâce à un nom de thread stable,
  `push_arriere_plan.py`) au lieu de la seule apparition d'un état final
  dans le fichier d'état — supprime la course intermittente avec le
  nettoyage automatique (issue #128) qui s'exécute juste après, dans ce
  même thread.
