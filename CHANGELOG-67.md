## 2026-09-23 — issue #67 (relecture_web)

- Ajout d'un badge dédié `⚠️ worktree orphelin — repli signalé`, distinct
  du badge `worktree` habituel, sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : affiché pour tout worktree
  secondaire dont le chemin apparaît dans une ligne « déjà pris » de
  `logs/watcher-<projet>.log` — le journal que Bridge_Agent écrit
  (issue #589 côté Bridge_Agent) quand une tâche `mode_write` n'a pas pu
  obtenir son propre worktree et est retombée sur `REP_TRAVAIL`.
- `relecture_web/git_info.py` : nouvelles fonctions `_lignes_deja_pris_watcher`
  (lecture seule best-effort de `logs/watcher-<projet>.log` dans le
  répertoire du projet `bridge_agent`, absent/illisible -> liste vide) et
  `worktree_orphelin_signale` (correspondance de chemin dans ces lignes).
  Appelées depuis `collect_etat_projets` pour renseigner
  `worktree["orphelin_signale"]` sur chaque worktree secondaire.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 4 (liste des badges).
