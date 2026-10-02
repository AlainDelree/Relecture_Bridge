## Issue #97 — 2026-10-03

- `relecture_web` : les options propres au bouton « Rejeter (sans
  fusionner) » (case « Purger réellement le(s) commit(s) rejeté(s) » et son
  avertissement nominatif, issue #96) passent dans un panneau repliable
  (`<details>`/`<summary>` « Options de rejet », à côté du bouton Rejeter),
  replié par défaut — les boutons habituels du panneau d'actions (Push,
  Merger, Supprimer, Rejeter, Comparer la sélection, etc.) restent affichés
  en permanence, inchangés. Le panneau s'ouvre automatiquement (et refuse
  de se refermer) tant que la case « Purger » est cochée à l'intérieur,
  pour ne jamais la cocher puis la perdre de vue en repliant par erreur ;
  la confirmation forte au clic sur Rejeter continue de refléter l'état
  réel de la case, que le panneau soit ouvert ou replié au moment du clic.
- Retrait entier de la case « Fermer aussi l'issue GitHub correspondante »
  et de son champ « raison » associé (bouton Rejeter, issue #95) : en usage
  normal, l'issue GitHub correspondant à un worktree est déjà fermée par le
  watcher CCL dès la fin de son traitement (label `done`), bien avant qu'un
  rejet n'intervienne — cette case ne servait quasiment jamais et ajoutait
  de la confusion pour ce cas marginal (issue restée ouverte par exception).
  Toute la logique associée côté `rejeter_worktrees_route` (vérification
  d'état puis `gh issue close`) est retirée avec elle. La logique de
  purge/nettoyage `Non_Lu/` (issue #96), sans rapport avec ce retrait, est
  conservée telle quelle.
- `git_info.py` : `get_etat_issue_github`, `fermer_issue_github` et
  `numero_issue_depuis_nom_branche` supprimées — plus aucun appelant après
  ce retrait (`extraire_numero_issue`, dont dépendait la troisième, reste
  utilisée ailleurs et n'est pas touchée).
- `RELECTURE_WEB_DOC.md` section 9 (ligne « Rejeter (sans fusionner) ») :
  retrait de la mention de fermeture d'issue GitHub, description du
  panneau repliable ajoutée.
