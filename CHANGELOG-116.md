## Issue #116 — 2026-10-25

- `confirmation_fichiers_ignores_worktree.html` (suite de #112/#113) :
  décision par fichier et journal des décisions, sans aucun classement
  automatique du bruit.
- Une case **« À garder »** décochée par défaut sur chaque fichier/dossier
  listé, avec un bouton « Tout cocher »/« Tout décocher » par worktree —
  ces cases ne servent qu'à décider et à tracer, la suppression reste
  strictement par worktree entier.
- **Confirmer la suppression malgré tout** : inactif (message explicite)
  si au moins une case « À garder » est cochée — règle revérifiée CÔTÉ
  SERVEUR (`app._refus_confirmation_fichiers_ignores`), pas seulement
  désactivée dans la page. Sinon, ouvre la fenêtre de confirmation forte
  habituelle enrichie d'un **menu obligatoire** (« Vu avec Claude Chat » /
  « Décision personnelle », sans valeur présélectionnée, bouton de
  validation inactif tant qu'aucun choix n'est fait). Une fois validé,
  chaque fichier listé est journalisé « supprimer », puis la suppression a
  lieu comme avant.
- **Annuler** n'est plus un simple lien : il ouvre une petite fenêtre avec
  le même menu obligatoire (nouvelle route POST
  `annuler_fichiers_ignores_route`, `/projet/<nom>/fichiers-ignores/annuler`).
  Une fois validé, rien n'est supprimé pour aucun worktree du lot, retour
  à la page du projet, et chaque fichier est journalisé « garder » (case
  cochée) ou « supprimer (pas encore fait) » (sinon).
- **Précédent, le fil d'Ariane, un lien vers un autre projet, le bouton
  retour du navigateur** : inchangés, toujours de simples liens `<a>` —
  aucune requête, donc aucun enregistrement ; le ou les worktrees restent
  exactement tels qu'ils sont, la page peut être rouverte plus tard.
- Journal (`git_info.journaliser_decision_fichier_ignore`, chemin en
  constante `git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES`) : texte
  UTF-8 en ajout seul, `relecture_web/decisions_fichiers_ignores.log` —
  hors de tout worktree, même principe que `changelog_fusion.log` (#62),
  ajouté au `.gitignore` racine. Pas un journal de résultat : enregistre
  la décision prise au moment de la validation, même si une suppression
  échoue ensuite (page de suppression forcée, non modifiée par cette
  issue). Une écriture impossible n'est jamais bloquante (avertissement
  affiché, action non interrompue).
- `base.html` (`ouvrirConfirmation`) : support optionnel d'un menu
  obligatoire (`options.menu`) dans la fenêtre de confirmation partagée,
  réutilisable par d'autres pages à l'avenir.
- `#109` (chargement à la demande d'un projet distant) et le calcul de
  taille jamais tenté par SSH restent inchangés — la taille affichée
  ("taille non calculée" pour un projet distant) est reportée telle
  quelle dans le journal.
- Tests : nouveau fichier `test_decisions_fichiers_ignores_worktree.py`
  (cases non présélectionnées, liens sans effet, Annuler/Confirmer avec et
  sans menu/case cochée, plusieurs worktrees, journal non inscriptible,
  chemin ignoré par git, projet distant avec faux ssh). Mise à jour de
  `test_fichiers_ignores_suppression_worktree.py` (menu désormais requis
  pour la re-soumission bypass) et de
  `test_bouton_annuler_confirmation_suppression.py` (Annuler de cette page
  précise n'est plus un lien simple ; `echec_suppression_worktree.html`
  inchangée).
- `RELECTURE_WEB_DOC.md` mise à jour (section 9).
