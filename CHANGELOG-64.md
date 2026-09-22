## 2026-09-22 — issue #64 (relecture_web)

- `finaliser_commit_merge` (`git_info.py`) plantait avec un
  `subprocess.TimeoutExpired` non rattrapé après seulement 10s
  (`TIMEOUT_GIT`) : le `git commit --no-edit` qu'elle exécute déclenche
  le hook `post-commit` du projet, qui appelle Claude en ligne de
  commande pour générer le résumé fonctionnel (`resumer_diff.py`) — une
  opération pouvant dépasser 10s sur un fichier volumineux (vécu
  concrètement sur `RELECTURE_WEB_DOC.md`). Push et Merger utilisent
  déjà `TIMEOUT_GIT_LONG` (120s) pour cette même raison de fond (issue
  #39), mais `finaliser_commit_merge` n'avait pas été aligné dessus lors
  de sa création (issue #61).
  - `git_info.py` : `finaliser_commit_merge` passe maintenant
    `timeout=TIMEOUT_GIT_LONG` (120s) à l'appel `git commit --no-edit`,
    en cohérence avec `pousser_branche` et `fusionner_worktree`.
  - `app.py` (`finaliser_merge_route`) : ajout d'un `try/except` autour
    de l'appel à `finaliser_commit_merge`, sur le même modèle que
    `pousser_branches_route`/`merger_branches_route` (issues #39/#61) —
    un dépassement du délai malgré tout, ou toute autre erreur
    inattendue, est désormais rapporté par un message flash explicite
    plutôt que de faire planter la requête avec une page d'erreur brute.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Finaliser le merge** du
    tableau des actions, et section 10) mise à jour en conséquence.
