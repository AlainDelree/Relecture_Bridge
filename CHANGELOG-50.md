## Issue #50 — 2026-09-20

- Fix : `est_branche_mergee` (relecture_web/git_info.py) plantait
  (`TypeError` dans `subprocess.run`) dès qu'une branche cible configurée
  dans `branches_cibles.conf` était une liste (plusieurs cibles, issue
  #41 — cas de `scrabble`). Gère maintenant ce cas : une branche est
  « fusionnée » si elle est ancêtre d'au moins une des cibles candidates
  (`git merge-base --is-ancestor` par candidate).
- Fix connexe (même page, même cause) : `get_diagnostic_doublons_branche`
  plantait pour la même raison sur `git cherry` — retourne désormais
  `False` (pas de verdict automatique) quand la cible est une liste, même
  parti pris que le cas M déjà en place pour le diagnostic des commits
  orphelins (issue #46), pour ne pas multiplier les `git cherry` coûteux
  sur chaque branche locale de la page.
- Résultat : la page `/projet/<nom>` d'un projet à plusieurs cibles
  configurées (ex. `scrabble`) s'affiche sans erreur, badge « fusionnée »
  correct.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 7.
