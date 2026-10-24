## Issue #108 — 2026-10-24

- `relecture_web` : préparation aux lignes `<nom>_ccw` du tableau §2 de
  `BRIDGE_AGENT_DOC.md` (suite de l'issue #94), qui référencent le clone
  Windows d'un projet (`C:\CCW\<nom>`) à des fins de relecture uniquement
  (ni watcher ni issue GitHub pour elles).
- `git_info.py` : la reconnaissance du worktree principal d'un projet
  distant (`collect_etat_projets`) comparait deux chemins via
  `os.path.realpath`, qui traite un chemin Windows comme un bloc opaque
  sur ce process Linux — un chemin à barres obliques inverses (celui du
  tableau) et son équivalent à barres obliques normales renvoyé par `git`
  (casse potentiellement différente) étaient donc jugés différents, et le
  dossier principal du clone Windows se serait affiché comme un worktree
  ordinaire, avec des actions de fusion/suppression proposées à tort.
  Nouvelle comparaison dédiée (`chemins_windows_egaux`,
  `worktree_est_principal`) qui ignore barres obliques, casse et barre
  finale pour un projet distant, sans rien changer à la comparaison
  `os.path.realpath` existante pour un projet local. `dossier_relecture`
  (nom du dossier `Relecture_Bridge/<dossier>/Non_Lu`) corrigé de même
  (`nom_dossier_chemin_windows`), bien que sans effet pratique aujourd'hui
  (aucun hook post-commit n'existe sur un clone Windows).
- `fusionner_changelog_worktree` lisait/écrivait directement le filesystem
  local (`os.listdir`, script `fusionner_changelog.py` lancé localement) :
  sur un chemin Windows, elle échouait silencieusement à trouver un
  dossier local inexistant et concluait à tort qu'aucun `CHANGELOG-<N>.md`
  n'attendait de fusion. Refuse maintenant explicitement pour un projet
  distant (`est_projet_distant`), avec un message clair plutôt qu'un faux
  négatif silencieux.
- La résolution de conflit sur un projet distant reste hors périmètre
  (lecture/écriture de fichier, pas des commandes git routées), mais
  `conflit_fichier_route`, `traiter_bloc_conflit_route` et
  `traiter_tous_blocs_conflit_route` refusent maintenant explicitement
  (« Résolution de conflit non disponible pour un projet distant (PC fixe
  CCW). ») avant toute tentative d'accès — avant ce correctif, elles
  laissaient `lire_conflits_fichier`/`resoudre_bloc_conflit` échouer sur un
  chemin local inventé (join d'un chemin Windows), avec un message
  d'erreur système confus mais sans jamais lire/écrire un fichier hors de
  propos (l'échec `OSError` était déjà sans risque, juste peu clair).
- `installer.sh` : une ligne à chemin Windows affiche maintenant
  « ℹ Clone Windows distant (PC fixe CCW) — pas de hook installé par ce
  script : ... », distinct du message « ⚠ Ignoré (pas un dépôt git) : ... »
  réservé à un vrai dossier local sans `.git` — comportement inchangé pour
  les chemins Linux.
- `RELECTURE_WEB_DOC.md` (§11) mis à jour : lignes `<nom>_ccw`, comparaison
  de chemins Windows, refus de la résolution de conflit et de la fusion du
  changelog à distance, comportement d'`installer.sh`.
- Tests ajoutés : `relecture_web/test_chemins_windows_ccw.py` (unittest
  autonome, stdlib uniquement, aucun accès réseau réel) — comparaison de
  chemins (barres obliques, casse, barre finale, chemin réellement
  différent y compris même préfixe), comportement local inchangé, refus de
  `fusionner_changelog_worktree` pour un projet distant, et comportement
  d'`installer.sh` vérifié avec un tableau factice en scratch (`curl`
  simulé, dépôt git jetable, jamais de vrai dépôt touché).
