## 2026-09-26 — issue #87 (relecture_web)

Après un Merger réussi sur chesscoach, l'intégration automatique du
CHANGELOG échouait avec « script introuvable » : `fusionner_changelog_worktree`
(`git_info.py`) cherchait `scripts/fusionner_changelog.py` **dans le dépôt du
projet fusionné**, alors que seuls quelques projets en possèdent une copie —
la plupart, chesscoach compris, n'en ont pas, bien que CCL y crée bien des
`CHANGELOG-<N>.md`.

- **Le script utilisé est désormais toujours celui de relecture_bridge**
  (`git_info.py`, constante `CHEMIN_SCRIPT_FUSION_CHANGELOG`), résolu à partir
  de l'emplacement de `git_info.py` lui-même (un niveau sous la racine de ce
  dépôt, comme `scripts/`) — plus aucune dépendance à une copie présente dans
  le dépôt cible. `--repo <dépôt fusionné>` continue de cibler le bon dépôt.
- **`scripts/fusionner_changelog.py` rendu robuste aux `CHANGELOG.md` d'autres
  projets**, qui ne suivent pas forcément la convention « Convention
  d'ajout : ... » de relecture_bridge (issue #252) : en-tête absent ->
  insertion après le premier titre de niveau 1 (`# ...`) trouvé, ou en tête de
  fichier si aucun titre ; `CHANGELOG.md` absent -> créé avec pour seul
  contenu les entrées fusionnées. Aucune perte de contenu existant dans tous
  les cas — seul le point d'insertion change.
- **Portée du commit d'intégration (issue #74) inchangée** : toujours
  `git add -- CHANGELOG.md CHANGELOG-<N>.md...` puis `git commit -- <mêmes
  chemins>`, jamais `git commit -a`.
- Testé sur des dépôts temporaires : avec l'en-tête habituel (comportement
  identique à avant), sans en-tête mais avec un titre, fichier vide sans
  titre, et `CHANGELOG.md` absent — dans les quatre cas, fusion réussie sans
  perte de contenu. Vérifié aussi de bout en bout via
  `fusionner_changelog_worktree` sur un faux dépôt sans copie locale du
  script, confirmant la disparition du message « script introuvable ».
- Documentation : `RELECTURE_WEB_DOC.md` section 9 (ligne **Merger**) mise à
  jour pour préciser que le script utilisé est celui de relecture_bridge, et
  le comportement selon la forme du `CHANGELOG.md` cible.
