# CHANGELOG — relecture_bridge

Historique complet des évolutions du projet, une section par issue, la
plus récente en premier.

Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
## 2026-09-21 — issue #60 (relecture_web)

## Issue #95 — 2026-10-02

- `relecture_web` : nouveau bouton « Rejeter (sans fusionner) » sur la page
  « branches d'un projet », pour supprimer un worktree et sa branche sans
  jamais tenter de les fusionner — cas réel : CCL signale lui-même que son
  travail fait doublon avec une autre issue déjà traitée, et que fusionner
  créerait des conflits inutiles. Jusqu'ici, seule une commande manuelle en
  terminal permettait ce geste.
- Garde-fou strictement inverse de « Supprimer la/les branche(s)
  fusionnée(s) » : refuse d'agir sur la branche principale, **et** refuse
  toute branche confirmée fusionnée (message flash renvoyant vers
  « Supprimer » dans ce cas). Même mécanique de suppression (`git worktree
  remove` puis `git branch -D`, ou `git branch -D` seule si le worktree a
  déjà été retiré).
- Confirmation forte dédiée (bandeau rouge, bouton nommé explicitement —
  ex. « Rejeter worktree-issue-88 », focus par défaut sur Annuler) avec un
  avertissement affichant, pour chaque branche concernée, le nombre de
  commits jamais fusionnés (`git log <branche principale>..<branche>`) —
  `git_info.get_nombre_commits_non_fusionnes` — pour que l'ampleur du
  travail perdu soit visible avant de confirmer une suppression réelle et
  définitive.
- Fermeture optionnelle de l'issue GitHub correspondante (case à cocher +
  champ de raison libre pour le commentaire) : numéro extrait du nom de la
  branche `worktree-issue-<N>` ou, à défaut, du sujet de son dernier commit
  (`git_info.numero_issue_depuis_nom_branche`), fermeture seulement si
  l'issue apparaît encore ouverte via `gh issue view`
  (`git_info.get_etat_issue_github` / `fermer_issue_github`) — n'agit pas si
  elle est déjà fermée (cas normal, le watcher CCL la ferme déjà lui-même).
  Cette vérification/fermeture via `gh` est volontairement isolée de la
  suppression du worktree : un échec (gh absent, non authentifié, pas de
  remote GitHub) est seulement rapporté à part, jamais bloquant —
  `relecture_web` ne dépend donc jamais de `gh`/GitHub pour sa fonction
  principale.
- Nouvelle route `/projet/<nom_projet>/rejeter`
  (`rejeter_worktrees_route`, `app.py`), nouvelles fonctions `git_info.py` :
  `get_nombre_commits_non_fusionnes`, `numero_issue_depuis_nom_branche`,
  `get_etat_issue_github`, `fermer_issue_github`.
- `RELECTURE_WEB_DOC.md` section 9 : nouvelle ligne « Rejeter (sans
  fusionner) » documentant le garde-fou et le niveau de confirmation.

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

## Issue #93 — 2026-09-28

- Refactor (`relecture_web/git_info.py`) : centralise derrière
  `_lancer_git` la quinzaine de fonctions qui exécutaient encore leur
  propre `subprocess.run(["git", "-C", ...])` en contournant ce point
  commun (`get_rapport_cherry_brut`, `get_patch_id_commit`,
  `trouver_commit_correspondant`, `get_diff_entre_commits`,
  `securiser_commit_orphelin`, `fusionner_worktree`, `supprimer_worktree`,
  `supprimer_branche`, `supprimer_branche_recuperation`, `revert_commit`,
  `pousser_branche`, `verifier_push_apres_timeout` (partie `git
  ls-remote`), `finaliser_commit_merge`) — `retraiter_fichier_conflit`
  passait déjà par `_lancer_git`, rien à y changer.
- `_lancer_git` a été étendu avec deux paramètres optionnels pour couvrir
  les usages qui ne s'y prêtaient pas encore : `timeout` (les appels à
  durée longue — push, merge, commit --no-edit — ou réseau — ls-remote —
  gardent leur délai propre, `TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`, au lieu
  du défaut `TIMEOUT_GIT`) et `entree` (texte transmis sur l'entrée
  standard, pour les pipes entre deux commandes git — `git show`/`git
  log -p` vers `git patch-id`, dans `get_patch_id_commit` et
  `trouver_commit_correspondant`).
- Aucun changement de comportement observable : mêmes commandes, mêmes
  codes de retour, mêmes messages d'erreur, mêmes timeouts — vérifié par
  test manuel sur un dépôt git temporaire (worktree, merge, push vers un
  remote local, conflit + finalisation de merge, branches de récupération,
  et les deux cas de pipe patch-id comparés à la commande brute).
