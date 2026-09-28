## Issue #93 — 2026-09-28

- Refactor (`relecture_web/git_info.py`) : centralise derrière
  `_lancer_git` la quinzaine de fonctions qui exécutaient encore leur
  propre `subprocess.run(["git", "-C", ...])` en contournant ce point
  commun (`get_rapport_cherry_brut`, `get_patch_id_commit`,
  `trouver_commit_correspondant`, `get_diff_entre_commits`,
  `securiser_commit_orphelin`, `fusionner_worktree`, `supprimer_worktree`,
  `supprimer_branche`, `supprimer_branche_recuperation`, `revert_commit`,
  `pousser_branche`, `verifier_push_apres_timeout` (partie `git
  ls-remote`), `finaliser_commit_merge`) — `retraiter_fichier_conflit`
  passait déjà par `_lancer_git`, rien à y changer.
- `_lancer_git` a été étendu avec deux paramètres optionnels pour couvrir
  les usages qui ne s'y prêtaient pas encore : `timeout` (les appels à
  durée longue — push, merge, commit --no-edit — ou réseau — ls-remote —
  gardent leur délai propre, `TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`, au lieu
  du défaut `TIMEOUT_GIT`) et `entree` (texte transmis sur l'entrée
  standard, pour les pipes entre deux commandes git — `git show`/`git
  log -p` vers `git patch-id`, dans `get_patch_id_commit` et
  `trouver_commit_correspondant`).
- Aucun changement de comportement observable : mêmes commandes, mêmes
  codes de retour, mêmes messages d'erreur, mêmes timeouts — vérifié par
  test manuel sur un dépôt git temporaire (worktree, merge, push vers un
  remote local, conflit + finalisation de merge, branches de récupération,
  et les deux cas de pipe patch-id comparés à la commande brute).
- `fusionner_changelog_worktree` : son `git add`/`git commit` passaient
  déjà par `_lancer_git` avant cette issue ; seul son appel au script
  externe `scripts/fusionner_changelog.py` reste un `subprocess.run`
  distinct (ce n'est pas une commande git) — un commentaire dans le code
  signale désormais explicitement cette deuxième surface d'exécution,
  hors du périmètre de ce refactor.
- Prépare le terrain pour une future issue de routage local/SSH des
  commandes git (diagnostic de l'issue #91) : tout appel git de ce module
  passe maintenant par ce point d'entrée unique.
