## Issue #112 — 2026-10-24

- `relecture_web/git_info.py` : nouvelle fonction
  `lister_fichiers_ignores_worktree(chemin_worktree)` — détecte, via
  `git status --porcelain=v1 --ignored` exécuté dans le worktree lui-même
  (donc routé par SSH pour un projet distant comme toute autre commande de
  ce module, issue #94/#109), les fichiers/dossiers ignorés par
  `.gitignore` présents dans un worktree : `git worktree remove`, même sans
  `--force`, les supprime SANS AUCUN AVERTISSEMENT, puisque `git status`
  (sans `--ignored`) et donc le diagnostic d'échec existant
  (`diagnostiquer_echec_suppression_worktree`, issue #103) ne les voient
  jamais. Cas réel ayant motivé cette issue : l'installeur et l'archive
  produits par un build Windows de Rummikub (`installeur\output\`,
  ignorés) auraient été perdus avec le worktree sans que la personne ne
  les ait recopiés à la main avant.
- Bruit sans valeur exclu de cet avertissement (un seul endroit à éditer :
  `DOSSIERS_IGNORES_SANS_VALEUR`/`SUFFIXES_IGNORES_SANS_VALEUR`/
  `NOMS_FICHIERS_IGNORES_SANS_VALEUR`) : `__pycache__`, `.pytest_cache`,
  `.mypy_cache`, `.ruff_cache`, `*.pyc`, `.DS_Store`, `Thumbs.db`,
  `desktop.ini`. Les dossiers d'environnement/dépendances (`venv`,
  `node_modules`...) sont volontairement absents de cette liste : ils
  peuvent représenter un travail d'installation long à refaire, voire un
  outil installé à la main dans le clone, donc restent toujours affichés.
- Tailles : pour un projet local, calculées en octets (`os.walk` plafonné
  en nombre de fichiers ET en temps, partagés entre toutes les entrées
  d'un même appel pour ne jamais bloquer la page), affichées en
  octets/Ko/Mo/Go (`formater_taille_octets`) ; au-delà du plafond ou en
  cas d'échec filesystem, l'entrée retombe sur « taille non calculée »,
  jamais une erreur. Pour un projet distant (PC fixe CCW), aucun calcul de
  taille n'est tenté par SSH (issue #109) — toujours « taille non
  calculée ».
- `relecture_web/app.py` : `supprimer_worktrees_route`,
  `merger_et_supprimer_route` et `rejeter_worktrees_route` appellent
  désormais cette détection AVANT toute tentative de suppression (et avant
  toute fusion pour « Merger et supprimer ») sur l'ensemble des worktrees
  sélectionnés. Dès qu'au moins un worktree concerné contient un fichier
  ignoré qui n'est pas du bruit, rien n'est supprimé ni fusionné pour
  AUCUN worktree du lot : une nouvelle page de confirmation
  (`confirmation_fichiers_ignores_worktree.html`) liste, par worktree
  concerné, ces fichiers/dossiers avec leur taille, et propose Annuler
  (rien n'est soumis) ou Confirmer la suppression malgré tout (ré-envoi de
  la requête d'origine avec un champ caché
  `ignorer_avertissement_fichiers_ignores=on`, après la fenêtre de
  confirmation forte habituelle). Si aucun worktree sélectionné n'est
  concerné, le comportement reste exactement le même qu'avant cette
  issue.
- `echec_suppression_worktree.html` (page de suppression forcée, issue
  #103) affiche en plus, dans une section distincte quand il y en a, ces
  mêmes fichiers ignorés (`_diagnostiquer_echec_pour_forcage` les ajoute
  désormais à l'entrée affichée) — pour que la confirmation forte porte
  sur l'ensemble de ce qui sera réellement perdu, pas seulement les
  fichiers modifiés/non suivis qui ont fait échouer la tentative normale.
- Rien n'est copié ni sauvegardé automatiquement : l'outil prévient, il ne
  décide pas à la place de la personne. Comportement de git et détection
  des worktrees inchangés par ailleurs.
- Nouveaux tests (`relecture_web/test_fichiers_ignores_suppression_worktree.py`,
  21 tests) : détection directe (bruit seul/dossier de build seul/mélange/
  rien, taille, échec gracieux), routage local/distant (faux `ssh`
  comptant ses appels, zéro calcul de taille et zéro appel hors action sur
  le projet distant concerné), et intégration complète des trois routes
  sur de vrais dépôts/worktrees jetables (confirmation avant toute
  suppression/fusion, annulation ne supprimant rien, confirmation
  supprimant/fusionnant bien, plusieurs worktrees sélectionnés dont un
  seul concerné met le lot entier en pause).
- `RELECTURE_WEB_DOC.md`, section 9 : nouvelle ligne « Avertissement
  fichiers ignorés avant suppression de worktree », et complément sur la
  ligne « Forcer la suppression » existante.