- `fusionner_changelog_worktree` : son `git add`/`git commit` passaient
  déjà par `_lancer_git` avant cette issue ; seul son appel au script
  externe `scripts/fusionner_changelog.py` reste un `subprocess.run`
  distinct (ce n'est pas une commande git) — un commentaire dans le code
  signale désormais explicitement cette deuxième surface d'exécution,
  hors du périmètre de ce refactor.
- Prépare le terrain pour une future issue de routage local/SSH des
  commandes git (diagnostic de l'issue #91) : tout appel git de ce module
  passe maintenant par ce point d'entrée unique.

## 2026-09-28 — issue #92 (relecture_web)

`relecture_web` n'avait jusqu'ici aucune authentification, en écoute
stricte sur `127.0.0.1` — un choix assumé tant que l'outil restait
strictement local, mais un préalable bloquant avant d'envisager un jour un
accès réseau (LAN, ou exposition externe pour piloter un futur PC fixe
Windows) : `relecture_web` peut déclencher merge, push, suppression de
branches et de worktrees, un enjeu plus grand que `new_issue.py` à l'époque
où il n'avait lui non plus aucune protection.

- **Ajout — `relecture_web/auth.py`** : mot de passe haché en sha256
  (`relecture_web/mot_de_passe.conf`, jamais en clair, permissions 0600,
  gitignoré), comparaison en temps constant (`hmac.compare_digest`),
  `SECRET_KEY` Flask persistée (`relecture_web/secret_key.conf`, même
  protection) et génération d'un certificat auto-signé via `openssl`
  (`relecture_web/ssl/`, généré une seule fois puis réutilisé). Aucun code
  partagé avec `bridge_agent`/`new_issue.py` — même principe, implémentation
  propre à ce dépôt.
- **Ajout — `--set-password`** (`app.py`) : demande le mot de passe deux
  fois (confirmation, saisie masquée via `getpass`), puis quitte sans
  lancer le serveur.
- **Ajout — modes `--lan` / `--externe`** (`app.py`), mêmes noms que
  `bridge_agent` pour la cohérence : par défaut inchangé (`127.0.0.1`,
  HTTP, mot de passe jamais exigé) ; `--lan` (`0.0.0.0`, HTTP, sans mot de
  passe, réseau de confiance) ; `--externe` (`0.0.0.0`, HTTPS obligatoire,
  mot de passe obligatoire — refuse de démarrer sans mot de passe configuré,
  avec message clair). `--lan` et `--externe` sont mutuellement exclusifs
  (erreur explicite `argparse`).
- **Ajout — décorateur `@login_requis`** appliqué à toutes les routes
  existantes (`app.py`) : transparent tant que le mode courant n'exige pas
  de mot de passe (défaut, `--lan`), redirige vers `/connexion` sinon
  (`--externe` uniquement).
- **Ajout — routes `/connexion` et `/deconnexion`**, template
  `templates/connexion.html` (page autonome, hors barre latérale) et
  styles associés (`static/style.css`).
- **Session persistante** : `PERMANENT_SESSION_LIFETIME` fixé à 30 jours,
  `session.permanent = True` posé à la connexion réussie — une session
  survit désormais aux redémarrages fréquents de `relecture_web` (usage non
  permanent, relancé manuellement à chaque merge d'issue) sans devenir
  illimitée.
- **Doc** : `RELECTURE_WEB_DOC.md` (section « Lancement et modes réseau »)
  et `relecture_web/README.md` mis à jour — la mention « usage strictement
  local, aucune authentification » ne décrivait plus que le mode par défaut.
- **Hors périmètre** (rappel explicite de l'issue) : le mode SSH vers un
  futur PC fixe Windows (issue #91) n'est pas traité ici — cette issue pose
  seulement l'authentification, prérequis avant d'envisager un jour une
  exposition réelle. Le host d'écoute par défaut ne change pas.

## 2026-09-26 — issue #90 (relecture_web)

Sur la page Conflit, cliquer sur la flèche bleue puis sur la flèche orange
remplaçait le résultat au lieu de l'ajouter — impossible de garder les deux
versions l'une après l'autre, un cas fréquent (deux ajouts indépendants au
même endroit). Par ailleurs, transmettre le contenu d'un gros bloc de
conflit à Claude Chat obligeait à une capture d'écran, imprécise.

- **Ajout — « Garder les deux »** (`templates/conflit.html`) : quatrième
  flèche (⇅, violette) dans le groupe bleu/orange/✕ de chaque bloc. Place
  le contenu HEAD puis celui de la branche entrante à la suite dans le
  `<textarea>` du résultat, avec un saut de ligne entre les deux uniquement
  si le texte HEAD n'en a pas déjà un en fin. Les flèches bleue et orange
  restent des remplacements complets, inchangées.
- **Ajout — « Copier ce bloc »** (`templates/conflit.html`,
  `static/style.css`) : bouton `.bouton-copier` (📋) en coin haut-droit de
  chaque bloc du panneau gauche (lecture seule), copiant tout le texte
  affiché du bloc — en-têtes `<<<<<<<`/`>>>>>>>` et contenu des deux côtés
  compris, tel qu'affiché à l'écran — via le mécanisme `.bouton-copier`
  déjà utilisé ailleurs dans `relecture_web` (retour visuel bref identique).
- **`git_info.py`** : nouvelle fonction `_texte_affiche_bloc`, et nouveau
  champ `texte_affiche` par segment de conflit dans `_extraire_blocs_conflit`
  — précalcule côté serveur le texte exact du panneau gauche pour un bloc
  donné, avec la même règle de saut de ligne que « Garder les deux »
  (jamais de ligne vide dupliquée entre les deux moitiés).
- Le marqueur `=======` d'un conflit brut n'a volontairement pas été
  réintroduit dans l'affichage ni dans le texte copié : le panneau gauche
  remplaçait déjà ce séparateur par l'en-tête `>>>>>>> <branche>` au-dessus
  du contenu de la branche entrante (issue #59), qui joue le même rôle de
  repère visuel sans perdre le nom de la branche — copier « tel qu'affiché »
  respecte ce choix existant plutôt que de le contredire silencieusement.
- **Doc** : `RELECTURE_WEB_DOC.md` section 10 complétée avec les deux
  nouveaux boutons.
- Vérifié : `python3 -m py_compile git_info.py app.py` OK ; sortie de
  `_extraire_blocs_conflit`/`_texte_affiche_bloc` testée manuellement sur un
  conflit simple et sur un bloc à côté HEAD vide (cas des deux ajouts
  indépendants) — aucune ligne vide dupliquée dans les deux cas. Pas de
  suite de tests automatisés existante pour `relecture_web` à étendre.

## 2026-09-26 — issue #89 (relecture_web)

`lire_verrous_actifs` (`git_info.py`, ajoutée par #88) découpait le contenu
de chaque fichier `.lock` par `splitlines()` en supposant une paire
`clé=valeur` par ligne, avec un `partition("=")` ne coupant qu'au premier
signe `=`. En réalité, Bridge_Agent écrit tous les champs d'un verrou sur
une seule ligne séparés par des espaces (ex. `pid=213661 projet=bridge_agent
mode=ecriture rep=/home/alain/bridge_agent-issue649 claude_pgid=214244`) :
sur une seule ligne, `champs["pid"]` récupérait donc toute la fin de la
ligne au lieu du seul numéro, `_pid_vivant` échouait systématiquement, et
`lire_verrous_actifs` retournait toujours une liste vide — le badge « ⚠ CCL
travaille ici » (issue #88) ne s'affichait donc jamais, quel que soit
l'état réel des tâches. Confirmé en conditions réelles (trois worktrees
Bridge_Agent, verrous actifs lus = `[]` côté relecture_web).

- **Fix** (`git_info.py`, `lire_verrous_actifs`) : chaque ligne du fichier
  est d'abord découpée sur les espaces (`ligne.split()`) pour isoler les
  jetons `clé=valeur` individuels, avant de les répartir avec
  `partition("=")` — accepte aussi bien le format réel (tout sur une seule
  ligne) qu'un éventuel format à une paire par ligne, au cas où Bridge_Agent
  évoluerait. `_lignes_deja_pris_watcher` (citée dans le docstring comme
  suivant le même principe) ne fait qu'un test de sous-chaîne `"déjà pris"
  in ligne` — elle ne parse aucune paire `clé=valeur` et n'était pas
  concernée par ce bug.
- **Pourquoi les tests manuels de l'issue #88 ne l'ont pas détecté** : ils
  utilisaient apparemment un fichier `.lock` de test à une paire par ligne
  (`pid=...\nrep=...\nmode=...`), un format qui fonctionnait déjà avec
  l'ancien code — la documentation elle-même (`RELECTURE_WEB_DOC.md`)
  décrivait ce format à tort (« une ligne `pid=<pid>` et une ligne
  `rep=<chemin>` »), sans jamais avoir été confrontée à un vrai fichier
  généré par Bridge_Agent. Corrigée en conséquence.
- Revérifié manuellement les trois scénarios demandés : verrou à une seule
  ligne avec pid vivant → `rep=` retrouvé et `worktree_ccl_actif` renvoie
  `True` pour ce chemin ; pid mort → liste vide ; ancien format à une paire
  par ligne → toujours accepté (non-régression).
- `RELECTURE_WEB_DOC.md` mise à jour (section badges) pour décrire le
  format réel du fichier de verrou.

## 2026-09-26 — issue #88 (relecture_web)

Jusqu'ici, fusionner une branche puis supprimer son worktree sont deux clics
séparés — le second sûr techniquement (`git worktree remove` refuse de
lui-même s'il reste des modifications non commitées, et la suppression
revérifie elle-même à l'instant du clic que la branche est un ancêtre de la
cible), mais avec un vrai risque non couvert : qu'une tâche CCL travaille
encore dans ce worktree (reprise après redémarrage, cf. l'incident #73/#609
sur Bridge_Agent), auquel cas le supprimer romprait sa tâche.

- **Détection d'un worktree où CCL travaille** (`git_info.py`,
  `lire_verrous_actifs`/`worktree_ccl_actif`) : lit les fichiers de verrou
  actifs de Bridge_Agent (`logs/verrous/*.lock`, lignes `pid=`/`rep=`/`mode=`
  — `mode=` ajouté par #609 côté Bridge_Agent), ne retient un verrou que si
  son `pid` correspond à un processus toujours vivant (`os.kill(pid, 0)`),
  et compare son `rep=` au chemin réel du worktree d'une branche. Dégrade
  proprement à liste vide (aucune erreur) si Bridge_Agent n'est pas installé
  au même endroit ou si `logs/verrous/` est inaccessible.
- **Badge rouge « ⚠ CCL travaille ici »** affiché sur la branche concernée,
  dans la page projet, visible avant toute action — simple signal, comme le
  badge « worktree orphelin » existant : n'empêche pas de cliquer sur Merger
  seul (l'utilisateur peut savoir ce qu'il fait), mais le nouveau bouton
  combiné ci-dessous refuse d'agir tant qu'il est actif.
- **Nouveau bouton « Merger et supprimer »** (`app.py`,
  `merger_et_supprimer_route`) : à côté des boutons Merger et Supprimer la/les
  branche(s) fusionnée(s) existants (inchangés), enchaîne les deux dans le
  même clic — mêmes conditions d'éligibilité que le Merger seul aujourd'hui
  (branche pas la cible, pas de contenu doublons uniquement), plus le refus
  explicite (message flash) si le badge ci-dessus est actif pour la branche.
  Si le merge échoue (conflit, timeout non confirmé abouti, erreur), aucune
  suppression n'est tentée — comportement identique à aujourd'hui. Si le
  merge réussit mais que la suppression échoue ensuite (modifications non
  commitées détectées entre-temps par git, cas rare mais réel), les deux
  résultats sont rapportés séparément dans le message flash. Confirmation
  légère unique pour l'ensemble, décrivant les deux étapes.
- Testé de bout en bout sur des dépôts git temporaires avec un faux
  Bridge_Agent (verrou actif avec un pid réellement vivant, puis pid
  terminé) : badge affiché seulement avec verrou actif, bouton combiné
  refusé avec verrou actif (rien touché), accepté et fonctionnel une fois
  le verrou levé (merge + suppression du worktree et de la branche
  confirmés), et Merger seul vérifié toujours autorisé malgré le badge actif.
- Documentation : `RELECTURE_WEB_DOC.md` section 4 (nouveau badge) et
  section 9 (nouvelle ligne « Merger et supprimer »).

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

## 2026-09-24 — issue #75 (post-commit)

Le hook `post-commit` construisait le nom des fichiers exportés dans
`<projet>/Non_Lu/` à partir du message de commit en remplaçant chaque
caractère non ASCII par un « _ » : un message en français (donc accentué)
donnait un nom quasi illisible, ex. « docs: régénère le tableau des
projets... » devenait `1963797_docs__r__g__n__re_le_tableau_des_projets...`.

- **Translittération des accents avant construction du nom** (`post-commit`) :
  le message de commit passe désormais par `iconv -f utf-8 -t
  ascii//translit` (é → e, à → a, ç → c, œ → oe...) avant le remplacement des
  caractères restants encore hors `[:alnum:]-_` par un « _ » — seul ce qui
  n'a pas d'équivalent ASCII devient un souligné. `iconv` absent de la
  machine : repli silencieux sur le message brut (comportement identique à
  avant l'issue #75 pour ce cas précis).
- **Soulignés en double et de fin de nom évités** : `tr -cs` (squeeze) ramène
  les runs de soulignés consécutifs (produits par exemple par une ponctuation
  suivie d'un espace) à un seul, et un `sed` final retire un éventuel
  souligné terminal — y compris celui que la troncature à 50 caractères
  pouvait faire apparaître en coupant juste après un souligné. Longueur
  maximale du champ message inchangée (50 caractères).
- **Aucun impact sur `relecture_web`** : vérifié dans `git_info.py` et
  `resumes_info.py` — seuls le hash en tête de nom (`_extraire_hash`,
  découpe sur le premier « _ ») et le suffixe (`.diff`, `_resume.md`,
  `_annote.md`) sont exploités ; le contenu du champ « message » n'est
  jamais reparsé.
- **Fichiers déjà exportés inchangés** : aucun renommage rétroactif, seuls
  les futurs exports bénéficient de la translittération.
- **Déploiement** : `installer.sh` déploie le hook par **copie**
  (`cp "$HOOK_SOURCE" "$projet/.git/hooks/post-commit"`), pas par lien
  symbolique — les projets déjà installés gardent l'ancien hook tant que
  `./installer.sh` n'est pas relancé depuis ce dépôt (`relecture_bridge`)
  pour redéployer la version corrigée sur les 8 projets actifs.
- Testé sur un dépôt temporaire (`git init` + commits avec messages
  accentués, incluant un cas avec tiret cadratin et caractères composés) :
  noms de fichiers lisibles, sans double ni souligné final.
- Documentation : `RELECTURE_WEB_DOC.md` section 8 ne détaille pas la règle
  de remplacement de caractères (seulement le motif générique
  `<hash>_<message>.diff`) — rien à mettre à jour de ce côté.

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

## 2026-09-24 — issue #73 (relecture_web)

Retours d'un test réel complet des issues #69 à #72 sur un conflit
artificiel (projet `ecole`) : plusieurs frictions d'usage regroupées en
une seule issue (mêmes fichiers que #71/#72, dont un conflit de merge
réel entre ces deux-là avait déjà montré l'intérêt de grouper).

- **« Retraiter ce fichier » repositionné et allégé** : le bouton est
  désormais affiché juste à côté de « ✅ Finaliser le merge » (même bloc
  `.ligne-finaliser-merge`) quand tous les fichiers du merge en cours
  sont résolus, au lieu d'une section séparée plus bas ; il reste à côté
  du fichier concerné tant que d'autres fichiers sont encore en conflit.
  Sa confirmation JS est supprimée (action peu risquée : elle ne fait que
  refaire la résolution de ce fichier). Une fois l'action effectuée,
  `relecture_web` amène directement sur la page Conflit du fichier remis
  en conflit plutôt que sur la page projet (`app.py`,
  `retraiter_fichier_conflit_route`).
- **Page Conflit — zones de résultat agrandies** : chaque `<textarea>` du
  panneau droit prend désormais au moins la hauteur du bloc correspondant
  du panneau gauche (`align-items: stretch` sur la grille CSS partagée,
  `style.css`) — sur un gros bloc de conflit (ex. un tableau de
  documentation), l'édition n'est plus pénible dans une zone restée
  minuscule.
- **Page Conflit — bouton Rafraîchir** : même comportement que celui déjà
  présent sur la page projet (simple lien GET vers l'URL courante, jamais
  de resoumission de formulaire) — utile notamment après le refus « le
  fichier a changé depuis l'affichage » de « Traiter tous les blocs »,
  dont le message demande de recharger la page.
- **Confirmations raccourcies et unifiées** (`ouvrirConfirmation`,
  `base.html`, remplace `confirmationForte`) : une seule ligne principale
  au format « Action + objet + projet » (ex. « Merger worktree-issue-72
  dans main — relecture_bridge ») plutôt qu'un long texte explicatif ; un
  avertissement éventuel (ex. bloc(s) au résultat vide pour « Traiter
  tous les blocs ») affiché en premier et mis en évidence, jamais noyé en
  fin de message ; la commande git équivalente conservée en petit texte
  discret sous la ligne principale ; le bouton de validation continue de
  porter le nom de l'action, jamais un OK générique ; focus par défaut
  sur Annuler dans tous les cas. Les confirmations légères (Merger,
  anomalie de « Traiter tous les blocs ») passent désormais par cette
  même fenêtre `relecture_web` en variante neutre (non rouge) plutôt que
  par le `confirm()` natif du navigateur, pour permettre ce format uniforme
  et coloré ; les confirmations fortes (Push, suppressions) gardent leur
  couleur d'alerte rouge (`modal-confirmation--forte`).
- **Couleur d'accent du projet** (`git_info.py` : `normaliser_couleur_hex`,
  `couleur_texte_lisible`) : lecture tolérante d'une colonne « Couleur »
  optionnelle en dernière position du tableau des projets actifs de
  `BRIDGE_AGENT_DOC.md` (hexadécimal), lors du même chargement réseau que
  le reste de la liste — colonne absente, vide ou invalide -> pas de
  couleur, jamais d'erreur (repli en douceur tant que l'issue bridge_agent
  qui ajoute cette colonne n'est pas encore en place). Utilisée comme
  bandeau dans les fenêtres de confirmation, comme chip dans l'en-tête de
  la page projet et de la page Conflit, et comme pastille dans la barre
  latérale — texte noir ou blanc choisi automatiquement pour rester
  lisible sur la couleur configurée (formule de luminance perçue YIQ), afin
  de ne pas confondre deux projets aux noms proches (`bridge_agent`/
  `relecture_bridge`, `alchess`/`chesscoach`).
- Doc : mise à jour de `RELECTURE_WEB_DOC.md`, sections 1 (nouvelle
  colonne lue), 2 (en-têtes, barre latérale), 9 (format des confirmations,
  « Retraiter » sans confirmation), 10 (repositionnement de « Retraiter »,
  hauteur des zones de résultat, Rafraîchir sur la page Conflit).

## 2026-09-24 — issue #72 (relecture_web)

- **Bouton « Retraiter le fichier en conflit »** : dans la section « ⚠
  Fusion en conflit » de la page projet, chaque fichier déjà résolu
  (`git add` fait) pendant le merge en cours porte désormais un bouton
  « 🔁 Retraiter ce fichier » — que d'autres fichiers restent en conflit
  ou que tous soient résolus (dans ce cas, à côté de « ✅ Finaliser le
  merge »). Le clic exécute `git checkout --conflict=merge --
  <chemin>` (nouvelle fonction `retraiter_fichier_conflit`,
  `relecture_web/git_info.py`), qui recrée les marqueurs de conflit
  d'origine pour ce fichier précis à partir du mécanisme « resolve-undo »
  de git (`git ls-files --resolve-undo`, nouvelle fonction
  `get_fichiers_resolus_merge`) ; le fichier redevient `UU` et réapparaît
  dans la liste des fichiers en conflit, prêt à être rouvert depuis la
  page Conflit.
  - Garde-fous côté serveur, revérifiés à partir de l'état git actuel :
    un merge réellement en cours (`MERGE_HEAD` présent, même principe que
    « Finaliser le merge ») et un chemin figurant dans la liste actuelle
    des fichiers résolus (jamais construit à l'aveugle depuis le seul
    paramètre d'URL, même principe que la page Conflit).
  - Confirmation JS légère avant soumission (efface la résolution déjà
    appliquée à ce fichier, en entier).
  - Message flash signalant que les marqueurs recréés portent les
    libellés génériques `ours`/`theirs` au lieu de `HEAD` et du nom de la
    branche entrante — vérifié que la page Conflit reste lisible dans ce
    cas (les libellés de branche entrante de l'issue #70 affichent alors
    simplement « theirs »).
  - Nouvelle route `POST
    /projet/<nom_projet>/conflit/<chemin_relatif>/retraiter`
    (`relecture_web/app.py`).
- **Correction de documentation (`RELECTURE_WEB_DOC.md`, section 9)** :
  le point de non-retour d'un fichier résolu pendant un merge n'est pas
  le `git add` de résolution — vérifié en local sur un conflit de test
  (git 2.43) : `git ls-files --resolve-undo` conserve les informations
  nécessaires, et `git checkout --conflict=merge -- <chemin>` recrée les
  marqueurs de conflit d'origine même après ce `git add` (seule
  différence : libellés `ours`/`theirs` génériques au lieu de `HEAD` et
  du nom de la branche entrante). La vraie limite reste la finalisation
  du merge (`git commit`, bouton « Finaliser le merge ») : une fois ce
  commit fait, `MERGE_HEAD` disparaît et `git merge --abort` cesse de
  fonctionner (vérifié). Section 10 complétée avec la description de la
  nouvelle action.

## 2026-09-24 — issue #71 (relecture_web)

- **Confirmations graduées selon le risque**, contre la fatigue de
  confirmation constatée en test réel (toutes les actions passaient par
  la même fenêtre native `confirm()`, au point que le clic sur OK
  devenait un réflexe et que le garde-fou ne protégeait plus rien).
  Trois niveaux désormais :
  - **Aucune confirmation** (application directe) : Sécuriser (un ou
    tous), Nettoyer ce projet / tous les projets, Traiter ce bloc,
    Traiter tous les blocs (sauf anomalie, voir ci-dessous), Finaliser
    le merge, Revert, Comparer / Comparer la sélection / Générer
    rapport.
  - **Confirmation légère** (fenêtre native `confirm()` conservée) :
    Merger — modifie la branche cible mais reste local et annulable
    tant que le merge n'est pas finalisé. « Traiter tous les blocs »
    repasse aussi par cette confirmation, mais uniquement si au moins
    un bloc a un résultat vide (anomalie potentielle — suppression de
    bloc), avec le message d'avertissement déjà existant.
  - **Confirmation forte** (nouvelle fenêtre propre à `relecture_web`,
    `#modal-confirmation-forte` dans `templates/base.html`, style
    `.modal-forte*`/`.bouton--danger`/`.bouton--annuler` dans
    `static/style.css`) : Push, Supprimer la/les branche(s)
    fusionnée(s), Supprimer la/les branche(s) de récupération (panneau
    d'actions de la page projet **et** suppression groupée depuis
    « Comparer la sélection »). Visuellement distincte (couleur
    d'alerte rouge), bouton de validation qui décrit l'action réelle
    avec sa portée (ex. « Pousser 2 branches vers GitHub », « Supprimer
    test_conflit_a ») au lieu d'un OK générique, focus par défaut sur
    Annuler pour qu'un Entrée réflexe ne valide rien, commande git
    équivalente toujours affichée. Implémentée en JS pur (fonction
    `confirmationForte()` dans `base.html`, réutilisée par
    `projet.html` et `comparer_selection.html`) — aucune route serveur
    ajoutée, les indicateurs « Push en cours... » / « Fusion en
    cours... » (issue #49) sont inchangés après validation.
  - Fichiers modifiés : `templates/base.html`, `templates/projet.html`,
    `templates/comparer_selection.html`, `templates/conflit.html`,
    `templates/branche.html`, `templates/index.html`,
    `static/style.css`. Aucun fichier Python touché (aucune route ni
    garde-fou serveur n'a changé, seule la confirmation côté
    navigateur est concernée).
- **Vérification de réversibilité** demandée par l'issue pour les
  actions passant en « aucune confirmation » au motif qu'elles sont
  réversibles : « Traiter ce bloc » / « Traiter tous les blocs »
  écrivent directement le fichier, sans fonction d'annulation dans
  `relecture_web` lui-même. Le geste reste réversible en pratique tant
  que le merge n'est pas finalisé, mais uniquement via une commande
  manuelle en terminal (`git checkout --conflict=merge -- <chemin>`
  tant que `git add` n'a pas eu lieu sur ce fichier précis, sinon
  `git merge --abort` qui annule tout le merge, pas seulement ce
  fichier) — jamais un bouton de `relecture_web`. Point documenté dans
  `RELECTURE_WEB_DOC.md` (section 9) plutôt que de retirer la
  confirmation ou d'en ajouter une nouvelle, comme demandé par l'issue.
- `RELECTURE_WEB_DOC.md` (section 9) : remplacement de l'affirmation
  « toutes les actions passent par `confirm()` » par la description des
  trois niveaux, et mise à jour de la colonne Garde-fou de chaque ligne
  du tableau pour indiquer son niveau. Ajout de la ligne « Traiter ce
  bloc », absente du tableau jusqu'ici bien que déjà listée comme
  action existante dans le texte de la section.

## 2026-09-24 — issue #70 (relecture_web)

- Correction de deux problèmes constatés en test réel (suite de
  l'issue #69) sur la page Conflit
  (`relecture_web/templates/conflit.html`) :
  - **Numérotation dans l'avertissement « résultat vide »** : la
    confirmation de « Traiter tous les blocs » listait les blocs vides
    avec leur index interne 0-based (« Bloc(s) au résultat vide : 0, 1 »),
    incohérent avec la navigation de la même page qui affiche « Bloc 1 /
    3 ». Le message affiche désormais la position 1-based (celle de la
    navigation) au lieu de l'index interne — seul l'affichage change, les
    index transmis au serveur (`index_bloc`, champs cachés
    `texte_final_<index>`) restent le 0-based habituel de
    `_trouver_blocs_conflit`.
  - **Libellé « version locale » inversé** : le texte d'en-tête et
    l'infobulle de la flèche orange décrivaient à tort l'orange comme la
    « version locale », alors que la version locale est HEAD (la branche
    actuelle, en bleu) — l'orange est la branche entrante, celle qu'on
    fusionne (portée par le marqueur `>>>>>>>`). Le texte d'en-tête et
    l'infobulle de la flèche orange parlent maintenant de « branche
    entrante », avec son nom affiché entre parenthèses quand il est
    disponible (extrait du marqueur `>>>>>>>` de chaque bloc, resp. du
    premier bloc du fichier pour le texte d'en-tête général) ; l'infobulle
    de la flèche bleue est précisée en « HEAD (branche actuelle) » pour la
    cohérence. `relecture_web/git_info.py` n'a pas été modifié (numérotation
    et format du marqueur `>>>>>>>` déjà exploitables tels quels).
- `RELECTURE_WEB_DOC.md` (section 10) : la terminologie ours/HEAD/bleu et
  theirs/branche entrante/orange était déjà correcte, aucune correction
  nécessaire sur ce point ; ajout d'une précision sur la numérotation
  1-based de la liste des blocs vides dans la confirmation JS, par
  opposition à l'index 0-based interne inchangé.

## 2026-09-24 — issue #69 (relecture_web)

- Ajout d'un bouton « 🔄 Rafraîchir » sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : simple lien GET vers l'URL
  courante de la page (pas un `location.reload()`), pour recharger l'état
  git à jour après une action faite en terminal sans jamais risquer de
  faire réapparaître l'avertissement « resoumettre le formulaire » du
  navigateur qu'un vrai F5 peut déclencher après un POST.
- Ajout d'un bouton « 📋 Copier » réutilisant le composant générique
  `.bouton-copier` déjà utilisé ailleurs (hash, nom de branche) pour
  copier dans le presse-papiers le chemin d'un fichier en conflit tel que
  renvoyé par `git status` : à côté de chaque fichier listé dans la
  section « ⚠ Fusion en conflit » de la page projet, et dans l'en-tête de
  la page Conflit. Purement côté navigateur, aucune route serveur.
- Ajout d'un bouton « Traiter tous les blocs » sur la page Conflit,
  variante « tout ou rien » de « Traiter ce bloc » qui applique en une
  seule opération le contenu de chaque `<textarea>` du panneau droit au
  bloc de conflit correspondant, sans recharger la page entre chaque
  bloc :
  - `relecture_web/git_info.py` : `lire_conflits_fichier` calcule
    désormais aussi une empreinte (sha256 du contenu) transmise à
    l'affichage ; nouvelle fonction `resoudre_tous_blocs_conflit`,
    réutilisant `_trouver_blocs_conflit` (même numérotation que
    l'affichage et que « Traiter ce bloc ») — refuse tout le traitement
    (aucun bloc écrit) si le nombre de blocs ou l'empreinte ne
    correspondent plus à ce qui a été affiché ; applique les
    remplacements du dernier bloc vers le premier pour que les décalages
    d'index provoqués par un remplacement ne perturbent jamais les blocs
    restant à traiter ; `git add` automatique une fois tous les blocs
    remplacés, comme pour le traitement bloc par bloc.
  - `relecture_web/app.py` : nouvelle route
    `POST /projet/<nom_projet>/conflit/<chemin_relatif>/traiter-tous`
    (`traiter_tous_blocs_conflit_route`).
  - `relecture_web/templates/conflit.html` : bouton « Traiter tous les
    blocs (N) », confirmation JavaScript avant soumission qui signale
    explicitement les blocs dont le textarea est vide (suppression du
    bloc). « Traiter ce bloc » reste disponible, inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` sections 9 et 10 pour les
  trois ajouts.

## 2026-09-23 — issue #68 (relecture_web)

- Ajout d'un bouton « 🧹 Nettoyer ce projet » sur la page « branches d'un
  projet » (`relecture_web/templates/projet.html`), à côté du titre —
  évite de repasser par la liste des projets pour nettoyer les résumés
  `Non_Lu/` déjà pushés du seul projet sur lequel on vient de travailler.
- Nouvelle route `POST /projet/<nom_projet>/nettoyer`
  (`nettoyer_projet_route`, `relecture_web/app.py`) : réutilise la même
  logique et le même garde-fou de sécurité que
  `nettoyer_tous_les_projets_route` (issue #17) — `lister_fichiers_resumes_pushes`
  puis `_supprimer_fichiers` — limitée à `projet['dossier_relecture']` /
  `projet['repertoire']` du seul projet affiché, avec confirmation
  JavaScript avant soumission.
- Le bouton global « Nettoyer tous les projets » (page d'accueil) est
  inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 9 (nouvelle ligne
  « Nettoyer ce projet » dans le tableau des actions).

## 2026-09-23 — issue #67 (relecture_web)

- Ajout d'un badge dédié `⚠️ worktree orphelin — repli signalé`, distinct
  du badge `worktree` habituel, sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : affiché pour tout worktree
  secondaire dont le chemin apparaît dans une ligne « déjà pris » de
  `logs/watcher-<projet>.log` — le journal que Bridge_Agent écrit
  (issue #589 côté Bridge_Agent) quand une tâche `mode_write` n'a pas pu
  obtenir son propre worktree et est retombée sur `REP_TRAVAIL`.
- `relecture_web/git_info.py` : nouvelles fonctions `_lignes_deja_pris_watcher`
  (lecture seule best-effort de `logs/watcher-<projet>.log` dans le
  répertoire du projet `bridge_agent`, absent/illisible -> liste vide) et
  `worktree_orphelin_signale` (correspondance de chemin dans ces lignes).
  Appelées depuis `collect_etat_projets` pour renseigner
  `worktree["orphelin_signale"]` sur chaque worktree secondaire.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 4 (liste des badges).

## 2026-09-22 — issue #66 (relecture_web)

- Après un timeout de 120s sur Push, Merger ou Finaliser le merge, le
  message flash renvoyait systématiquement Alain vers une vérification
  manuelle en ligne de commande (« a dépassé le délai, mais a pu se
  terminer entre-temps — vérifiez manuellement si besoin »), y compris
  quand l'opération avait en réalité bel et bien abouti — constaté sur
  `bridge_agent` (worktree-issue-588) : message de timeout affiché,
  mais fusion réellement terminée (commit de fusion présent, copie de
  travail propre), vérifié à la main via `git status`/`git log`/`git
  worktree list`.
  - `git_info.py` : trois nouvelles fonctions de vérification post-timeout,
    chacune appelée uniquement depuis le bloc `except
    subprocess.TimeoutExpired:` de l'action correspondante :
    - `verifier_push_apres_timeout(repertoire, branche)` — compare le
      commit local de `branche` au commit réellement exposé par le
      remote via `git ls-remote` (pas le suivi local
      `refs/remotes/...`, qui ne serait mis à jour que par un `fetch` et
      pourrait rester périmé). Retourne `ok` = True (push confirmé),
      False (push non abouti), ou None si la vérification elle-même n'a
      pas pu aboutir (réseau).
    - `verifier_merge_apres_timeout(repertoire, branche_cible,
      branche_source)` — distingue trois états réels via `MERGE_HEAD`
      et `git merge-base --is-ancestor` : fusion aboutie, fusion arrêtée
      sur des conflits (pas un échec, la page de résolution de conflits
      prend le relais normalement), ou fusion non aboutie.
    - `verifier_finalisation_merge_apres_timeout(repertoire)` — dans ce
      flux précis, seul le commit visé par `finaliser_commit_merge` peut
      faire disparaître `MERGE_HEAD` ; sa disparition signale donc de
      façon fiable que le commit a bien été créé avant que le timeout
      Python ne tue le process (probablement resté bloqué dans le hook
      `post-commit`).
  - `app.py` : les trois blocs `except subprocess.TimeoutExpired:`
    (`pousser_branches_route`, `merger_branches_route`,
    `finaliser_merge_route`) appellent désormais la vérification
    correspondante et affichent un message flash final reflétant l'état
    réel constaté (succès confirmé, échec confirmé, conflits en attente,
    ou état indéterminé avec la raison), au lieu du message générique
    précédent.
  - `RELECTURE_WEB_DOC.md` (section 9, lignes **Push**/**Merger**/
    **Finaliser le merge** du tableau des actions, et section 10) mise à
    jour en conséquence.
  - Testé manuellement sur des dépôts git temporaires (push déjà abouti,
    push jamais poussé, merge déjà fusionné, merge en conflit non
    résolu, merge non finalisé) pour valider les trois états retournés
    par chaque fonction de vérification.

## 2026-09-22 — issue #64 (relecture_web)

- `finaliser_commit_merge` (`git_info.py`) plantait avec un
  `subprocess.TimeoutExpired` non rattrapé après seulement 10s
  (`TIMEOUT_GIT`) : le `git commit --no-edit` qu'elle exécute déclenche
  le hook `post-commit` du projet, qui appelle Claude en ligne de
  commande pour générer le résumé fonctionnel (`resumer_diff.py`) — une
  opération pouvant dépasser 10s sur un fichier volumineux (vécu
  concrètement sur `RELECTURE_WEB_DOC.md`). Push et Merger utilisent
  déjà `TIMEOUT_GIT_LONG` (120s) pour cette même raison de fond (issue
  #39), mais `finaliser_commit_merge` n'avait pas été aligné dessus lors
  de sa création (issue #61).
  - `git_info.py` : `finaliser_commit_merge` passe maintenant
    `timeout=TIMEOUT_GIT_LONG` (120s) à l'appel `git commit --no-edit`,
    en cohérence avec `pousser_branche` et `fusionner_worktree`.
  - `app.py` (`finaliser_merge_route`) : ajout d'un `try/except` autour
    de l'appel à `finaliser_commit_merge`, sur le même modèle que
    `pousser_branches_route`/`merger_branches_route` (issues #39/#61) —
    un dépassement du délai malgré tout, ou toute autre erreur
    inattendue, est désormais rapporté par un message flash explicite
    plutôt que de faire planter la requête avec une page d'erreur brute.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Finaliser le merge** du
    tableau des actions, et section 10) mise à jour en conséquence.

## 2026-09-22 — issue #63 (relecture_web)

- Correction d'un cas où la fusion automatique du `CHANGELOG-<N>.md`
  (issue #51) réussissait bel et bien côté script, mais restait sans effet
  durable pour un projet dont le worktree du merge n'était pas déjà la
  branche courante (cas de `bridge_agent`, contrairement à
  `relecture_bridge` où la branche courante coïncide généralement avec la
  branche cible) : `CHANGELOG-585.md`/`CHANGELOG-586.md` restaient non
  fusionnés malgré des prérequis (`CHANGELOG.md`, `scripts/
  fusionner_changelog.py`) pourtant bien présents.
  - Cause réelle : `fusionner_changelog_worktree` lançait le script (qui
    modifie `CHANGELOG.md` et supprime les `CHANGELOG-<N>.md` sur disque)
    mais ne commitait jamais ce résultat. `fusionner_worktree` bascule
    ensuite potentiellement sur la branche d'origine (`doit_basculer`,
    quand la branche cible n'a pas de worktree dédié) : un `git checkout`
    avec un `CHANGELOG.md` modifié en local est refusé par git dès que la
    branche de destination diffère sur ce fichier — bascule qui échouait
    silencieusement (retour jamais vérifié), laissant le dépôt dans un état
    non commité que toute opération git ultérieure pouvait écraser sans
    aucun message d'erreur.
  - `git_info.py` : `fusionner_changelog_worktree` commite désormais
    immédiatement (`git commit -a`) le résultat du script dès qu'il a
    réussi, rendant la fusion durable indépendamment de ce que fait
    l'appelant ensuite. `fusionner_worktree` vérifie maintenant le code
    retour du `checkout` de retour et remonte l'échec via un nouveau champ
    `erreur_retour_branche` plutôt que de l'ignorer.
  - `app.py` : nouveau message flash dédié si `erreur_retour_branche` est
    renseigné, pour ne plus jamais laisser un tel échec invisible.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne « Merger ») : documentation de
    la fusion automatique du changelog (jusqu'ici non documentée depuis
    l'issue #51) et de ce correctif de durabilité.

## 2026-09-22 — issue #62 (relecture_web)

- Journalisation persistante des tentatives de fusion automatique du
  CHANGELOG (déclenchée après un merge, issue #51) : jusqu'ici, le
  résultat (succès/échec) n'était visible que via un message flash
  éphémère, affiché une seule fois juste après l'action — vécu
  concrètement quand Alain a mergé deux branches sur `bridge_agent`
  depuis `relecture_web` sans repérer le détail du message, sans moyen
  après coup de confirmer si la fusion automatique avait réellement
  réussi.
  - `git_info.py` : nouveau fichier de log `relecture_web/changelog_fusion.log`
    (non commité, voir `.gitignore`), une ligne par tentative réellement
    lancée (script trouvé ou non) — date/heure ISO, projet, commande
    exécutée, résultat (`SUCCES`/`ECHEC`), message d'erreur le cas
    échéant. Écrite par la nouvelle fonction `_journaliser_fusion_changelog`,
    appelée depuis `fusionner_changelog_worktree` (qui accepte maintenant
    un paramètre optionnel `nom_projet`). Une erreur d'écriture du journal
    reste silencieuse pour l'utilisateur — elle ne doit jamais faire
    échouer la fusion elle-même.
  - `fusionner_worktree` propage `nom_projet` jusqu'à
    `fusionner_changelog_worktree` ; `app.py` passe `projet["nom"]` lors de
    l'appel dans `merger_branches_route`.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Merger** du tableau des
    actions) mise à jour en conséquence.

## 2026-09-21 — issue #61 (relecture_web)

- Ajout du bouton **« Finaliser le merge »**, pour clore le dernier geste
  manuel encore nécessaire après une résolution de conflits entièrement
  faite depuis `relecture_web` (issues #55/#56/#59) : la section « Fusion
  en conflit » de la page projet accepte automatiquement chaque fichier
  résolu (`git add`), mais le commit du merge lui-même restait à taper en
  terminal — cassant le flux visé par tout ce chantier.
  - `git_info.py` : deux nouvelles fonctions, `get_merge_en_cours`
    (`git rev-parse --verify --quiet MERGE_HEAD`, distingue un vrai merge en
    cours d'un simple conflit `UU` isolé — cherry-pick/revert en conflit ne
    créent jamais `MERGE_HEAD`) et `finaliser_commit_merge`
    (`git commit --no-edit`, l'équivalent non-interactif de `git commit`
    sans `-m` : accepte tel quel le message déjà préparé par git dans
    `.git/MERGE_MSG`, sans ouvrir d'éditeur inutilisable depuis une page
    web).
  - `app.py` : `projet_route` calcule désormais `merge_en_cours` et
    `peut_finaliser_merge` (= merge en cours ET plus aucun fichier en
    conflit) pour chaque projet. Nouvelle route
    `POST /projet/<nom_projet>/finaliser-merge` — revalide l'état git
    actuel (pas la seule page déjà affichée) avant d'appeler
    `finaliser_commit_merge`, pour ne jamais tenter un commit partiel même
    sur un formulaire soumis depuis une page obsolète.
  - `templates/projet.html` : la section « Fusion en conflit » reste
    affichée tant qu'un merge est en cours, mais bascule d'une liste de
    fichiers à résoudre vers un unique bouton « ✅ Finaliser le merge » une
    fois tous les fichiers résolus — jamais les deux à la fois, et le
    bouton n'apparaît pas tant qu'il reste un seul fichier en conflit.
    Même pattern de confirmation que les autres actions du système
    (`confirm()` JS avec commande équivalente affichée,
    `git -C <repertoire> commit --no-edit`).
  - `RELECTURE_WEB_DOC.md` (section 9, tableau des actions, et section 10)
    mises à jour en conséquence.

- Correction du chevauchement visuel dans l'en-tête de la page **Conflit**
  (`conflit.html`) constaté après le passage à la vue à deux panneaux
  (issue #59) : le libellé « Résultat final — éditable » du panneau droit
  se superposait avec le bouton de navigation « Bloc suivant » (►) et le
  compteur de position (« Bloc n / total »).
  - Cause : la colonne centrale de la grille CSS partagée par l'en-tête
    et le corps (`.conflit-vue__entetes`, `.conflit-vue__corps`) était
    fixée à `72px`, largeur suffisante pour les trois petites flèches du
    corps mais trop étroite pour contenir les boutons de navigation
    (◀ / ▶) et le texte « Bloc n / total » de l'en-tête — ce contenu
    débordait donc visuellement sur la colonne de droite.
  - Correctif (`static/style.css`) : l'en-tête (`.conflit-vue__entetes`)
    utilise désormais sa propre largeur de colonne centrale,
    `minmax(96px, auto)`, qui s'élargit automatiquement pour accueillir
    la navigation sans jamais empiéter sur les colonnes voisines ; le
    corps (`.conflit-vue__corps`, les trois flèches par bloc) conserve
    sa colonne fixe de `72px`, inchangée. Ajout de `min-width: 0` et
    `overflow-wrap: break-word` sur les libellés (`.conflit-vue__entete-titre`)
    et de `flex-wrap: wrap` sur le conteneur de navigation
    (`.conflit-vue__entete-titre--milieu`) pour rester lisible sans
    chevauchement même à largeur de fenêtre réduite.

## 2026-09-21 — issue #59 (relecture_web)

- Page **Conflit** (issues #55, #56) refondue en vue à deux panneaux
  synchronisés, remplaçant entièrement l'ancien bloc isolé + textarea
  séparé (pas un mode alternatif en plus) :
  - Panneau gauche : le fichier complet en lecture seule, bloc de
    conflit affiché à sa vraie place dans le texte environnant (HEAD en
    bleu, version locale en orange), inchangé sur ce point.
  - Panneau droit : le même fichier complet, éditable, avec à
    l'emplacement de chaque bloc le `<textarea>` de composition du
    texte final (mécanisme de résolution par bloc de l'issue #56
    inchangé côté serveur — `resoudre_bloc_conflit` et la route
    `traiter_bloc_conflit_route` ne bougent pas).
  - Trois flèches par bloc entre les deux panneaux : bleue (copie
    « ours »/HEAD dans le résultat), orange (copie « theirs »/version
    locale), verte (vide le résultat). Le texte reste modifiable à la
    main après un transfert — jamais une copie figée.
  - Boutons « ◀ » / « ▶ » dans l'en-tête pour naviguer entre les blocs
    d'un même fichier sans quitter la page (position affichée « Bloc
    n / total », bloc ciblé mis en évidence et centré à l'écran).
- Défilement synchronisé obtenu par construction : les deux panneaux et
  leurs en-têtes partagent une seule grille CSS à trois colonnes
  (gauche / flèches / droite), construite ligne par ligne à partir des
  mêmes segments — une seule barre de défilement pour toute la page,
  pas deux volets indépendants à recaler en JS.
- `base.html` : ajout du bloc Jinja `classe_contenu` (vide par défaut)
  pour permettre à une page de s'afficher plus large ; `conflit.html`
  l'utilise (`contenu-principal--large`, 1500px) pour donner de la
  place aux deux panneaux côte à côte.
- Aucun changement côté serveur (`app.py`, `git_info.py`) : uniquement
  `conflit.html`, `base.html` et `style.css`.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour pour décrire la
  nouvelle vue à deux panneaux (issue #59).
- Vérifié : le template Jinja se parse sans erreur ; relecture visuelle
  du HTML/CSS/JS généré (pas de serveur de test disponible dans ce
  périmètre pour un essai navigateur complet).

## Issue #58 — fetch_projets() doit se replier sur la résolution normale si le forçage IPv4 échoue

- `relecture_web/git_info.py` : extraction du téléchargement de
  `DOC_URL` dans `_telecharger_doc_projets(forcer_ipv4)`, réutilisable
  avec ou sans le monkeypatch IPv4 introduit par l'issue #57.
  `fetch_projets()` tente d'abord l'appel avec IPv4 forcé (rapide dans
  le cas normal) ; s'il échoue pour n'importe quelle raison (coupure
  réseau ponctuelle, IPv4 momentanément indisponible...), une seconde
  tentative est faite en résolution normale (IPv4 ou IPv6, au choix
  d'`urllib`) avant d'abandonner avec `ErreurRecuperationProjets`. Une
  perturbation réseau passagère ne provoque donc plus d'échec total du
  chargement de la liste des projets — au pire un chargement plus lent
  cette fois-là.

## Issue #57 — fetch_projets() met 80s au lieu de 0,4s (résolution IPv6)

- `relecture_web/git_info.py` : `fetch_projets()` force désormais la
  résolution IPv4 le temps de l'appel `urlopen(DOC_URL)`, en remplaçant
  temporairement `socket.getaddrinfo` par une variante qui filtre sur
  `socket.AF_INET`, restaurée dans un `finally` juste après l'appel réseau.
  Corrige un ralentissement de 80s (4x `TIMEOUT_RESEAU`, retries IPv6 en
  série) à 0,2-0,4s, sans toucher aux commandes `git` (qui n'utilisent pas
  ce mécanisme) ni au reste de l'application.

## 2026-09-21 — issue #56 (relecture_web)

- Page **Conflit** (issue #55) : à côté de chaque bloc affiché en
  lecture seule, ajout d'un `<textarea>` éditable pré-rempli avec la
  version « ours », dans lequel Alain compose le texte final à garder
  (copie d'une des deux versions, combinaison, ou tout autre texte, y
  compris vide pour supprimer le bloc). Bouton « Traiter ce bloc »
  (confirmation JS avec aperçu du texte) qui remplace ce bloc précis —
  marqueurs `<<<<<<<`/`=======`/`>>>>>>>` compris — par ce texte dans
  le fichier réel, en local uniquement.
- Nouvelle route `POST /projet/<nom_projet>/conflit/<chemin>/traiter` :
  revalide que le fichier est toujours en conflit avant d'écrire, comme
  la route de lecture voisine. Redirige vers la même page de conflit
  s'il reste des blocs (le suivant apparaît naturellement en premier),
  ou vers la page du projet avec un message clair une fois le fichier
  entièrement résolu.
- `git_info.py` : `_extraire_blocs_conflit` (issue #55) factorisée avec
  une nouvelle `_trouver_blocs_conflit`, partagée avec la nouvelle
  `resoudre_bloc_conflit` — garantit que la numérotation des blocs
  (0-based, ordre d'apparition) est strictement identique entre
  affichage et résolution, pour qu'une soumission ne puisse jamais
  toucher le mauvais bloc. Si le fichier a changé entre l'affichage et
  la soumission au point que le numéro de bloc ne corresponde plus
  (bloc déjà traité, fichier modifié ailleurs), `resoudre_bloc_conflit`
  échoue proprement avec un message d'erreur plutôt que d'écrire à
  l'aveugle. Lecture/écriture strictement UTF-8 (contrairement à la
  lecture seule d'issue #55, qui tolère les octets invalides puisqu'elle
  n'écrit jamais).
- Une fois le dernier bloc d'un fichier traité, `git add <fichier>` est
  lancé automatiquement pour marquer sa résolution — le commit et le
  push restent des gestes manuels d'Alain, volontairement non
  automatisés.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour (titre et contenu :
  détection **et résolution**, suppression de la mention "strictement
  en lecture seule" devenue fausse).
- Testé manuellement (dépôt de test jetable hors périmètre) : bloc
  unique, blocs multiples, texte final vide (suppression du bloc),
  index de bloc obsolète (erreur propre sans écriture) — tous les cas
  se comportent comme attendu, `git add` ne se déclenche qu'au dernier
  bloc.

## 2026-09-21 — issue #55 (relecture_web)

- Nouvelle section **⚠ Fusion en conflit** sur la page « branches d'un
  projet » : détecte, via `git status --porcelain` (codes `UU`, `AA`,
  `DD`, `AU`, `UA`, `DU`, `UD`), les fichiers en conflit d'une fusion
  non résolue et les liste, sans avoir à taper `git status`/`grep` en
  terminal.
- Nouvelle page **Conflit** (`/projet/<nom_projet>/conflit/<chemin>`)
  pour un fichier sélectionné : localise chaque bloc entre `<<<<<<<`,
  `=======` et `>>>>>>>`, affiche les deux versions dans des blocs de
  texte à fond coloré distinct (bleu « ours »/`HEAD`, orange « theirs »
  — volontairement pas un `<textarea>`, qui ne supporte pas le texte en
  couleur), et le texte hors conflit normalement autour pour le
  contexte. Un éventuel marqueur de base commune diff3 (`|||||||`) est
  ignoré, seules les deux versions en conflit sont affichées.
- Strictement en lecture seule : aucune écriture sur le fichier. Le
  chemin demandé n'est accepté que s'il figure dans la liste actuelle
  des fichiers en conflit renvoyée par `git status` (recalculée à
  chaque requête), jamais construit à l'aveugle depuis le paramètre
  d'URL — protège aussi contre un chemin en dehors du dépôt du projet.
  La résolution (choisir/éditer le texte final et l'écrire) fait
  l'objet d'une issue de suivi séparée.
- `git_info.py` : `get_fichiers_en_conflit`, `_extraire_blocs_conflit`,
  `lire_conflits_fichier`.
- `RELECTURE_WEB_DOC.md` mise à jour (nouvelle section 10, ancienne
  section 10 renumérotée 11, mention dans la navigation section 2).

## 2026-09-20 — issue #54 (relecture_web)

- Pour une branche fusionnée sélectionnée dont le worktree est encore
  actif, le bouton « Supprimer » enchaîne désormais `git worktree
  remove` puis `git branch -D` dans le même clic — plus besoin de
  recliquer une seconde fois pour que la branche, alors sans worktree
  détecté, tombe sous le second cas (issue #43). Comportement inchangé
  pour une branche déjà sans worktree (suppression directe de la
  branche).
- Si le retrait du worktree échoue (modifications non commitées), la
  branche n'est pas touchée — même garde-fou qu'avant, juste enchaîné.
  Si le worktree est retiré mais que la suppression de branche échoue
  pour une autre raison, un message flash distinct rapporte cet état
  intermédiaire.
- Message flash rapportant les deux étapes en une seule ligne (même
  principe que la suppression combinée branche + fichiers `Non_Lu/`,
  issues #31/#40). Aperçu de confirmation JavaScript mis à jour pour
  afficher les deux commandes équivalentes.
- `RELECTURE_WEB_DOC.md` mise à jour (tableau des actions, section 9).

## Issue #53 — 2026-09-20

- Doc : `RELECTURE_WEB_DOC.md` section 7 (`branches_cibles.conf`)
  corrigée — le passage affirmait encore que déclarer plusieurs
  branches cibles pour un projet « fait toujours planter la génération
  de la page `/projet/<nom>` », ce que l'issue #50 a corrigé
  (`est_branche_mergee` et `get_diagnostic_doublons_branche` gèrent
  désormais une liste de cibles). Le texte reflète maintenant l'état
  réel : la page s'affiche sans erreur, le badge « fusionnée » est
  correct (vrai si fusionnée dans au moins une cible) ; seul le bouton
  **Merger** reste à corriger, renvoi explicite vers l'issue #51 pour
  ce point précis.

## 2026-09-20 — issue #52 (relecture_web)

- Projet à plusieurs branches cibles configurées (`branches_cibles.conf`,
  ex. `scrabble = master, feature/moteur-strategique`) : le bouton
  Merger ne devine plus aucune cible par défaut — un sélecteur « Cible
  du merge » apparaît dans le panneau d'actions, à choisir explicitement
  avant que la fusion ne soit possible (refus par message flash sinon,
  côté serveur). La confirmation JavaScript affiche la commande
  équivalente correspondant à la cible réellement choisie.
- `est_branche_mergee` accepte désormais une liste de cibles (fusionnée
  si ancêtre d'au moins une d'entre elles), pour que la page
  `/projet/<nom>` ne plante plus pour un projet à plusieurs cibles.
- Comportement inchangé pour un projet à une seule cible configurée (ou
  sans configuration) : pas de sélecteur, bouton Merger identique à
  avant cette issue.
- `RELECTURE_WEB_DOC.md` mise à jour (section 7, tableau des actions
  section 9).

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

## 2026-09-20 — issue #49 (relecture_web)

- Ajout d'un indicateur visuel « Push en cours... Ns » / « Fusion en
  cours... Ns » (fenêtre superposée avec spinner et compteur de secondes)
  affiché juste après la confirmation d'un push ou d'un merge, tant que la
  page ne s'est pas rechargée avec le résultat. Purement côté navigateur,
  aucun changement de comportement serveur.

