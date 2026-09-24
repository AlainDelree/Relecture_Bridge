## 2026-09-24 — issue #74 (relecture_web)

Pendant l'issue #73, CCL avait travaillé directement dans le dossier
principal `~/Relecture_Bridge` (repli sur REP_TRAVAIL, worktree dédié déjà
pris) ; l'intégration automatique du CHANGELOG déclenchée par un Merger
avait alors committé tout l'arbre de travail (`git commit -a`), travail
inachevé de CCL compris, sous le message générique « chore: fusionne
CHANGELOG-<N>.md dans CHANGELOG.md (auto) » (commit 0c477c0).

- **Portée du commit d'intégration du CHANGELOG strictement limitée**
  (`fusionner_changelog_worktree`, `git_info.py`) : `git add -- CHANGELOG.md
  CHANGELOG-<N>.md...` puis `git commit -- <mêmes chemins>`, au lieu de
  `git commit -a` — ne committe plus jamais que `CHANGELOG.md` et les
  `CHANGELOG-<N>.md` réellement consommés, quel que soit le reste de
  l'arbre de travail au même moment.
- **Nouveau garde-fou avant Merger** (`get_modifications_non_committees`,
  `git_info.py` ; `merger_branches_route`, `app.py`) : si le dossier de la
  branche cible contient des modifications non committées (fichiers suivis
  modifiés, ou fichiers non suivis non ignorés), le merge est refusé par
  message flash explicite avant même d'être tenté — plutôt que de fusionner
  par-dessus un travail potentiellement en cours.
- **`.gitignore` racine** : remplace l'entrée `Relecture_Bridge/Non_Lu/`
  (spécifique au dossier auto-référentiel de relecture_bridge) par le motif
  générique `*/Non_Lu/`, qui couvre le dossier d'exports en attente de
  lecture de tous les projets (présents et futurs), pour qu'un `git add -A`
  (backup CCL, ou une future fusion mal scopée) ne puisse jamais les
  embarquer dans un commit sans rapport.
- Documentation : `RELECTURE_WEB_DOC.md` section 9 (ligne Merger) mise à
  jour avec le nouveau garde-fou et la portée exacte du commit
  d'intégration du CHANGELOG.
