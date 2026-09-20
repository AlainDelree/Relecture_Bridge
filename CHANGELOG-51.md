## 20 septembre 2026 — issue #51

Fusion automatique de `CHANGELOG-<N>.md` lors d'un merge depuis
`relecture_web`.

- `fusionner_worktree` (`relecture_web/git_info.py`) appelle désormais
  `fusionner_changelog_worktree` juste après un merge réussi, pendant que
  la branche cible est encore extraite dans le dépôt (avant toute bascule
  de retour) : si la branche fusionnée a introduit un `CHANGELOG-<N>.md` à
  la racine du dépôt, lance `scripts/fusionner_changelog.py` (déjà présent
  dans le projet concerné) pour l'intégrer dans `CHANGELOG.md`.
- Aucun `CHANGELOG-<N>.md` détecté : `changelog` vaut `None`, aucun message
  supplémentaire affiché.
- Résultat de cette étape rapporté par un message flash séparé dans
  `merger_branches_route` (`relecture_web/app.py`) — succès, ou message
  d'erreur explicite (script absent, échec du script) sans jamais faire
  échouer silencieusement la fusion elle-même.
- `RELECTURE_WEB_DOC.md` (section 9, ligne « Merger ») mis à jour en
  conséquence.
- Vérifié par test manuel dans des dépôts temporaires hors du dépôt réel
  (merge avec `CHANGELOG-<N>.md` présent et script présent, merge sans
  `CHANGELOG-<N>.md`, merge avec `CHANGELOG-<N>.md` mais script absent).
