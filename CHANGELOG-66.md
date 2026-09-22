## 2026-09-22 — issue #66 (relecture_web)

- Après un timeout de 120s sur Push, Merger ou Finaliser le merge, le
  message flash renvoyait systématiquement Alain vers une vérification
  manuelle en ligne de commande (« a dépassé le délai, mais a pu se
  terminer entre-temps — vérifiez manuellement si besoin »), y compris
  quand l'opération avait en réalité bel et bien abouti — constaté sur
  `bridge_agent` (worktree-issue-588) : message de timeout affiché,
  mais fusion réellement terminée (commit de fusion présent, copie de
  travail propre), vérifié à la main via `git status`/`git log`/`git
  worktree list`.
  - `git_info.py` : trois nouvelles fonctions de vérification post-timeout,
    chacune appelée uniquement depuis le bloc `except
    subprocess.TimeoutExpired:` de l'action correspondante :
    - `verifier_push_apres_timeout(repertoire, branche)` — compare le
      commit local de `branche` au commit réellement exposé par le
      remote via `git ls-remote` (pas le suivi local
      `refs/remotes/...`, qui ne serait mis à jour que par un `fetch` et
      pourrait rester périmé). Retourne `ok` = True (push confirmé),
      False (push non abouti), ou None si la vérification elle-même n'a
      pas pu aboutir (réseau).
    - `verifier_merge_apres_timeout(repertoire, branche_cible,
      branche_source)` — distingue trois états réels via `MERGE_HEAD`
      et `git merge-base --is-ancestor` : fusion aboutie, fusion arrêtée
      sur des conflits (pas un échec, la page de résolution de conflits
      prend le relais normalement), ou fusion non aboutie.
    - `verifier_finalisation_merge_apres_timeout(repertoire)` — dans ce
      flux précis, seul le commit visé par `finaliser_commit_merge` peut
      faire disparaître `MERGE_HEAD` ; sa disparition signale donc de
      façon fiable que le commit a bien été créé avant que le timeout
      Python ne tue le process (probablement resté bloqué dans le hook
      `post-commit`).
  - `app.py` : les trois blocs `except subprocess.TimeoutExpired:`
    (`pousser_branches_route`, `merger_branches_route`,
    `finaliser_merge_route`) appellent désormais la vérification
    correspondante et affichent un message flash final reflétant l'état
    réel constaté (succès confirmé, échec confirmé, conflits en attente,
    ou état indéterminé avec la raison), au lieu du message générique
    précédent.
  - `RELECTURE_WEB_DOC.md` (section 9, lignes **Push**/**Merger**/
    **Finaliser le merge** du tableau des actions, et section 10) mise à
    jour en conséquence.
  - Testé manuellement sur des dépôts git temporaires (push déjà abouti,
    push jamais poussé, merge déjà fusionné, merge en conflit non
    résolu, merge non finalisé) pour valider les trois états retournés
    par chaque fonction de vérification.
