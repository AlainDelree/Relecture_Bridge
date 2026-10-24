## Issue #113 — 2026-10-24

- `confirmation_fichiers_ignores_worktree.html` (page de confirmation
  avant suppression d'un worktree contenant des fichiers ignorés par git,
  issue #112) n'affichait qu'un seul bouton visible (« Confirmer la
  suppression malgré tout ») : avec un seul choix visible, l'impression
  était de n'avoir que celui-là. Un lien **Annuler** (retour simple vers
  la page du projet, rien n'est soumis) est désormais affiché juste avant
  ce bouton, avec le focus par défaut (un appui accidentel sur Entrée ne
  déclenche donc jamais la suppression) — style neutre identique au
  bouton Annuler des fenêtres de confirmation forte existantes
  (`.bouton--annuler`), pendant que le bouton de confirmation garde son
  style de danger. Le formulaire de confirmation (champs cachés, requête
  renvoyée) est inchangé.
- `echec_suppression_worktree.html` (page de suppression forcée après un
  premier échec, issue #103) avait le même défaut pour chaque worktree
  concerné par un bouton « Forcer la suppression » : même correction, même
  ordre (Annuler avant le bouton de forçage), pour chaque worktree —
  seul le premier Annuler de la page reçoit le focus par défaut (un seul
  élément `autofocus` par page, comme l'exige le HTML). Les formulaires de
  forçage (champ caché `branche`, `purger_commit_rejet`) sont inchangés.
- Aucune autre page de confirmation de l'outil n'était concernée : les
  autres actions destructrices (Push, Merger, Supprimer, Rejeter...)
  passent déjà par la fenêtre de confirmation forte commune
  (`#modal-confirmation`, `base.html`), qui propose déjà un bouton Annuler
  avec le focus par défaut depuis l'issue #71/#73.
- Nouveaux tests
  (`relecture_web/test_bouton_annuler_confirmation_suppression.py`,
  9 tests) : sur les deux pages, l'élément Annuler apparaît avant le
  bouton destructeur, pointe vers la page du projet, ne déclenche aucune
  suppression, et le formulaire de confirmation/forçage reste inchangé ;
  un seul `autofocus` sur la page même avec plusieurs worktrees en échec
  simultanément.
- `RELECTURE_WEB_DOC.md`, section 9 : complément sur la ligne « Forcer la
  suppression » — la ligne « Avertissement fichiers ignorés avant
  suppression de worktree » décrivait déjà le bouton Annuler attendu,
  conforme à l'implémentation désormais corrigée.
