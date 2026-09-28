## Issue #94 — 2026-09-28

- `relecture_web` : routage local/distant des commandes git vers le PC
  fixe Windows (CCW) via SSH — étape 2 du pilotage des projets CCW depuis
  `relecture_web` (diagnostic issue #91), sur le socle de centralisation
  posé par l'issue #93 (`_lancer_git`). Limité aux commandes git
  elles-mêmes, comme demandé par l'issue.
- Nouveau fichier `relecture_web/ccw_host.conf` (même convention que
  `branches_cibles.conf`) : `ccw_host = utilisateur@hôte` (obligatoire) et
  `ccw_key = <chemin>` (optionnel, défaut `~/.ssh/ccl_ccw`). Tant que
  `ccw_host` n'est pas renseigné, aucune commande distante n'est tentée
  (échec propre, message clair) — fichier livré avec les deux entrées
  commentées, à renseigner par Alain.
- `git_info.py` : `est_projet_distant` (heuristique `^[A-Za-z]:\\` sur
  `repertoire`), `charger_config_ccw`, `_lancer_git_distant`,
  `tester_connectivite_ccw`, `commande_affichee`. `_lancer_git` route
  désormais vers l'exécution locale ou distante (SSH) selon
  `est_projet_distant(repertoire)`, en conservant la même interface de
  retour (`subprocess.CompletedProcess` : code de retour, stdout,
  stderr) — aucun appelant existant n'a eu besoin d'être adapté à cette
  distinction.
- SSH : `ConnectTimeout=6` + `BatchMode=yes` + `StrictHostKeyChecking=
  accept-new`, en plus du timeout applicatif existant
  (`TIMEOUT_GIT`/`TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`) — un PC fixe éteint
  échoue vite plutôt que de bloquer le serveur Flask de développement
  (mono-thread).
- Échappement des chemins Windows (`_quoter_argument_distant`) :
  guillemets doubles dès qu'un argument contient un espace, forme
  acceptée aussi bien par `cmd.exe` que par un shell POSIX (Git Bash) —
  le shell distant réel n'ayant pas pu être confirmé par le diagnostic
  #91. Chaque commande git est envoyée seule (jamais enchaînée par `&&`
  au shell distant) : les enchaînements existants
  (`fusionner_worktree` : checkout/merge/checkout retour ;
  worktree remove puis branch -D) le faisaient déjà via des appels
  `_lancer_git` séparés, pas via un `&&` shell — comportement inchangé,
  donc déjà robuste au shell distant réel.
- Commandes prévisualisées à Alain avant confirmation
  (`commande_affichee`) : préfixées par la commande `ssh` réellement
  exécutée pour un projet distant (push, merge, merger-et-supprimer,
  suppression de branche/worktree, revert, sécurisation, finalisation de
  merge), inchangées pour un projet local. Un seul préfixe `ssh` en tête
  des aperçus combinés (« Merger et supprimer », suppression worktree +
  branche), même si plusieurs commandes git sont réellement envoyées
  séparément derrière.
- `collect_etat_projets` : nouveau statut `"injoignable"` (distinct de
  `"introuvable"`, réservé aux projets locaux) pour un projet distant dont
  le PC fixe ne répond pas à un test de connectivité SSH borné
  (`tester_connectivite_ccw`), testé avant toute tentative de commande
  git — sur le modèle du test `os.path.isdir` déjà en place pour les
  projets locaux. `index.html`/`projet.html` affichent alors « 🔌 PC fixe
  éteint ou injoignable — projet indisponible pour le moment » ;
  `_projet_pret` (`app.py`) refuse toute action avec le même message
  flash — même comportement dégradé que l'existant (branches/
  diagnostics/conflits indisponibles), jamais de page cassée.
- Vérifié bout en bout sur ce worktree (aucun accès au PC fixe réel
  nécessaire) : un faux exécutable `ssh` placé en tête de `PATH` (ignore
  les options de connexion, exécute la commande git assemblée via
  `sh -c`) simule un projet distant joignable, avec un `repertoire`
  fictif `C:\CCW\Projet Test` (nom contenant un espace, comme demandé par
  l'issue) pointant en réalité vers un dépôt git local — `_lancer_git`,
  `tester_connectivite_ccw`, `commande_affichee` et `collect_etat_projets`
  testés directement en Python, résultats conformes (log/branche lus à
  travers le routage SSH simulé, aperçu de commande correctement préfixé,
  statut `"ok"`). Cas hôte injoignable testé séparément avec le vrai
  binaire `ssh` pointé vers une IP non routable (`192.0.2.1`,
  TEST-NET-1) : `tester_connectivite_ccw` retourne `False` en ~3s
  (`ConnectTimeout` respecté, aucun blocage) et `collect_etat_projets`
  renvoie bien le statut `"injoignable"`. Cas `ccw_host` non configuré
  testé aussi : échec propre et immédiat, sans tentative de connexion.
- Documentation : nouvelle section 11 de `RELECTURE_WEB_DOC.md` (« Le
  mode SSH vers le PC fixe Windows (CCW, issue #94) »), ancienne section
  11 renumérotée 12 sans changement de contenu.
- Hors périmètre (suivi à prévoir, comme prévu par l'issue) : résolution
  de conflit sur un fichier distant, exécution distante de
  `scripts/fusionner_changelog.py`, équivalent Windows du badge « CCL
  travaille ici » (issue #88) pour un worktree distant.
