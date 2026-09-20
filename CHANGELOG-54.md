## 2026-09-20 — issue #54 (relecture_web)

- Pour une branche fusionnée sélectionnée dont le worktree est encore
  actif, le bouton « Supprimer » enchaîne désormais `git worktree
  remove` puis `git branch -D` dans le même clic — plus besoin de
  recliquer une seconde fois pour que la branche, alors sans worktree
  détecté, tombe sous le second cas (issue #43). Comportement inchangé
  pour une branche déjà sans worktree (suppression directe de la
  branche).
- Si le retrait du worktree échoue (modifications non commitées), la
  branche n'est pas touchée — même garde-fou qu'avant, juste enchaîné.
  Si le worktree est retiré mais que la suppression de branche échoue
  pour une autre raison, un message flash distinct rapporte cet état
  intermédiaire.
- Message flash rapportant les deux étapes en une seule ligne (même
  principe que la suppression combinée branche + fichiers `Non_Lu/`,
  issues #31/#40). Aperçu de confirmation JavaScript mis à jour pour
  afficher les deux commandes équivalentes.
- `RELECTURE_WEB_DOC.md` mise à jour (tableau des actions, section 9).
