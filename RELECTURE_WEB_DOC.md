# RELECTURE_WEB_DOC.md — documentation publique de `relecture_web`

> **Consigne de maintenance.** Ce document doit être relu et mis à jour
> après toute issue qui change le comportement de `relecture_web`
> (nouveau badge, nouvelle action, nouveau cas de diagnostic, changement
> de garde-fou, etc.) — sur le même principe que
> [`BRIDGE_AGENT_DOC.md`](https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/BRIDGE_AGENT_DOC.md)
> pour Bridge_Agent. Un document qui ne suit pas les évolutions de
> l'outil devient trompeur plutôt qu'utile — pire qu'une absence de
> documentation, puisqu'il inspire une fausse confiance.
>
> Ce fichier est public, accessible sans authentification via
> `raw.githubusercontent.com/AlainDelree/Relecture_Bridge/main/RELECTURE_WEB_DOC.md`.
> Vocation : que n'importe quel Claude Chat de projet (pas seulement
> celui de `relecture_bridge`) puisse le récupérer pour comprendre une
> capture d'écran ou un export texte de cet outil qu'Alain lui montre,
> sans reconstruire le contexte à la main.

## 1. Qu'est-ce que `relecture_web` ?

`relecture_web` est un petit programme web Flask, indépendant du reste
de Bridge_Agent (il ne partage pas de code avec `new_issue.py` ni avec
`watcher.py` — toute la lecture git est réimplémentée dans son propre
`git_info.py`). Il vit dans le dossier `relecture_web/` du dépôt
`relecture_bridge`, à côté du mécanisme d'export passif décrit plus bas
(section 8).

Son rôle : donner à Alain une interface pour **relire, diagnostiquer et
agir** sur l'état git réel des projets Bridge_Agent — commits en
attente de push, branches locales, commits orphelins (ni pushés, ni
présents sur une branche locale actuelle) — sans taper de commandes git
à la main.

Le fichier `relecture_web/README.md` résume l'intention d'origine :
« vocation à devenir la maison des futures actions de relecture », pas
un simple visualiseur en lecture seule.

### Lancement et modes réseau (issue #92)

`relecture_web` peut déclencher merge, push, suppression de branches et de
worktrees — contrairement à un simple visualiseur, l'exposer au-delà de la
machine d'Alain sans protection serait risqué. Trois modes de lancement,
mêmes noms que `new_issue.py` (`bridge_agent`) pour la cohérence, mais
implémentation propre à `relecture_bridge` (`relecture_web/auth.py`), sans
code partagé entre les deux dépôts :

```bash
python3 relecture_web/app.py             # par défaut : 127.0.0.1, HTTP, sans mot de passe
python3 relecture_web/app.py --lan       # 0.0.0.0, HTTP, sans mot de passe
python3 relecture_web/app.py --externe   # 0.0.0.0, HTTPS, mot de passe obligatoire
python3 relecture_web/app.py --set-password
```

- **Par défaut (aucun argument)** — `127.0.0.1:5057`, comportement inchangé
  depuis la création de l'outil : aucune authentification exigée, même si un
  mot de passe est configuré (usage strictement local).
- **`--lan`** — `0.0.0.0:5057` en HTTP, toujours sans mot de passe :
  réservé à un réseau local de confiance, jamais à une exposition au-delà.
- **`--externe`** — `0.0.0.0:5057` en HTTPS obligatoire (certificat
  auto-signé, généré une seule fois via `openssl` dans `relecture_web/ssl/`
  s'il n'existe pas déjà, puis réutilisé) et mot de passe obligatoire :
  refuse de démarrer si aucun mot de passe n'est configuré, avec un message
  invitant à lancer `--set-password` d'abord. `--lan` et `--externe` sont
  incompatibles entre eux (erreur explicite si les deux sont passés).
- **`--set-password`** — demande le mot de passe deux fois (confirmation,
  saisie masquée via `getpass`, jamais affiché ni stocké en clair) puis
  enregistre son hash sha256 dans `relecture_web/mot_de_passe.conf`
  (permissions 0600, gitignoré — jamais commité) ; quitte sans lancer le
  serveur.

**Session persistante** : la `SECRET_KEY` Flask est générée une seule fois
puis persistée dans `relecture_web/secret_key.conf` (gitignoré, permissions
0600), relue aux lancements suivants — jamais régénérée aléatoirement à
chaque démarrage, sinon toute session survivante serait invalidée à chaque
redémarrage. Une connexion réussie (mode `--externe`) reste valide 30 jours
(`PERMANENT_SESSION_LIFETIME`) : l'outil n'étant pas un service permanent
(relancé manuellement à chaque merge d'issue), la session doit survivre à
ses redémarrages fréquents sans devenir illimitée pour autant.

Le décorateur `@login_requis` (`app.py`) est appliqué à toutes les routes,
mais ne bloque rien tant que le mode courant n'exige pas de mot de passe
(par défaut et `--lan`) — seul `--externe` l'active réellement. Le mode SSH
vers un futur PC fixe Windows n'est pas couvert par cette issue : elle ne
fait que poser l'authentification, prérequis avant d'envisager un jour une
exposition LAN/externe réelle ; le host d'écoute par défaut ne change pas.

### Source de la liste des projets

`relecture_web` récupère la liste des projets actifs directement depuis
le tableau public de `BRIDGE_AGENT_DOC.md` (`raw.githubusercontent.com`),
pas d'une config locale codée en dur — et non pas une seule fois « au
démarrage » comme une version antérieure de cette section l'affirmait à
tort (issue #109) : en réalité, `fetch_projets()` retélécharge et
reparse ce tableau à **chaque chargement de page**, mémoïsé seulement le
temps d'une requête HTTP (`_charger_projets()`, `app.py` — voir aussi la
barre latérale ci-dessous). Si un projet est ajouté ou retiré de ce
tableau, `relecture_web` le reflète donc dès le prochain chargement de
page — avec un délai possible côté GitHub : `raw.githubusercontent.com`
met en cache le fichier brut environ cinq minutes, une ligne nouvellement
publiée peut donc mettre jusqu'à ce délai avant d'apparaître.

Une colonne **Couleur** optionnelle, en dernière position de ce même
tableau (hexadécimal, ex. `#1a4fb4`), est lue au passage lors de ce même
chargement — aucun appel réseau supplémentaire (issue #73). Lecture
tolérante par la **forme** du dernier champ de chaque ligne
(`normaliser_couleur_hex`, `git_info.py`), pas par nom de colonne ni
position fixe : un tableau à 4 colonnes sans cette colonne (dernier champ
`(conf local)` par ex.) ne matche simplement pas le motif hexadécimal et
retombe sans erreur sur « pas de couleur » pour ce projet — jamais
d'exception, même colonne absente, vide ou invalide. Une couleur valide
sert à distinguer visuellement les projets aux noms proches
(`bridge_agent`/`relecture_bridge`, `alchess`/`chesscoach`...), voir
section 2 pour où elle apparaît. Le texte affiché dessus reste toujours
lisible quelle que soit la couleur : `couleur_texte_lisible` calcule noir
ou blanc selon une formule de luminance perçue classique (YIQ), pour un
fond saturé (jaune, par ex. celui de `bridge_agent`) comme pour un fond
sombre.

## 2. Navigation à trois niveaux

L'interface est organisée en trois niveaux, chacun avec sa page :

1. **Projets** (`/`) — un projet par ligne, avec le nombre de résumés
   en attente de relecture entre parenthèses, et un badge `🌿 N
   worktree(s)` s'il y a des worktrees secondaires actifs. Un projet
   dont le dossier est introuvable ou n'est pas un dépôt git est affiché
   grisé, sans lien cliquable. Les projets locaux sont listés d'abord
   (ordre du tableau), puis les projets distants du PC fixe CCW
   (eux-mêmes dans l'ordre du tableau), séparés par un intitulé « PC fixe
   (Windows) » qui n'apparaît que s'il en existe au moins un (issue #109)
   — voir section 11 pour leur statut particulier et le chargement à la
   demande de leur état complet.
2. **Branches d'un projet** (`/projet/<nom_projet>`) — une branche par
   ligne, avec son dernier commit, son nombre de résumés en attente, et
   des badges d'état (voir section 4). C'est aussi sur cette page
   qu'apparaît, en haut, la section **diagnostic automatique des
   commits orphelins** (section 3) quand il y en a.
3. **Commits d'une branche** (`/projet/<nom_projet>/branche/<nom_branche>`)
   — chaque commit est une carte repliée (hash + message + date/heure
   réelle du commit, issue #48), qui se déplie au clic pour révéler le
   résumé fonctionnel en trois sections (nature du changement / intention
   probable / points d'attention) et le diff complet.

Pages supplémentaires, atteintes depuis des boutons plutôt que depuis la
navigation principale : **Comparer**, **Rapport** (section 5),
**Comparer la sélection** (issue #47, section 5) — cette dernière
uniquement depuis le panneau d'actions du niveau 2, sur une sélection de
branches `recuperation-<hash>` — et **Conflit** (issue #55, section
10), atteinte depuis la section « Fusion en conflit » du niveau 2
quand le dépôt est en état de fusion non résolue.

Une **barre latérale gauche**, présente sur toutes les pages (`base.html`),
liste les noms de tous les projets avec un lien direct vers leur page
`/projet/<nom_projet>` — le projet actuellement affiché y est mis en
évidence. Volontairement minimale (juste les noms, sans compteur ni
badge) : la liste réutilise la même donnée déjà chargée par la route en
cours (mémoïsée le temps d'une requête), pour ne pas répéter l'appel
réseau vers `BRIDGE_AGENT_DOC.md` sur chaque page — le coût déjà corrigé
une fois côté page d'accueil (section suivante, issue #17/#19) ne devait
pas être réintroduit ailleurs (issue #44). Quand un projet a une couleur
configurée (voir section précédente), une petite pastille de cette
couleur apparaît devant son nom dans cette liste (issue #73) — y compris
pour un projet distant, qui garde sa couleur propre. Même regroupement
« locaux puis distants » avec le même séparateur « PC fixe (Windows) »
que la page d'accueil (issue #109).

La même couleur, quand elle est configurée, apparaît aussi en évidence à
deux autres endroits pour ne jamais confondre deux projets aux noms
proches : dans l'en-tête de la page « branches d'un projet » et de la
page Conflit (chip coloré à côté du nom du projet), et dans les fenêtres
de confirmation d'action (bandeau en tête de la fenêtre, voir section 9)
— toujours avec un texte noir ou blanc choisi pour rester lisible sur
cette couleur, jamais codé en dur (issue #73).

**Symbole « crochet pre-push » (issue #129) :** sur la page « branches
d'un projet », un petit symbole apparaît juste devant le chip coloré du
nom du projet quand ce projet est équipé d'un crochet `pre-push` (voir
section 13) — 🪝 avec l'info-bulle « Crochet pre-push actif : les tests se
lancent avant chaque push » pour un crochet présent et exécutable, ⚠️ avec
l'info-bulle « Crochet pre-push présent mais non exécutable : ignoré par
git, aucun test ne se lance » pour un fichier de crochet présent mais sans
le droit d'exécution (`chmod +x` oublié). Réutilise exactement
`git_info.projet_equipe_hook_pre_push` — la même fonction que celle qui
fait basculer le push en arrière-plan côté section 13, jamais une seconde
logique de détection, pour que ce symbole reflète toujours fidèlement ce
que fera un push réel. Rien n'est affiché pour un projet sans crochet, pour
un projet distant du PC fixe CCW, ni si la détection échoue : la page se
charge alors normalement, simplement sans ce symbole. Volontairement
absent de la barre latérale et de la page d'accueil, qui resteraient
minimales (issue #44) : une détection par projet y lancerait une commande
git par projet sur chaque page, contrairement à cette page qui n'en fait
qu'une seule, pour le seul projet affiché.

**Indicateurs de push en arrière-plan (issue #123) :** pour un projet dont
une entrée existe dans `push_arriere_plan.CHEMIN_ETAT_PUSH` et qui est soit
en cours, soit non acquittée (voir section 13), la barre latérale affiche,
à droite de son nom, une petite pastille bleue animée (`.indicateur-push-
en-cours`) pendant que le push tourne — volontairement distincte de la
pastille de couleur du projet (`.pastille-couleur`, statique, toujours
avant le nom) pour ne jamais être confondue avec elle. Une fois le push
terminé et tant que son résultat n'est pas acquitté, cette pastille est
remplacée par un panneau pleine largeur sous le nom : rouge « ⚠ ATTENTION
— REFUS » pour un refus, orange « ⚠ À VÉRIFIER » pour un état interrompu ou
indéterminé — le sens ne repose jamais sur la seule couleur, toujours sur
le texte. L'entrée redevient strictement identique à un projet sans push
suivi dès que `vu` passe à True (bouton « Vu » de la fenêtre de résultat
globale ou de la page du projet) ; un push abouti ne s'y affiche jamais
puisque `vu` y est déjà mis à True automatiquement par le moteur. Donnée
injectée par `app.injecter_barre_laterale`
(`push_arriere_plan.etats_a_signaler`, une seule lecture du fichier d'état
pour tous les projets de la barre), puis tenue à jour en continu par le
sondage JS décrit en section 13 — aucun changement pour un projet dont le
push n'est pas suivi.

## 3. Le diagnostic automatique des commits orphelins (cas A à F)

Un « commit orphelin » est un commit qui a un résumé en attente dans
`Non_Lu/` mais qu'**aucune branche locale actuelle** ne contient — par
exemple parce que la branche qui le portait a été supprimée après
fusion, ou parce qu'il a été créé sur une branche de récupération
(section 6). Un tel commit n'est retenu que par le reflog git (90 jours
par défaut avant `git gc`), donc potentiellement en danger.

Pour chaque commit orphelin, `relecture_web` lance
`git cherry <branche_cible> <hash_commit>` : cette commande compare le
**contenu** (le diff) du commit à tout ce qui existe déjà dans la
branche cible, indépendamment du hash ou du message — un diagnostic par
message ou par hash serait trompeur si le même travail a été réintégré
sous un hash différent (rebase, cherry-pick, réécriture manuelle).

- `+` en préfixe de la sortie de `git cherry` → contenu absent de la
  branche cible → **cas A : nouveau, à merger**.
- `-` en préfixe → contenu déjà présent sous un autre hash → **cas B :
  doublon, nettoyable**.

Ce principe de base est affiné par cinq cas supplémentaires :

| Cas | Signification | Badge affiché |
|---|---|---|
| **A** | Nouveau contenu, absent de la branche cible. | 🆕 nouveau — à merger |
| **B** | Contenu déjà intégré dans la branche cible sous un autre hash (doublon confirmé). | ♻️ doublon — nettoyable, avec un bouton **Comparer** |
| **C** | (Pas un badge séparé) Un commit orphelin qui apparaît comme ancêtre dans la chaîne d'un *autre* commit orphelin plus récent est absorbé dans l'entrée de ce dernier plutôt que listé à part — `git cherry` renvoie déjà toute la chaîne depuis la base commune. La carte du commit le plus récent porte alors un badge « chaîne de N commit(s) », dépliable pour voir chaque maillon avec son propre statut nouveau/doublon. |
| **D** | Le commit ne modifie aucun fichier (commit de backup `--allow-empty`, comme ceux que CCL fait avant chaque modification). Exclu du diagnostic. | commit vide — exclu |
| **E** | Aucune branche cible de comparaison n'est configurée pour ce projet (section 7) — rien à comparer, aucun verdict deviné. | branche cible à configurer |
| **F** | `git cherry` échoue, ou renvoie une sortie inattendue pour ce commit — cas ambigu, aucun verdict automatique. | ⚠ ambigu — à traiter manuellement, avec un bouton **Générer rapport** |
| **M** | Plusieurs branches cibles sont configurées pour ce projet (section 7, liste plutôt que chaîne unique). Deviner automatiquement la plus pertinente pour chaque commit orphelin croiserait chaque commit avec chaque branche candidate (`git cherry`/`merge-base`) — un coût qui a fait échouer par timeout une tentative en ce sens sur un historique volumineux (`scrabble`, issue #46). Aucune commande git supplémentaire n'est lancée : aucun verdict A-F deviné. | plusieurs cibles configurées pour ce projet — vérification manuelle nécessaire via Comparer, avec un bouton **Comparer** |

**Nuance sur le cas A** : `git cherry` compare des diffs, pas des
messages. Un doublon *réimplémenté différemment* (variables renommées,
logique réorganisée) peut donc être classé à tort en cas A « nouveau ».
Comme filet de sécurité indépendant, si le message du commit référence
un numéro d'issue (`#123`) et que ce même numéro apparaît déjà dans un
message de commit de la branche cible, un badge d'avertissement
supplémentaire s'ajoute : « ⚠ peut-être déjà traité sous une autre forme
— issue #123 déjà référencée ». Ce n'est qu'un indice, pas un verdict —
le numéro peut coïncider avec un sujet réellement différent.

**Important pour un Claude Chat externe qui lit ce diagnostic** : ces
cas (A-F) sont un outil de tri, pas une vérité absolue. Le principe de
conception explicite du chantier est que « le diagnostic automatique
aide à prioriser, il ne doit jamais empêcher une vérification humaine
directe » — d'où l'existence des boutons Comparer et Générer rapport
pour les cas B et F.

## 4. Autres badges (hors diagnostic orphelins)

Sur la page « branches d'un projet » :

- **`principale`** — la branche extraite dans le worktree racine du
  dépôt (celle que `git rev-parse --abbrev-ref HEAD` renvoie dans le
  répertoire de travail principal).
- **`worktree`** — une branche a un worktree git actif dessus.
- **`fusionnée`** — la branche est un ancêtre de la branche cible de
  comparaison (`git merge-base --is-ancestor`).
- **`♻️ doublons uniquement — rien à merger`** — tous les commits
  propres de la branche sont déjà intégrés dans la branche cible sous
  d'autres hashes (même logique `git cherry`, appliquée à l'ensemble de
  la branche plutôt qu'à un seul commit). Fusionner cette branche
  n'apporterait rien de neuf.
- **`N commit(s) en attente (push)`** — le worktree de cette branche a
  des commits locaux non poussés vers sa branche amont configurée.
- **`à jour (<amont>)`** — le worktree est synchronisé avec son amont.
- **`🔒 sécurisé (recuperation-<hash>)`** — un commit orphelin a déjà
  une branche de sécurisation (section 6).
- **`⚠️ worktree orphelin — repli signalé`** — le chemin de ce worktree
  secondaire apparaît dans une ligne « déjà pris » du journal
  `logs/watcher-<projet>.log` que bridge_agent écrit (issue #589) quand
  une tâche `mode_write` n'a pas pu obtenir son propre worktree et est
  retombée sur `REP_TRAVAIL` : ce worktree correspond probablement à la
  tentative précédente restée plantée sur le disque, potentiellement
  avec du travail non committé dedans (issue #67). Lecture seule d'un
  fichier hors périmètre `relecture_bridge`, comme le reste de l'état
  git des autres projets (section 1) ; absent ou illisible → badge
  simplement absent, aucune erreur.
- **`⚠ point d'attention`** — sur une carte de commit repliée, le résumé
  fonctionnel généré automatiquement contient du texte non vide dans sa
  section « Points d'attention ».
- **`⚠ CCL travaille ici`** (issue #88, format corrigé par l'issue #89) — un
  fichier de verrou actif de Bridge_Agent (`logs/verrous/*.lock`, avec des
  paires `pid=<pid>` et `rep=<chemin>` par tâche `mode_write` en cours,
  toutes sur une seule ligne séparées par des espaces en pratique côté
  Bridge_Agent ; `mode=` ajouté par l'issue #609 côté Bridge_Agent) désigne,
  par son `rep=`, le worktree de
  cette branche — et le `pid` porté par ce verrou correspond à un
  processus toujours vivant (sinon fichier orphelin d'une tâche terminée
  sans nettoyage, ex. `kill -9`, ignoré). Signale qu'une tâche CCL travaille
  peut-être encore dans ce worktree, en particulier après une reprise
  post-redémarrage (cf. l'incident #73/#609 sur Bridge_Agent) — supprimer
  le worktree pendant qu'elle tourne romprait sa tâche. **Ce n'est qu'un
  signal visuel** : il n'empêche pas de cliquer sur Merger seul (aucune
  garantie que le dossier ne bouge pas pendant la lecture par git, entre
  l'affichage de la page et le clic), mais **le bouton combiné « Merger et
  supprimer » (section 9) refuse d'agir tant qu'il est actif**. Dégrade
  proprement à badge absent (jamais d'erreur affichée) si Bridge_Agent
  n'est pas installé au même endroit ou si son dossier `logs/verrous/`
  est inaccessible — même principe que le badge « worktree orphelin »
  ci-dessus. **Depuis l'issue #118**, la même lecture des verrous (étendue
  aux champs `projet=`/`mode=`, voir `git_info.lire_verrous_actifs`) sert
  aussi, indépendamment de ce badge, à un second garde-fou avant toute
  fusion (« Merger » et « Merger et supprimer », voir section 9) : pas sur
  le worktree de la branche sélectionnée ici, mais sur le dossier où le
  merge va réellement s'exécuter (le worktree dédié de la branche CIBLE
  s'il en a un, sinon le dossier principal du projet).

## 5. Comparer et Générer rapport (pages de vérification)

Deux actions, toujours en lecture seule (aucune commande git de
modification n'est déclenchée), pensées pour les cas où le diagnostic
automatique ne suffit pas :

- **Comparer** (cas B, doublon confirmé — également proposé sur le cas M
  pour une vérification manuelle) — retrouve, dans la branche cible, le
  commit dont l'empreinte de patch (`git patch-id --stable`, qui identifie
  un contenu de diff indépendamment du hash) correspond exactement au
  commit orphelin, puis affiche le `git diff` entre les deux. Un diff vide
  confirme visuellement le doublon. Si aucune empreinte ne correspond
  exactement (contenu légèrement retouché entre-temps malgré le verdict
  « doublon » de `git cherry`), la page l'indique explicitement plutôt que
  d'afficher un mauvais candidat. Si le commit orphelin lui-même est vide
  (backup `--allow-empty`), la page ne tente même pas la recherche par
  empreinte de patch : elle l'indique directement (« commit vide — rien à
  comparer, aucune action requise »), pour ne pas laisser croire à un
  doute sur son contenu (issue #45). Pour un projet à plusieurs cibles
  configurées (cas M, section 7), un seul commit étant en jeu, essayer
  chaque branche candidate tour à tour reste négligeable — contrairement
  au diagnostic automatique, ce bouton essaie donc chaque cible jusqu'à
  trouver une correspondance (issue #46).
- **Générer rapport** (cas F, ambigu, mais disponible sur tout commit)
  — assemble un texte prêt à copier-coller dans une conversation Claude
  Chat dédiée au projet : hash, message, résumé fonctionnel déjà
  généré, sortie brute de `git cherry`, branches locales et distantes
  contenant le commit, et liste des autres commits orphelins en
  attente pour ce projet. C'est exactement ce texte qu'un Claude Chat
  externe peut recevoir pour investiguer un commit que l'outil n'a pas
  pu trancher automatiquement.
- **Comparer la sélection** (issue #47) — vérifie en une seule action
  plusieurs branches `recuperation-<hash>` cochées (niveau « branches
  d'un projet »), plutôt que de faire confiance au seul badge de
  diagnostic ou de cliquer Comparer une par une : relance
  `comparer_commit_doublon` pour chacune (réutilisation directe, aucune
  nouvelle logique de comparaison) et affiche un résultat groupé, une
  ligne par branche — diff vide (♻️ doublon confirmé), diff non vide
  (⚠ à vérifier manuellement, avec un lien vers la page Comparer
  individuelle pour le détail), ou commit vide (ℹ️ rien à comparer,
  issue #45). Une branche sélectionnée qui ne suit pas la convention
  `recuperation-<hash>` est ignorée avec un message flash, même
  garde-fou que pour la suppression groupée (section 6). Route en
  lecture seule malgré la méthode POST (nécessaire pour transmettre la
  sélection) : aucune commande git de modification n'est déclenchée.
  Seules les branches confirmées diff vide dans le résultat se voient
  proposer un bouton de suppression groupée, qui réutilise directement
  l'action « Supprimer la/les branche(s) de récupération » existante
  (section 6, issue #29/#31/#40) — les autres restent à traiter
  manuellement via le lien de détail, jamais incluses dans cette
  suppression groupée.

## 6. La convention `recuperation-<hash>`

**Ce n'est pas un mécanisme de Bridge_Agent** — c'est une convention
propre à `relecture_web`, pour sécuriser un commit orphelin menacé par
le nettoyage du reflog (90 jours, purgeable ensuite par `git gc`).

L'action « Sécuriser » (bouton individuel sur chaque commit orphelin,
ou « 🔒 Sécuriser tous les commits orphelins » pour tout traiter en un
geste) crée une branche nommée `recuperation-<hash_commit>` pointant
exactement sur ce commit — via `git branch recuperation-<hash> <hash>`.

Points clés :

- **Geste défensif pur** : ne fusionne, ne modifie et ne pousse jamais
  rien. La seule conséquence est qu'un commit qui ne serait plus retenu
  que par le reflog devient retenu par une branche normale, donc
  permanent jusqu'à suppression explicite.
- **Idempotent** : si la branche existe déjà pour ce hash, l'action ne
  la recrée pas et l'affiche comme déjà sécurisée.
- **S'applique à n'importe quel commit orphelin**, tranché ou non par
  le diagnostic A-F — la sécurisation ne dépend d'aucun verdict.
- **Suppression dédiée** : une branche `recuperation-<hash>` n'a jamais
  de worktree associé (elle n'a jamais été extraite), donc l'action
  générique de suppression de worktree ne s'applique pas. Une action
  séparée « Supprimer la/les branche(s) de récupération » fait
  `git branch -D <nom>` — refusée par construction pour tout nom qui ne
  suit pas exactement le motif `recuperation-<hash>` (protection
  indépendante du badge affiché, pour qu'une branche de travail
  ordinaire comme `main` ou `dev` ne puisse jamais passer par cette
  action même en cas d'erreur de diagnostic). Cette suppression efface
  aussi les fichiers `Non_Lu/` associés à ce hash, sans quoi le commit
  redeviendrait immédiatement orphelin non sécurisé.
- **Chaîne complète nettoyée, pas seulement le hash nommé** (issue #40) :
  si le commit visé par la branche a lui-même des ancêtres non fusionnés,
  la branche protège toute cette chaîne (comportement normal de git — un
  pointeur de branche protège tout ce qui est en dessous), le même
  regroupement que le cas C du diagnostic (section 3). Avant de supprimer
  la branche, `relecture_web` réutilise `get_chaine_cherry` pour lister ces
  ancêtres et efface le fichier `Non_Lu/` de chacun — sans quoi un ancêtre
  protégé uniquement par cette branche redeviendrait orphelin et non
  protégé après coup.
- Pour les branches `recuperation-<hash>` spécifiquement, le badge
  « doublons uniquement » (section 4) réutilise directement le
  diagnostic du commit visé plutôt que d'agréger `git cherry` sur toute
  la chaîne de la branche — une branche de récupération peut avoir été
  créée sur un point ancien de l'historique, ce qui ferait remonter de
  vieux commits sans rapport et fausserait un agrégat global.

## 7. `branches_cibles.conf`

Fichier `relecture_web/branches_cibles.conf`, au format `nom_projet =
branche` (une ligne par projet, `#` pour les commentaires). Il fixe,
projet par projet, la **branche cible de comparaison** utilisée par
tous les diagnostics `git cherry`/fusion/badges de cette page —
c'est-à-dire la référence contre laquelle on juge « déjà intégré » ou
non.

- `nom_projet` est le champ « nom » du tableau de `BRIDGE_AGENT_DOC.md`
  (ex. `ff_galerie`), pas le nom du dossier local ni celui du dépôt
  GitHub.
- Un projet **absent** de ce fichier n'a pas de surcharge : sa branche
  principale git (celle du worktree racine) reste la référence par
  défaut.
- Utile quand un projet travaille sur une branche de développement
  (ex. `dev`) avant de merger vers sa branche principale (`main`) :
  comparer directement contre `main` donnerait un écart de commits
  trompeur (tout ce qui est sur `dev` en attente de merge apparaîtrait
  comme « orphelin » ou « non intégré » à tort).
- **`branche` accepte plusieurs branches séparées par une virgule**
  (ex. `master, feature/moteur-strategique`, issue #41), pour les
  projets à lignes de développement parallèles et indépendantes — qui
  ne se succèdent pas comme `dev`/`main`, mais coexistent sans qu'un
  travail sur l'une doive passer par l'autre. Dans ce cas,
  `charger_branches_cibles()`/`get_branche_cible_comparaison()`
  retournent une **liste** de branches plutôt qu'une chaîne unique
  (repli inchangé — chaîne unique — pour les projets à une seule
  cible ou sans configuration).

  Le diagnostic des commits orphelins (cas M ci-dessus, issue #46) et le
  bouton Comparer (essaie chaque branche candidate tour à tour, issue #46)
  savent gérer une liste sans deviner ni planter. `get_branches_locales`
  et `est_branche_mergee` (badge « fusionnée ») savent aussi gérer une
  liste sans planter (issue #50) : une branche est considérée fusionnée
  si elle est ancêtre d'au moins une des cibles candidates. **Le bouton
  Merger, en revanche, ne devine jamais de cible parmi plusieurs
  candidates** (issue #52) : un merge modifie réellement le dépôt, à la
  différence d'un diagnostic — deviner la mauvaise cible serait plus
  grave qu'un badge imprécis. Quand plusieurs cibles sont configurées,
  le panneau d'actions affiche donc un sélecteur (« Cible du merge »)
  listant les cibles candidates ; Alain doit en choisir une explicitement
  avant que le bouton Merger ne devienne utilisable pour de vrai — la
  commande équivalente affichée en confirmation reflète la cible
  choisie. Sans ce choix (ou avec une cible hors de la liste configurée,
  ex. requête forgée), `merger_branches_route` refuse l'action par
  message flash plutôt que de deviner. Pour un projet à une seule cible
  configurée, rien ne change : pas de sélecteur, comportement identique
  à avant l'issue #52.

- **Ce fichier suit le même statut que les `configs/*.conf` de
  Bridge_Agent** : CCL ne le modifie jamais de sa propre initiative,
  même sur demande explicite d'une issue — seul Alain l'édite à la
  main.

## 8. Le mécanisme d'export passif (contexte, pas une action de `relecture_web`)

`relecture_web` lit les résumés déjà produits par un mécanisme
indépendant : un hook git `post-commit` (installé sur chaque projet
Bridge_Agent) qui, à chaque commit, exporte dans
`<projet>/Non_Lu/<hash>_<message>.diff` le diff complet du commit, et
tente de générer un résumé fonctionnel en trois sections (nature du
changement / intention probable / points d'attention) dans un fichier
`_resume.md` associé, via le CLI Claude Code. `relecture_web` regroupe
ces fichiers par hash et par branche pour l'affichage des cartes de
commit (section 2, niveau 3) — mais ne les génère pas lui-même.

Une fois un commit lu et validé par Alain, ses fichiers `.diff`/
`_resume.md` sont déplacés vers `<projet>/Traités/` (commande `traite`,
distincte de `relecture_web`) — ce qui les retire de la liste des
résumés en attente.

## 9. Actions disponibles et leurs garde-fous

Depuis l'issue #71, la confirmation avant soumission est graduée selon le
risque réel de l'action plutôt qu'uniforme — une confirmation identique
pour un geste anodin et un geste difficile à défaire apprend à ne plus la
lire (fatigue de confirmation), au point que le garde-fou ne protège plus
personne. Trois niveaux, indiqués dans la colonne Garde-fou de chaque
action ci-dessous :

- **Aucune confirmation** — action locale, sans danger ou facilement
  réversible : application directe au clic.
- **Confirmation légère** — fenêtre propre à `relecture_web`
  (`#modal-confirmation`, `base.html`), variante visuelle neutre (pas de
  couleur d'alerte). Depuis l'issue #73, ce n'est plus le `confirm()`
  natif du navigateur : le passage par la fenêtre maison permet de
  raccourcir et colorer les confirmations de façon uniforme (voir
  ci-dessous).
- **Confirmation forte** — même fenêtre `#modal-confirmation`, variante
  visuelle distincte (couleur d'alerte rouge, classe
  `modal-confirmation--forte`), réservée aux actions difficiles à
  défaire. Le bouton de validation décrit l'action réelle avec sa portée
  (ex. « Pousser 2 branches vers GitHub », « Supprimer test_conflit_a »)
  au lieu d'un OK générique.

Dans les deux variantes de fenêtre (issue #73, `ouvrirConfirmation`,
`base.html`) : une seule ligne principale au format « Action + objet +
projet » (ex. « Merger worktree-issue-72 dans main — relecture_bridge »)
plutôt qu'un long texte explicatif ; un avertissement éventuel (ex.
bloc(s) au résultat vide pour « Traiter tous les blocs ») affiché en
premier et mis en évidence, jamais noyé en fin de message ; la commande
git équivalente en petit texte discret sous la ligne principale ; un
bandeau à la couleur du projet en tête de fenêtre quand elle est
configurée (section 2, issue #73) ; et dans tous les cas le focus par
défaut sur Annuler, pour qu'un Entrée réflexe ne valide rien.

**Grisage pendant l'envoi réel (issue #120) :** dès le clic de validation
dans la fenêtre — jamais à son ouverture — `ouvrirConfirmation` grise son
propre bouton de validation (non cliquable, libellé remplacé par « <action>
en cours... »), bloque aussi son bouton Annuler, et bloque en plus, si
`options.boutonDeclencheur` est fourni, le bouton « Confirmer » de la page
derrière qui a ouvert cette fenêtre — pour qu'aucun second envoi ne parte
pendant que le premier tourne (un clic resté sans retour visible pendant
une suppression ou une fusion encourageait sinon à recliquer). La fenêtre
reste affichée tant que la vraie navigation déclenchée par le formulaire
n'a pas eu lieu, elle ne se ferme jamais ici — donc là où un indicateur
« ... en cours... Ns » existe déjà (Push, Merger, issue #49 ci-dessous), il
reste affiché tel quel, par-dessus la fenêtre grisée (`.overlay-action`
passé à un z-index supérieur à `.modal-confirmation` pour cette raison) :
ce grisage s'y ajoute, il ne le remplace pas. Un `pageshow` global
réinitialise ces trois boutons (validation et Annuler de la fenêtre,
déclencheur de la page) si une restauration par le bouton « précédent » du
navigateur (bfcache) les avait figés désactivés juste avant la navigation ;
un rechargement de page (nouvel appel à `ouvrirConfirmation`) les
réinitialise de la même façon. Branché pour toutes les actions qui
utilisent cette fenêtre, y compris les trois pages de confirmation forte
dédiées plus bas (fichiers ignorés avant suppression de worktree, forçage
de suppression, avertissement de verrou avant fusion) — chacune relie son
propre bouton de page à `options.boutonDeclencheur`.

Dans tous les cas (y compris l'absence de toute confirmation), jamais
d'exécution silencieuse : la commande git équivalente qui sera exécutée
est toujours affichée avant soumission (dans la fenêtre de confirmation
quand il y en a une, ou visible sur la page elle-même sinon).

| Action | Portée | Commande équivalente | Garde-fou |
|---|---|---|---|
| **Revert** | Un commit précis, sur la page d'une branche. | `git revert --no-edit <hash>` | **Aucune confirmation** (issue #71). Crée un nouveau commit d'annulation, ne réécrit pas l'historique — réversible (revert du revert, ou reset tant qu'il n'est pas poussé). |
| **Push** | Une ou plusieurs branches sélectionnées (cases à cocher, niveau « branches d'un projet »). | `git push <remote> <branche>` (une seule commande pour toutes les branches cochées si le projet est équipé d'un crochet pre-push, voir section 13) | **Confirmation forte** (issue #71) — le push quitte la machine. Cible toujours une branche entière jusqu'à son dernier commit, jamais une sélection de commits épars. **Projet NON équipé d'un crochet `pre-push` (comportement inchangé) :** timeout de 120s (dépôt volumineux, connexion lente) ; en cas de dépassement, l'état réel est revérifié automatiquement (`git ls-remote` comparé au commit local) plutôt que de renvoyer Alain vers une vérification manuelle — le message flash final indique explicitement si le push a bien abouti, a échoué, ou si l'état n'a pu être déterminé (issue #66 ; issue #39). Après la confirmation, une fenêtre superposée « Push en cours... Ns » (compteur de secondes) reste affichée jusqu'au rechargement de la page avec le résultat — purement visuel côté navigateur, aucun changement serveur (issue #49). **Projet équipé d'un crochet `pre-push` exécutable (issue #122, section 13) :** le push part en arrière-plan dans un thread du serveur dès la confirmation — la requête revient tout de suite, sans fenêtre « ... en cours... Ns » bloquante (elle n'a plus de sens, la page ne reste jamais en attente) ; le résultat réel se suit dans le panneau « Dernier push » de la page projet. Jamais pour un projet distant du PC fixe (`_ccw`, section 11) : toujours le comportement synchrone ci-dessus. Pour équiper un projet de ce crochet, voir le guide pratique en fin de section 13. **Nettoyage automatique après un push confirmé abouti (issue #128)**, pour ce seul projet : réutilise exactement `nettoyer_resumes_pousses`, donc le même garde-fou que « Nettoyer ce projet » ci-dessous (commit déjà ancêtre d'une branche distante) — voir la ligne « Nettoyer ce projet » pour le détail des deux chemins (synchrone/arrière-plan) et des cas exclus (refus, interruption, indétermination, projet distant). |
| **Merger** | Une ou plusieurs branches sélectionnées. | `git merge <branche>` (avec bascule temporaire si la branche cible n'a pas de worktree dédié) | **Confirmation légère** (issue #71 ; fenêtre maison depuis l'issue #73, plus `confirm()` natif) — modifie la branche cible mais reste local et annulable tant que le merge n'est pas finalisé (section 10). Refusé si la branche est déjà la branche cible, ou si le diagnostic « doublons uniquement » (section 4) indique qu'elle n'apporterait aucun contenu nouveau. **Garde-fou avant tout merge (issue #74) : refusé par message flash explicite si le dossier de la branche cible contient des modifications non committées (fichiers suivis modifiés, ou fichiers non suivis non ignorés — `git status --porcelain`)** — un tel état peut signaler qu'une tâche CCL y travaille encore, repliée sur ce même dossier faute de worktree dédié disponible (voir issue #73, où l'intégration automatique du CHANGELOG avait alors committé ce travail en cours par-dessus) ; aucune tentative de fusion n'est même lancée dans ce cas. **Depuis l'issue #117**, le message nomme explicitement les fichiers concernés avec leur statut (`chemin (modifié|non suivi|supprimé|renommé|copié|ajouté|conflit)` — `git_info.get_modifications_non_committees_detaillees`/`decrire_modifications_non_committees`), plafonné à une dizaine d'entrées puis « … et N autres », en rappelant qu'il s'agit du dossier principal du projet et que ces fichiers peuvent être non suivis par git — avant cette issue, le message ne donnait qu'un décompte (« N fichier(s) concerné(s) »), et avait été confondu à tort avec le panneau .gitignore affiché juste en dessous à l'époque (voir la ligne « Panneau .gitignore » plus bas pour le détail de ce malentendu et son autre correction, le déplacement du panneau). Un conflit (une fois le merge lancé) laisse volontairement le dépôt en état de fusion non résolue (pas de rollback automatique), pour ne pas perdre l'information. Même timeout étendu (120s) que Push (issue #39) ; en cas de dépassement, l'état réel est revérifié automatiquement (branche source devenue ancêtre de la cible ? fusion arrêtée sur des conflits ? ni l'un ni l'autre ?) et le message flash final le reflète explicitement, plutôt qu'un renvoi systématique vers une vérification manuelle (issue #66). Projet à plusieurs cibles configurées (section 7, issue #52) : un sélecteur « Cible du merge » apparaît dans le panneau d'actions — aucune cible n'est devinée, refus par message flash si aucune n'est choisie explicitement. Même indicateur « Fusion en cours... Ns » que Push après confirmation (issue #49). Si le merge introduit un ou plusieurs `CHANGELOG-<N>.md` à la racine du dépôt, une intégration automatique dans `CHANGELOG.md` est tentée juste après (issue #51) ; succès ou échec est rapporté par message flash **et** journalisé dans `relecture_web/changelog_fusion.log` (date/heure, projet, commande, résultat, erreur éventuelle) — consultable après coup même si le flash est passé inaperçu (issue #62). **Le script utilisé est toujours celui de relecture_bridge (`scripts/fusionner_changelog.py`, ce dépôt), jamais une copie du projet fusionné (issue #87)** — résolu à partir de l'emplacement de `relecture_web/git_info.py` lui-même, puis lancé avec `--repo <dépôt fusionné>` ; auparavant, seuls quelques projets équipés d'une copie locale du script bénéficiaient de cette intégration, les autres échouaient avec « script introuvable ». Ce script reste robuste à un `CHANGELOG.md` cible qui ne suit pas la convention « Convention d'ajout : ... » de relecture_bridge (issue #252) : en-tête absent -> insertion après le premier titre de niveau 1 trouvé, ou en tête de fichier si aucun titre ; `CHANGELOG.md` absent -> créé avec pour seul contenu les entrées fusionnées ; contenu existant jamais perdu, quelle que soit la forme du fichier cible. Si un `CHANGELOG-<N>.md` commence par sa ligne de titre d'échange (« # CHANGELOG-N — à fusionner dans CHANGELOG.md », tiret cadratin ou simple), cette ligne et les lignes vides qui la suivent directement sont retirées avant insertion — elle ne décrit que le fichier temporaire, pas l'entrée de changelog (issue #104) ; absente, rien n'est retiré. **Portée strictement limitée à `CHANGELOG.md` et aux `CHANGELOG-<N>.md` consommés (issue #74)** : le commit d'intégration (`git add -- CHANGELOG.md CHANGELOG-<N>.md... && git commit -- <mêmes chemins>`) ne touche jamais que ces fichiers précis — jamais un `git commit -a`/`git add -A`, qui aurait embarqué toute autre modification présente dans l'arbre (cause du commit 0c477c0 pendant l'issue #73, qui avait ainsi committé le travail inachevé d'une tâche CCL repliée sur ce même dossier). |
| **Merger et supprimer** (issue #88) | Une ou plusieurs branches sélectionnées, en un seul clic. | `git merge <branche>` (avec bascule temporaire comme pour Merger seul) **puis**, seulement si le merge réussit, la même commande que « Supprimer la/les branche(s) fusionnée(s) » ci-dessous. | **Confirmation légère unique pour l'ensemble** décrivant les deux étapes qui vont s'enchaîner. Même garde-fou « modifications non committées » que Merger seul (ligne ci-dessus, issue #74, message nommant les fichiers concernés depuis l'issue #117). Mêmes deux conditions d'éligibilité que Merger seul (branche pas la cible, pas « doublons uniquement ») — **PLUS** refus explicite par message flash si le badge « ⚠ CCL travaille ici » (section 4) est actif pour cette branche, contrairement à Merger seul qui reste autorisé même avec ce badge affiché (l'utilisateur peut savoir ce qu'il fait délibérément). Si le merge échoue (conflit, timeout non confirmé abouti, erreur) : comportement identique à Merger seul, **aucune suppression n'est tentée**. Si le merge réussit mais que la suppression échoue ensuite (modifications non commitées détectées entre-temps par git, cas rare mais réel) : les deux résultats sont rapportés séparément dans le message flash — le merge a eu lieu, la suppression non, avec la raison. Les boutons Merger et Supprimer existants restent inchangés à côté de celui-ci pour un enchaînement en deux clics séparés si préféré. |
| **Avertissement verrou Bridge_Agent avant fusion** (issue #118) | « Merger » et « Merger et supprimer » (lignes ci-dessus), déclenché avant toute tentative de fusion — y compris l'intégration automatique du CHANGELOG qui la suit, puisqu'elle fait partie du même geste. | Aucune commande destructrice : relit `logs/verrous/*.lock` (même source et même tolérance de format que le badge « ⚠ CCL travaille ici », section 4, étendue aux champs `projet=`/`mode=` — `git_info.lire_verrous_actifs`/`verrous_sur_dossier`), en lecture seule — jamais de verrou créé, modifié ou supprimé depuis `relecture_web`. | **Confirmation forte, page dédiée** (`confirmation_verrou_fusion.html`), déclenchée si au moins un verrou Bridge_Agent actif (pid vivant — signal 0 ou présence dans `/proc` ; un pid vivant appartenant à un autre utilisateur compte comme vivant) correspond, par son `rep=` résolu en chemin réel, au dossier où CE merge va réellement s'exécuter : le worktree dédié de la branche cible choisie s'il en a un, sinon le dossier principal du projet (jamais les worktrees des AUTRES branches du même projet — une issue qui y travaille ne gêne en rien ce merge précis, cas normal qui ne doit déclencher aucun avertissement). Motivé par un angle mort du garde-fou « modifications non committées » (#74/#117, ligne Merger ci-dessus) : un dossier peut être parfaitement propre au moment du clic si l'issue qui y travaille est encore en lecture, ou n'a pas encore écrit — un merge (surtout avec conflits) ou un `git pull` survenant pendant qu'elle tourne serait alors vu par son propre contrôle d'écriture comme une modification extérieure et restauré, avec échec définitif de cette issue (cas réel visé : un audit à périmètre dynamique dont le `REPO_CIBLE` est justement le dépôt où l'on fusionne). La page nomme, pour chaque verrou concerné, le projet et le mode (lecture/écriture) de l'issue — les deux modes sont concernés, pas seulement l'écriture. Deux actions : **Annuler** (lien simple vers la page du projet, focus par défaut, rien n'est soumis, même pattern que `echec_suppression_worktree.html`) ou **« Fusionner quand même »**, qui réémet la requête d'origine (toutes sélections comprises) avec un champ caché `forcer_malgre_verrou=on` — la fenêtre de confirmation forte habituelle (`#modal-confirmation`, bandeau rouge, focus par défaut sur Annuler) s'intercale encore avant l'envoi réel. **Jamais mémorisé d'une requête à l'autre ni d'un rechargement à l'autre** (même leçon que la case « Purger », issue #102) : ce champ caché n'existe que dans le formulaire de cette page précise, jamais une case cochée qui survivrait. **Revérifié côté serveur à l'exécution**, pas seulement à l'affichage de la page projet : le test relit l'état réel des verrous à chaque requête (une issue peut démarrer entre l'ouverture de la page et le clic), et n'accepte le contournement que si `forcer_malgre_verrou=on` est explicitement présent dans CETTE requête. S'ajoute au refus « modifications non committées » (#74/#117) et au refus du badge « ⚠ CCL travaille ici » de « Merger et supprimer » (ligne ci-dessus) sans les remplacer — placé avant eux dans `merger_et_supprimer_route` (inutile de montrer l'avertissement « fichiers ignorés » si la fusion elle-même ne peut pas même être lancée), donc jamais les deux messages empilés pour une même branche dans une même requête. Dégradation silencieuse, même principe que le badge existant : dossier `logs/verrous/` absent/illisible, fichier malformé, ou Bridge_Agent installé ailleurs → aucun avertissement, aucune erreur affichée. Les projets distants du PC fixe (lignes `_ccw`, section 11) ne sont pas couverts par ce contrôle : aucun accès SSH ajouté. |
| **Supprimer la/les branche(s) fusionnée(s)** | Une ou plusieurs branches sélectionnées confirmées fusionnées. | `git worktree remove <chemin>` **puis** `git branch -D <nom>` dans le même clic si la branche a encore un worktree actif (issue #54 — plus besoin de recliquer une seconde fois) ; sinon `git branch -D <nom>` directement (issue #43 — cas d'un worktree déjà retiré manuellement, ne laissant que la branche). | **Confirmation forte** (issue #71). Refusé si c'est la branche principale, ou si elle n'est pas confirmée fusionnée dans la branche cible. Le `worktree remove` n'est jamais `--force` : git refuse de lui-même s'il reste des modifications non commitées ; si cette étape échoue, la branche n'est pas touchée. Le `branch -D` (sans worktree) n'a pas cette protection, d'où l'exigence stricte de `mergee` en amont. Même bouton dans tous les cas — seule la commande affichée en confirmation diffère, et le message flash rapporte les deux étapes quand les deux ont eu lieu. |
| **Rejeter (sans fusionner)** (issue #95) | Une ou plusieurs branches sélectionnées confirmées **NON** fusionnées. | Même commande que « Supprimer la/les branche(s) fusionnée(s) » ci-dessus (`git worktree remove <chemin>` **puis** `git branch -D <nom>`, ou `git branch -D <nom>` seule si le worktree a déjà été retiré) — mais **jamais aucune tentative de merge au préalable**. | **Confirmation forte**, garde-fou strictement inverse de « Supprimer la/les branche(s) fusionnée(s) » : refusé si c'est la branche principale, **ou si la branche est confirmée fusionnée** (message flash renvoyant vers l'action « Supprimer » dans ce cas). Pour le cas réel qui a motivé ce bouton (chesscoach, worktree-issue-88) : CCL peut lui-même signaler que son travail fait doublon avec une autre issue déjà traitée et que fusionner créerait des conflits inutiles — jusque-là, la seule façon de supprimer proprement un tel worktree sans jamais le fusionner était une commande manuelle en terminal. Fenêtre de confirmation à bandeau rouge, bouton nommé explicitement (ex. « Rejeter worktree-issue-88 », jamais un OK générique), focus par défaut sur Annuler (même mécanique que toute confirmation forte, section 9 ci-dessus) — avec en plus un avertissement mettant en avant, pour chaque branche concernée, le nombre de commits non encore fusionnés (`git log <branche principale>..<branche>`), pour qu'Alain voie l'ampleur du travail perdu avant de confirmer une suppression réelle et définitive d'un travail jamais intégré. Pas de fermeture d'issue GitHub ici (retirée en #97, après avoir existé en #95) : en usage normal, l'issue correspondante est déjà fermée par le watcher CCL dès la fin de son traitement (label `done`), bien avant qu'un rejet n'intervienne — la case ne servait quasiment jamais et ajoutait de la confusion pour ce cas marginal. **Option « Purger réellement » (issue #96, case à cocher distincte, décochée par défaut) :** `branch -D` seul ne fait que détacher la branche, le commit reste récupérable via le reflog (90 jours par défaut) et continue d'apparaître comme commit orphelin « ambigu » dans le diagnostic (constat fait en testant le geste manuel équivalent sur chesscoach, worktree-issue-88). Cochée, elle déclenche après coup, une seule fois pour l'ensemble des branches rejetées avec succès, `git reflog expire --expire=now --all` puis `git gc --prune=now` (`purger_reflog_et_gc`) — ces deux commandes sont **globales au dépôt**, aucune option git ne permet de n'expirer que le reflog d'une branche déjà supprimée ; tout autre commit orphelin non sécurisé présent dans le dépôt est donc détruit en même temps, sauf s'il reste atteignable depuis une branche `recuperation-<hash>` (voir « Sécuriser » ci-dessous, qui reste le geste à recommander pour un commit orphelin qu'on veut garder). L'avertissement de confirmation liste nommément ces autres commits menacés avant l'envoi du formulaire, pour qu'Alain sache ce qu'il perd en plus du commit qu'il rejette. Après une purge réussie, les fichiers `Non_Lu/<hash>_*` des commits confirmés disparus (`git cat-file -e`, jamais supposé) sont aussi nettoyés — vise aussi bien les commits ciblés que les orphelins collatéraux purgés, pour éviter le résidu « ambigu » constaté sinon dans le diagnostic (un résumé `Non_Lu/` dont le commit n'existe plus n'est pas revalidé ailleurs dans le diagnostic général, limite connue laissée telle quelle hors périmètre de l'issue #96). **Panneau repliable (issue #97) :** cette case et son avertissement nominatif sont repliés par défaut dans un panneau « Options de rejet » (`<details>`/`<summary>`, à côté du bouton Rejeter), pour ne pas alourdir visuellement l'usage courant qui n'a besoin de Rejeter qu'occasionnellement — les boutons habituels du panneau d'actions restent, eux, affichés en permanence. Le panneau s'ouvre automatiquement (et refuse de se refermer) tant que la case « Purger » est cochée à l'intérieur, pour ne jamais la cocher puis la perdre de vue en repliant par erreur ; la fenêtre de confirmation forte au clic sur Rejeter reflète toujours l'état réel de la case, que le panneau soit ouvert ou replié au moment du clic. **Décochage systématique et message raccourci (issue #102) :** la case « Purger » ne survit jamais à un changement de sélection de branches (décochée dès qu'une case de branche change d'état) ni à un chargement de page (décochée au chargement initial et sur tout retour via le bfcache du navigateur, en plus d'un `autocomplete="off"` empêchant une restauration de formulaire) — une option irréversible et globale au dépôt ne doit jamais rester cochée d'une branche à l'autre. Le libellé de la case est raccourci sur une seule ligne (« Purger définitivement le commit rejeté (irréversible, concerne tout le dépôt) »), sans commande git visible en permanence ; le paragraphe rouge dense qui expliquait tout en détail est remplacé par un message d'une ligne, vert (« ✅ Aucun autre commit menacé. ») s'il n'y a aucun autre commit orphelin non sécurisé menacé, rouge avec la liste nominative des hashes/sujets sinon — l'explication complète (ce que font `git reflog expire` et `git gc --prune=now`, ce qui reste récupérable sans la case) est reléguée dans un bloc repliable « Pourquoi ? » à l'intérieur du panneau. La fenêtre de confirmation forte au clic sur Rejeter rappelle aussi, en première ligne de son avertissement (visible même si le panneau était replié), « 🔴 PURGE DÉFINITIVE activée » suivi du nom des branches visées, quand la case est cochée. |
| **Forcer la suppression** (issue #103) | Un seul worktree, celui dont la tentative de « Rejeter », « Supprimer la/les branche(s) fusionnée(s) » ou « Merger et supprimer » vient d'échouer. | `git worktree remove --force <chemin>` **puis** `git branch -D <nom>`. | **Confirmation forte**, affichée sur une page dédiée (`echec_suppression_worktree.html`) plutôt que dans la fenêtre de confirmation habituelle — accessible seulement après ce premier échec, jamais un bouton permanent, jamais une case à cocher qui survivrait à un rechargement (leçon de la case « Purger », issue #102). **Détection indépendante de la langue de git** : l'échec initial de `git worktree remove` n'est jamais interprété via son message d'erreur (traduit selon la locale de git) — `diagnostiquer_echec_suppression_worktree` revérifie l'état réel du dossier via `git status --porcelain` exécuté DANS le worktree lui-même (jamais le répertoire du projet). Une sortie non vide confirme le cas « fichiers modifiés ou non suivis » (ceux ignorés par `.gitignore` n'y figurent jamais, comme pour git lui-même) et déclenche l'affichage de cette page ; une sortie vide (verrou, chemin déjà supprimé à la main, autre cause) laisse le message d'erreur brut de git s'afficher comme avant, sans aucun bouton de forçage. Pour le worktree concerné, la page affiche : la liste des fichiers avec leur statut (modifié / non suivi), plafonnée à 20 entrées puis « … et N autres » ; pour les fichiers suivis modifiés, `+ajouts −suppressions` par fichier (`git diff HEAD --numstat`) ; un bouton « Copier le diff » (`.bouton-copier`) copiant le diff complet (`git diff HEAD`) des seuls fichiers suivis modifiés, plafonné à 2000 lignes (signalé si tronqué) — pour transmettre le contenu à un Claude Chat avant de trancher. Garde-fous identiques à l'action d'origine : pour « Rejeter », branche toujours **NON** confirmée fusionnée (`rejeter_worktree_force_route`) ; pour « Supprimer » et « Merger et supprimer », branche toujours confirmée fusionnée (`supprimer_worktree_force_route`, partagée par les deux — au moment de cet échec, le merge de « Merger et supprimer » a déjà eu lieu, la branche est donc par construction fusionnée) — **PLUS** un refus propre à cette variante forcée : si le badge « ⚠ CCL travaille ici » (section 4) est actif sur ce worktree, le bouton disparaît et un message explicite s'affiche à sa place (jamais de bouton simplement désactivé en silence) — forcer la suppression sous les pieds d'une tâche en cours la romprait. Si le worktree est en plus verrouillé (`git worktree lock`, qui exige alors deux `--force` consécutifs pour le retirer) ou si la suppression forcée échoue malgré tout, l'erreur brute de git est affichée telle quelle, sans nouvelle tentative automatique. L'option « Purger réellement » de « Rejeter » (ligne ci-dessus, issue #96) reste disponible ici, reportée depuis le formulaire d'origine (champ caché) et appliquée à cette seule branche une fois le forçage confirmé. **Depuis l'issue #112**, cette page affiche aussi, dans une section distincte quand il y en a, les fichiers/dossiers ignorés par `.gitignore` du worktree (voir la ligne « Avertissement fichiers ignorés avant suppression de worktree » ci-dessous) — pour que la confirmation forte porte sur l'ensemble de ce qui sera réellement perdu, pas seulement les fichiers modifiés/non suivis. **Depuis l'issue #113**, pour chaque worktree concerné un bouton **Annuler** (lien simple vers la page du projet, rien n'est soumis) est affiché juste avant « Forcer la suppression », focus par défaut sur le premier de la page — avec un seul bouton visible par worktree, l'impression était de n'avoir que le choix de supprimer. |
| **Avertissement fichiers ignorés avant suppression de worktree** (issue #112) | Chaque worktree sélectionné par « Supprimer la/les branche(s) fusionnée(s) », « Merger et supprimer » ou « Rejeter (sans fusionner) », AVANT toute tentative de suppression (et avant toute fusion pour « Merger et supprimer ») — jamais pour les variantes forcées elles-mêmes, qui affichent déjà ces mêmes fichiers dans la section ajoutée à `echec_suppression_worktree.html` (ligne ci-dessus). | Aucune commande destructrice : `git status --porcelain=v1 --ignored` exécuté dans le worktree lui-même (`lister_fichiers_ignores_worktree`), en lecture seule. | **Confirmation forte, page dédiée** (`confirmation_fichiers_ignores_worktree.html`), déclenchée dès qu'AU MOINS UN worktree sélectionné contient un fichier/dossier ignoré qui n'est pas du bruit — **aucune suppression ni fusion n'a lieu pour AUCUN worktree du lot** tant que cette page n'a pas été validée, même pour ceux de la sélection qui n'ont eux-mêmes rien à signaler. Motivée par un angle mort réel de git : `git status` (sans `--ignored`) — et donc `git worktree remove`, MÊME SANS `--force` — ne voit jamais les fichiers ignorés par `.gitignore` ; ils disparaissent silencieusement avec le worktree, sans le moindre avertissement (cas réel : l'installeur et l'archive produits par un build Windows de Rummikub dans `installeur\output\`, ignorés, sauvés seulement parce qu'ils avaient été recopiés à la main avant la suppression). La page liste, par worktree concerné, ces fichiers/dossiers au premier niveau de leur propre arborescence ignorée (`git status --ignored` réduit déjà de lui-même un dossier entièrement ignoré à son seul nom, sans logique de regroupement supplémentaire à écrire), avec leur taille quand elle est disponible. **Bruit sans valeur exclu** : une liste GLOBALE, valable pour tous les projets (un seul endroit à éditer dans le code, `DOSSIERS_IGNORES_SANS_VALEUR`/`SUFFIXES_IGNORES_SANS_VALEUR`/`NOMS_FICHIERS_IGNORES_SANS_VALEUR` dans `git_info.py`) : `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `desktop.ini` — jamais un dossier d'environnement ou de dépendances (`venv`, `node_modules`...), volontairement absent de cette liste : il peut représenter un travail d'installation long à refaire, voire un outil installé à la main dans le clone, donc reste toujours affiché plutôt que silencieusement masqué. **Depuis l'issue #119**, s'y ajoute une liste PAR PROJET, alimentée depuis la page elle-même plutôt qu'en éditant le code (voir « Bruit par projet » ci-dessous). **Tailles :** pour un projet local, calculée en octets pour chaque entrée (`os.walk` plafonné en nombre de fichiers ET en temps, partagés entre toutes les entrées d'un même appel — `LIMITE_FICHIERS_TAILLE_FICHIERS_IGNORES`/`LIMITE_SECONDES_TAILLE_FICHIERS_IGNORES`), affichée en octets/Ko/Mo/Go ; au-delà du plafond, ou en cas d'échec filesystem, l'entrée retombe sur « taille non calculée » sans jamais bloquer l'affichage ni la suppression confirmée. Pour un projet distant (PC fixe CCW), **aucun calcul de taille n'est tenté par SSH** (issue #109) : la détection elle-même passe par `_lancer_git` comme toute autre commande (donc par SSH, routée, seulement pour une action sur CE projet précis — jamais d'accès au PC fixe pour les autres), mais chaque entrée affiche directement « taille non calculée ». Un échec de `git status --ignored` lui-même (chemin introuvable, permissions...) retourne une liste vide plutôt que de bloquer quoi que ce soit — à charge de la suppression normale, inchangée, de refléter l'état réel du dossier. Deux actions sur la page : **Annuler** ou **Confirmer la suppression malgré tout** (ré-soumet exactement la requête d'origine, toutes sélections comprises, avec un champ caché `ignorer_avertissement_fichiers_ignores=on` qui contourne cette seule vérification côté serveur — la fenêtre de confirmation forte habituelle, `#modal-confirmation`, s'intercale encore avant l'envoi réel). **Depuis l'issue #116** : une case **« À garder »** apparaît sur chaque fichier/dossier listé (décochée par défaut, jamais présélectionnée), avec un bouton « Tout cocher »/« Tout décocher » par worktree pour la basculer d'un seul geste — ces cases ne servent QUE à décider et à tracer, jamais à choisir individuellement ce qui disparaît : la suppression reste strictement par worktree entier, exactement comme avant. Si au moins une case est cochée, **Confirmer** devient inactif avec un message demandant de copier ces fichiers d'abord (puis de décocher, ou de revenir plus tard) — règle revérifiée CÔTÉ SERVEUR, pas seulement désactivée dans la page : une requête construite à la main malgré tout est refusée sans rien supprimer (et bloque aussi tout classement en bruit de la même requête, voir ci-dessous). Sinon, **Confirmer** ouvre la fenêtre de confirmation forte habituelle (focus par défaut sur Annuler). **Depuis l'issue #119** (remplace le menu obligatoire « origine de la décision » introduit par #116, désormais retiré, suite de données réelles accumulées par le journal — voir la ligne suivante) : cette fenêtre propose, pour chaque fichier/dossier listé, une case **« Classer comme bruit pour ce projet »** (décochée par défaut, jamais présélectionnée), sans aucun menu ni blocage du bouton de validation. Son texte rappelle qu'une case cochée disparaîtra désormais SANS AUCUN AVERTISSEMENT avec tout worktree de CE projet (tout le contenu, pour un dossier). Une fois validée : chaque fichier listé est journalisé « supprimer », chaque chemin coché en plus est ajouté à la liste de bruit du projet (voir « Bruit par projet » ci-dessous) et journalisé « bruit » séparément, puis la suppression a lieu comme avant. **Annuler est redevenu un simple lien** `<a>` (comme avant #116, le menu obligatoire qui le justifiait ayant disparu) : aucune requête, donc aucun enregistrement, rien n'est jamais supprimé pour AUCUN worktree du lot. **Précédent, le fil d'Ariane, un lien vers un autre projet, ou le bouton retour du navigateur restent eux aussi de simples liens `<a>` inchangés** : aucune requête, donc aucun enregistrement, et le ou les worktrees restent exactement tels qu'ils sont — cette page peut être rouverte plus tard en relançant l'action d'origine. |
| **Journal des décisions sur les fichiers ignorés** (issue #116, suite de #112/#113, champ « origine » retiré et ligne « bruit » ajoutée par l'issue #119) | Chaque fichier/dossier listé sur `confirmation_fichiers_ignores_worktree.html`, à la validation de **Confirmer** uniquement — plus aucune ligne écrite pour Annuler (redevenu un simple lien, voir la ligne précédente) ni pour Précédent/fil d'Ariane/liens. | Aucune commande git : une simple ligne ajoutée en fin de fichier texte (`git_info.journaliser_decision_fichier_ignore`). | Pas de confirmation propre — journalisé dans le même geste que la validation de la fenêtre de confirmation forte ci-dessus. **Ne classe rien automatiquement de lui-même** : avant l'issue #119, permettait seulement à Alain de décider plus tard, sur des données réelles, quels fichiers reviennent assez souvent pour être considérés comme du bruit — certains fichiers revenaient à chaque suppression (ex. `secret_key.conf`, `changelog_fusion.log` dans les worktrees de Relecture_Bridge lui-même) et la décision revenait jusqu'ici à Alain à chaque fois, parfois après en avoir parlé avec un Claude Chat ; cette donnée accumulée a servi à créer la liste de bruit par projet (voir la ligne suivante). **Format d'une ligne** (texte, UTF-8, ajout seul) : `AAAA-MM-JJTHH:MM:SS | projet=<nom> | branche=<branche> | fichier=<chemin affiché> | taille=<taille affichée ou "taille non calculée"> | decision=<garder|supprimer|bruit>` — une ligne par fichier et par décision, jamais groupée ; `bruit` s'ajoute, pour un même fichier, EN PLUS de sa ligne `garder`/`supprimer`, jamais à sa place. **Pas un journal de résultat** : la ligne reflète la décision prise au moment de la validation, même si une suppression réelle échoue ensuite (renvoi vers `echec_suppression_worktree.html`, page de suppression forcée non modifiée par ces issues) — vérifier après coup le sort réel d'un worktree donné reste à faire à la main pour l'instant. **Emplacement** (`git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES`, constante modifiable pour les tests) : `relecture_web/decisions_fichiers_ignores.log`, hors de tout worktree, même principe que `relecture_web/changelog_fusion.log` (issue #62) — ignoré par git (`.gitignore` racine), sans quoi il ferait apparaître le dossier principal de `relecture_web` comme modifié et bloquerait les fusions automatiques du CHANGELOG. **Écriture jamais bloquante** : une impossibilité d'écrire (dossier en lecture seule, disque plein...) n'empêche jamais l'action en cours, seulement un message flash d'avertissement sur la page suivante — sans jamais laisser croire que la décision a bien été enregistrée. |
| **Bruit par projet** (issue #119, suite de #112/#116) | Chaque chemin coché « Classer comme bruit pour ce projet » dans la fenêtre de confirmation forte de `confirmation_fichiers_ignores_worktree.html` (ligne ci-dessus) — jamais ailleurs, jamais automatiquement. | Aucune commande git : lecture/écriture d'un fichier texte local (`git_info.lire_bruit_projets`/`ajouter_bruit_projet`/`retirer_bruit_projet`). | S'ajoute, PAR PROJET, au bruit global sans valeur de la ligne « Avertissement fichiers ignorés » ci-dessus (`DOSSIERS_IGNORES_SANS_VALEUR` et voisines, valables pour tous les projets, toujours le seul endroit à éditer dans le code pour en exclure davantage GLOBALEMENT) — volontairement pas de règle par nom seul valable pour tous les projets : un fichier de clé ou de journal portant le même nom dans un autre projet reste signalé. **Stockage** (`git_info.CHEMIN_LISTE_BRUIT_PROJETS`, constante modifiable pour les tests) : `relecture_web/bruit_projets.log`, même emplacement et même principe que le journal des décisions ci-dessus — hors de tout worktree, ignoré par git, créé au premier ajout. Fichier texte lisible et modifiable à la main, une entrée par ligne (`projet=<nom> | chemin=<chemin exact affiché sur la page de confirmation>`), relu à chaque détection (jamais mis en cache), donc sans redémarrage de relecture_web pour qu'un ajout/retrait prenne effet. **Entrées initiales** : pour `relecture_bridge` lui-même, `relecture_web/secret_key.conf` (clé de session créée par l'application lancée pendant les tests d'une issue) et `relecture_web/changelog_fusion.log` (journal de fusion rempli par ces mêmes essais) — aucune autre entrée présumée pour aucun projet, en particulier aucun dossier d'environnement/dépendances ni de sorties de build. **Dégradation systématique vers la prudence** : fichier absent, illisible, ou ligne individuellement mal formée (ignorée SEULE, sans faire échouer les lignes valides voisines) → aucun filtrage supplémentaire, donc plus de signalements, jamais moins — exactement le comportement d'avant cette issue. **Classement accepté CÔTÉ SERVEUR uniquement dans une requête qui porte réellement la confirmation de suppression** (`ignorer_avertissement_fichiers_ignores=on`, sans case « à garder » cochée, voir la ligne ci-dessus) — jamais seul, jamais via une autre route. Les projets distants du PC fixe (`_ccw`, section 11) utilisent le même mécanisme et la même clé de projet : aucun accès SSH ajouté, puisque ce fichier ne dépend jamais du filesystem distant. |
| **Panneau « Bruit ignoré pour ce projet »** (issue #119) | Les entrées de bruit par projet de la ligne ci-dessus, pour le projet affiché. | Aucune commande git : relecture/réécriture du même fichier texte local que la ligne ci-dessus. | **Aucune confirmation** (contrairement au panneau .gitignore ci-dessous) : « Retirer » ne supprime jamais rien, seulement une entrée de cette liste — l'avertissement avant suppression de worktree redevient alors actif pour ce chemin, dans ce projet. Panneau repliable (`<details id="details-bruit">`), fermé par défaut, dans la section « 🛠️ Outils du projet » à côté du panneau .gitignore — même esprit que ce dernier (issue #98), sans aucun de ses refus (projet distant, fusion en cours, badge « CCL travaille ici »…) : ce panneau ne touche jamais le dépôt git du projet, seulement le fichier de bruit local, donc fonctionne à l'identique pour un projet distant. |
| **Ajouter un motif au .gitignore** (issue #98) | Le `.gitignore` à la racine du worktree **principal** du projet (jamais ceux des worktrees de CCL, jamais de `.gitignore` imbriqué). | `git add -- .gitignore` **puis** `git commit -m "chore: .gitignore — ajoute <motif>" -- .gitignore` | **Aucune confirmation** — ajout réversible en un clic (bouton « Retirer » sur la ligne). Validé avant écriture : une seule ligne, non vide, pas de doublon exact déjà présent. Un motif qui désigne un dossier existant du projet reçoit automatiquement un `/` final s'il manque (signalé dans le message de retour). Raccourci « Ignorer » : même action, motif prérempli depuis la liste des fichiers/dossiers non suivis et non ignorés du dépôt (même source que le garde-fou Merger de l'issue #74, `git status --porcelain`). **Piège git signalé automatiquement (issue #98) :** un motif ajouté n'arrête jamais de suivre un fichier déjà suivi par git — `git ls-files -i -c --exclude=<motif>` est relancé juste après l'ajout (et à chaque affichage de la page, pour rester visible après un rafraîchissement) ; tout fichier déjà suivi concerné est listé avec un bouton « Ne plus suivre » (voir ligne suivante), jamais traité automatiquement. |
| **Retirer un motif du .gitignore** (issue #98) | Une ligne « motif » du `.gitignore` affiché (jamais une ligne commentaire ou vide, conservées mais non supprimables individuellement). | `git commit -m "chore: .gitignore — retire <motif>" -- .gitignore` (après réécriture du fichier sans cette ligne) | **Confirmation légère** (même niveau que Merger) — l'avertissement rappelle que les fichiers visés par ce motif redeviennent non suivis, avec le risque de les committer par erreur ensuite. L'index et le texte exact de la ligne sont revérifiés côté serveur contre l'état actuel du fichier avant toute suppression — un décalage (fichier modifié entre l'affichage et l'envoi du formulaire) fait échouer l'action plutôt que de retirer la mauvaise ligne. |
| **Ne plus suivre** (issue #98) | Un fichier déjà suivi par git qui correspond à un motif du `.gitignore` (piège ci-dessus). | `git rm --cached -- <chemin>` **puis** `git commit -m "chore: ne plus suivre <chemin>" -- <chemin>` | **Confirmation forte** — modifie l'index et crée un commit ; jamais lancé automatiquement, uniquement sur ce bouton explicite. Le fichier reste intact sur disque, seul son suivi par git s'arrête. |

Les trois actions ci-dessus partagent un même refus commun, avant même
d'afficher le contenu du panneau : projet **distant** (PC fixe CCW, section
11 — la lecture/écriture de fichier distante fait partie des surfaces
hors-git encore non traitées, #94), fusion en cours (`MERGE_HEAD`), badge
« ⚠ CCL travaille ici » actif sur le worktree principal du projet (section
4), ou `.gitignore` déjà modifié de façon non committée **avant** toute
action de ce panneau — ce dernier cas signale une modification d'origine
extérieure (édition manuelle en terminal, autre outil) que le panneau ne
doit jamais embarquer silencieusement dans son propre commit automatique.
Dans tous ces cas, le panneau affiche le motif du refus à la place de son
contenu habituel plutôt que de tenter une lecture qui n'aurait pas de sens
(ex. filesystem distant inaccessible). Panneau repliable (`<details
id="details-gitignore">`), fermé par défaut — même principe que le panneau
« Options de rejet » de l'issue #97.

**Emplacement (issue #117) :** ce panneau, affiché jusque-là en haut de la
page projet (juste sous les messages flash), est désormais dans une
section autonome « 🛠️ Outils du projet » en bas de page, sous la liste des
branches et son panneau d'actions — avant cette issue, il était affiché
directement sous le message de refus « Modifications non committées » de
Merger (ci-dessus, issue #74), dont la seule ligne ressemblant à un nom de
fichier était alors « 📄 .gitignore » : un Claude Chat consulté sur
capture d'écran avait conclu à tort que ce fichier était la cause du
refus, alors que le panneau n'a aucun rapport (cas réel, projet
rummikub). Son identifiant (`#details-gitignore`) et ses trois actions
(ajouter/retirer un motif, « Ne plus suivre ») sont inchangés — aucune
redirection de cette page ne dépendait de sa position précédente (chaque
action redirige simplement vers le haut de la page projet, sans ancre).
Le panneau « Bruit ignoré pour ce projet » (`#details-bruit`, issue #119,
voir §9 ci-dessus) a rejoint cette même section « 🛠️ Outils du projet »
dès sa création, juste à la suite de celui-ci.

| **Sécuriser** (un commit ou tous) | Un commit orphelin, ou tous les commits orphelins d'un projet. | `git branch recuperation-<hash> <hash>` | **Aucune confirmation.** Voir section 6 — geste purement défensif, idempotent. |
| **Supprimer la/les branche(s) de récupération** | Une ou plusieurs branches sélectionnées suivant la convention `recuperation-<hash>` (panneau d'actions de la page projet, ou suppression groupée depuis « Comparer la sélection »). | `git branch -D <nom>` | **Confirmation forte** (issue #71) — références difficiles à récupérer. Voir section 6 — refus structurel si le nom ne suit pas exactement la convention, indépendamment du badge affiché. Supprime aussi les fichiers `Non_Lu/` de toute la chaîne de commits protégée par la branche, pas seulement le hash nommé. |
| **Comparer** | Un commit orphelin (cas B), en lecture seule. | `git diff <hash1> <hash2>` (après localisation par `git patch-id`) | **Aucune confirmation** — lecture seule, aucune modification (voir section 5). |
| **Comparer la sélection** | Une ou plusieurs branches `recuperation-<hash>` sélectionnées, en lecture seule. | `comparer_commit_doublon` (donc `git diff`/`git patch-id`) relancé pour chacune | **Aucune confirmation** — lecture seule, aucune modification (voir section 5). Branche hors convention `recuperation-<hash>` ignorée. Le bouton de suppression groupée proposé sur le résultat ne couvre que les branches confirmées diff vide (voir ligne « Supprimer la/les branche(s) de récupération » ci-dessus pour son propre garde-fou). |
| **Générer rapport** | Un commit non tranché (cas F, ou tout commit affiché sur une branche), en lecture seule. | `git cherry`, `git branch --contains`, `git branch -r --contains` (assemblés en texte) | **Aucune confirmation** — lecture seule, aucune modification (voir section 5). |
| **Nettoyer tous les projets** | Tous les projets accessibles. | suppression de fichiers `Non_Lu/` (pas de commande git) | **Aucune confirmation.** Ne supprime que les résumés dont le commit est déjà un ancêtre d'une branche **distante** (`git branch -r --contains`) — jamais un résumé dont le commit n'est pas encore réellement en sécurité sur GitHub. |
| **Nettoyer ce projet** | Le seul projet affiché (page « branches d'un projet », issue #68). | suppression de fichiers `Non_Lu/` (pas de commande git) | **Aucune confirmation.** Même garde-fou et même fonction que « Nettoyer tous les projets » ci-dessus, appliquée à un seul projet — évite de repasser par la liste des projets après un push depuis cette page. **Depuis l'issue #128, déclenché automatiquement après un push confirmé abouti depuis cette même page** (voir section 13) — ce bouton et « Nettoyer tous les projets » restent par ailleurs inchangés, pour les cas que ce déclenchement automatique ne voit pas (un push fait directement en terminal, hors de relecture_web). |
| **Finaliser le merge** | Le merge en cours du projet (page « branches d'un projet »). | `git commit --no-edit` | **Aucune confirmation** (issue #71). Voir section 10 — n'apparaît que si un merge est réellement en cours (`MERGE_HEAD` présent) ET qu'il ne reste plus aucun fichier en conflit ; revalidé côté serveur à partir de l'état git actuel, jamais de commit partiel. Même timeout étendu (120s) que Push et Merger (issue #64) — ce commit déclenche le hook `post-commit` du projet, qui peut dépasser le timeout court sur un fichier volumineux ; en cas de dépassement, l'état réel est revérifié automatiquement (`MERGE_HEAD` a-t-il disparu ?) et le message flash final indique explicitement si le merge a bien été finalisé, plutôt qu'un renvoi systématique vers une vérification manuelle (issue #66). |
| **Retraiter le fichier en conflit** | Un fichier déjà résolu (`git add` fait) du merge en cours, page « branches d'un projet » (issue #72). | `git checkout --conflict=merge -- <chemin>` | **Aucune confirmation** (issue #72, retirée par l'issue #73 — action peu risquée : elle ne fait que refaire la résolution de ce fichier). Proposé pour chaque fichier déjà résolu du merge en cours : à côté du fichier concerné tant que d'autres fichiers restent en conflit, ou juste à côté de « Finaliser le merge » une fois tous les fichiers résolus (issue #73 — jusque-là dans une section séparée plus bas, visuellement loin de « Finaliser »). N'apparaît que si un merge est réellement en cours (`MERGE_HEAD` présent), revérifié côté serveur ; le chemin n'est accepté que s'il figure dans `git ls-files --resolve-undo`. Les marqueurs recréés portent les libellés génériques « ours »/« theirs » (voir section 10). Une fois l'action effectuée, amène directement sur la page Conflit du fichier remis en conflit (issue #73 — auparavant sur la page projet, obligeant à recliquer sur le fichier). Disparaît une fois le merge finalisé. |
| **Traiter ce bloc** | Un bloc de conflit précis, sur la page Conflit (issue #56). | Aucune commande git — écriture directe du fichier ; `git add <chemin_relatif>` automatique seulement si ce bloc était le dernier du fichier. | **Aucune confirmation** (issue #71). Voir « réversibilité » ci-dessous et section 10. |
| **Traiter tous les blocs** | Tous les blocs de conflit d'un fichier affiché sur la page Conflit (issue #69). | `git add <chemin_relatif>` une fois tous les blocs remplacés (pas de commande git de remplacement — écriture directe du fichier, comme « Traiter ce bloc »). | **Aucune confirmation par défaut ; confirmation légère (fenêtre maison depuis l'issue #73, plus `confirm()` natif) uniquement si une anomalie est détectée** — au moins un bloc au résultat vide (issue #71). L'avertissement listant ces blocs vides est affiché en premier dans la fenêtre, mis en évidence (issue #73). Voir section 10 — tout ou rien : `resoudre_tous_blocs_conflit` refuse tout le traitement (aucun bloc écrit) si le nombre de blocs actuellement présents ne correspond plus à ce qui a été affiché, ou si une empreinte (sha256) du contenu calculée à l'affichage ne correspond plus au contenu actuel. Réutilise `_trouver_blocs_conflit` (même numérotation que l'affichage et que « Traiter ce bloc ») ; applique les remplacements du dernier bloc vers le premier pour que les décalages d'index provoqués par un remplacement ne perturbent jamais les blocs restant à traiter. « Traiter ce bloc » reste disponible, inchangé, pour un traitement bloc par bloc. |

**Réversibilité d'un fichier déjà résolu pendant un merge en cours (issue
#72) :** tant que le merge n'est pas finalisé (`MERGE_HEAD` présent), la
résolution déjà appliquée à un fichier — y compris après le `git add`
automatique lancé par « Traiter ce bloc » / « Traiter tous les blocs » une
fois son dernier bloc traité — reste réversible individuellement, pas
seulement avant ce `git add`. Git conserve dans l'index de quoi annuler
cette résolution via son mécanisme « resolve-undo » (`git ls-files
--resolve-undo`, qui répertorie les fichiers résolus du merge en cours) ;
`git checkout --conflict=merge -- <chemin>` (comportement vérifié en local
sur git 2.43) s'appuie dessus pour recréer les marqueurs de conflit
d'origine pour ce fichier précis, sans toucher aux autres fichiers déjà
résolus. Le bouton « Retraiter le fichier en conflit » ci-dessus expose
désormais ce geste directement depuis `relecture_web`, sans repasser par
un terminal. Seule différence par rapport aux marqueurs d'origine : les
libellés redeviennent génériques (`ours`/`theirs`) au lieu de `HEAD` et du
nom de la branche entrante (issue #70) — la page Conflit reste lisible
dans ce cas, voir section 10. La vraie limite reste la finalisation du
merge (bouton « Finaliser le merge », qui exécute le `git commit`) : une
fois ce commit fait, `MERGE_HEAD` disparaît et `relecture_web` ne propose
plus ni ce bouton ni « Finaliser le merge » — `git merge --abort` cesse
lui aussi de fonctionner à ce moment précis (vérifié), ce qui fait de ce
commit le vrai point de non-retour du merge dans son ensemble.

Deux compléments d'ergonomie purement côté navigateur (issue #69), sans
route serveur ni commande git, donc absents du tableau ci-dessus :

- **Rafraîchir** (page « branches d'un projet », et depuis l'issue #73
  aussi la page Conflit) — un simple lien vers l'URL courante de la page
  (pas un `location.reload()` ni un F5 clavier), pour revoir l'état git à
  jour après une action faite en terminal sans jamais risquer de faire
  réapparaître l'avertissement « resoumettre le formulaire » du
  navigateur : toutes les actions de ce tableau redirigent déjà en GET
  après leur POST (motif Post/Redirect/Get), donc un vrai F5 sur la page
  affichée ne poserait normalement pas ce problème non plus — le bouton
  est une garantie supplémentaire, pas un contournement d'un bug
  existant. Sur la page Conflit, utile en particulier après le refus « le
  fichier a changé depuis l'affichage » (« Traiter ce bloc » / « Traiter
  tous les blocs »), dont le message demande justement de recharger la
  page.
- **Copier** (icône 📋) — copie dans le presse-papiers le chemin d'un
  fichier en conflit tel que renvoyé par `git status` (relatif à la
  racine du dépôt), pour le coller dans un terminal ou un éditeur.
  Présent à côté de chaque fichier listé dans la section « ⚠ Fusion en
  conflit » (page projet) et dans l'en-tête de la page Conflit — même
  bouton générique `.bouton-copier` (`base.html`) déjà utilisé ailleurs
  pour copier un hash ou un nom de branche, avec le même retour visuel
  bref (icône remplacée par ✓ quelques instants).

## 10. Détecter, afficher et résoudre les conflits de fusion (issues #55, #56, #59)

Quand un `git merge` déclenché depuis le panneau d'actions (section 9)
échoue par conflit, le dépôt reste volontairement en état de fusion non
résolue plutôt que de revenir en arrière (voir action **Merger**,
section 9). Sur la page « branches d'un projet », une section **⚠
Fusion en conflit** apparaît alors en tête de page, listant chaque
fichier concerné avec son code `git status --porcelain` à deux lettres
(le plus courant : `UU`, modifié des deux côtés ; les combinaisons
ajout/suppression `AA`/`DD`/`AU`/`UA`/`DU`/`UD` sont aussi détectées).

Cliquer sur un fichier ouvre une page dédiée qui localise chaque bloc
entre les marqueurs `<<<<<<<`, `=======` et `>>>>>>>`.

Si le dépôt a été fusionné avec `merge.conflictStyle=diff3` (marqueur
supplémentaire `|||||||` pour la base commune), la base est ignorée :
seules les deux versions en conflit sont affichées, pas la base à trois
voies.

Le chemin de fichier demandé n'est accepté que s'il figure dans la
liste actuelle des fichiers en conflit renvoyée par `git status` —
jamais construit à l'aveugle à partir du seul paramètre d'URL.

**Vue à deux panneaux synchronisés (issue #59)** : la page affiche le
fichier complet en deux colonnes côte à côte plutôt qu'un bloc isolé de
son contexte.

- **Panneau gauche** (lecture seule) : le fichier complet, avec chaque
  bloc de conflit affiché à sa vraie place dans le texte environnant —
  version « ours »/`HEAD` sur fond bleu, version « theirs »/branche
  entrante sur fond orange — volontairement pas un `<textarea>`, qui ne
  permet pas ce code couleur.
- **Panneau droit** (éditable) : le même fichier, avec à l'emplacement
  de chaque bloc un `<textarea>` où Alain compose le texte final à
  garder (copie d'une des deux versions, combinaison des deux, ou tout
  autre texte — y compris vide, pour supprimer le bloc). Trois flèches
  entre les deux panneaux, une par bloc : bleue (copie « ours » dans le
  résultat), orange (copie « theirs »), verte (vide le résultat) — le
  texte reste modifiable à la main après un transfert, ce n'est jamais
  une copie figée. Chaque `<textarea>` prend au moins la hauteur du bloc
  correspondant du panneau gauche (issue #73, `align-items: stretch` sur
  la grille CSS partagée décrite ci-dessous) : sur un gros bloc de conflit
  (ex. un tableau de documentation), la zone d'édition reste confortable
  au lieu de rester minuscule au milieu d'un long panneau gauche.

Les deux panneaux et leurs en-têtes partagent une seule grille CSS à
trois colonnes (gauche / flèches / droite) construite ligne par ligne
à partir des mêmes segments — le défilement est donc synchronisé par
construction (une seule barre de défilement pour toute la page, pas
deux volets indépendants à recaler en JS). Pour que ça tienne, les
segments de contexte de cette page ne doivent jamais porter de hauteur
plafonnée avec défilement interne (la règle générique `pre.brut`,
utilisée ailleurs comme `branche.html`, est volontairement neutralisée
ici) — sinon chaque segment redevient un volet à défiler pour
lui-même, gauche et droite se désynchronisent, et il n'y a plus de
grille unique à faire défiler (bug corrigé par l'issue #65). Des
boutons « ◀ » / « ▶ » dans l'en-tête (avec position affichée, ex.
« Bloc 2 / 5 ») permettent de naviguer entre les blocs d'un même
fichier sans quitter la page : le bloc ciblé est mis en évidence
(contour bleu) et amené au centre de l'écran par un défilement fluide.
Une marge de respiration (`padding-bottom: 50vh` sous la grille)
garantit qu'il reste toujours assez d'espace de défilement sous le
dernier bloc du fichier pour le centrer réellement à l'écran, y
compris quand il n'a que peu de contenu après lui (issue #65).

**Résolution bloc par bloc (issue #56)**, inchangée sous cette
nouvelle vue : un bouton « Traiter ce bloc » (avec confirmation JS,
aperçu du texte inclus) remplace ce bloc précis — marqueurs
`<<<<<<<`/`=======`/`>>>>>>>` compris — par le contenu du `<textarea>`
du panneau droit dans le fichier réel, en local uniquement.

La numérotation des blocs (0-based, ordre d'apparition dans le
fichier) est calculée par la même fonction que l'affichage
(`_trouver_blocs_conflit`), pour que le bloc traité soit toujours
exactement celui affiché. Si le fichier a changé entre l'affichage et
la soumission (bloc déjà traité, fichier modifié ailleurs) au point que
ce numéro ne corresponde plus, la résolution échoue proprement avec un
message d'erreur plutôt que d'écrire sur le mauvais bloc — Alain doit
recharger la page.

Une fois le dernier bloc d'un fichier traité, `git add <fichier>` est
lancé automatiquement pour marquer sa résolution, avec un message flash
clair — **le push reste un geste manuel**, volontairement non
automatisé. Tant qu'il reste des blocs, la page se recharge sur le
même fichier (le bloc suivant apparaît naturellement en premier).

**Préservation des fins de ligne (issue #107, suite de l'issue #105)** :
la lecture et la réécriture du fichier (`lire_conflits_fichier`,
`resoudre_bloc_conflit`, `resoudre_tous_blocs_conflit`) se font avec
`newline=""` — Python ne traduit donc jamais `\r\n` en `\n` à la lecture
ni l'inverse à l'écriture. Un fichier entièrement en CRLF reste
entièrement en CRLF après résolution d'un ou plusieurs blocs, un fichier
LF reste en LF, et un fichier mixte garde chaque ligne de contexte (y
compris un bloc non traité) avec exactement sa terminaison d'origine —
seul le texte du bloc réellement remplacé change.

Le texte validé (contenu du `<textarea>` soumis, quelle que soit la
façon dont il a été composé — saisi à la main, copié via une flèche
« ours »/« theirs », « garder les deux », ou vidé) est, lui, normalisé
avant insertion vers la fin de ligne **dominante du fichier cible** :
la plus fréquente entre CRLF et LF dans le fichier, LF par défaut en cas
d'égalité ou d'absence de toute fin de ligne. Cette normalisation est
nécessaire parce qu'un navigateur convertit les retours à la ligne d'un
`<textarea>` en CRLF au moment de la soumission d'un formulaire HTML,
quelle que soit leur forme dans le DOM — y compris pour un texte
composé par une flèche de copie, pas seulement pour du texte tapé à la
main. Sans cette normalisation, un fichier LF recevrait du CRLF à
l'endroit de chaque bloc traité, aboutissant à des fins de ligne
mélangées au sein d'un même fichier. Le texte précalculé pour le bouton
« Copier ce bloc » (`_texte_affiche_bloc`) est quant à lui toujours
rendu en `\n`, qu'il provienne d'un bloc CRLF ou non : destiné au
presse-papiers, il ne doit jamais exposer de caractère `\r` à Alain.

**Traiter tous les blocs (issue #69)** : pour éviter de recliquer
« Traiter ce bloc » un par un (ce qui recharge la page à chaque fois),
un bouton « Traiter tous les blocs » applique en une seule opération
chaque `<textarea>` du panneau droit à son bloc correspondant, sans
quitter la page. Il réutilise directement `_trouver_blocs_conflit`
(même numérotation que l'affichage et que la résolution bloc par bloc),
donc chaque texte final est garanti appliqué au bon bloc.

- **Tout ou rien** : côté serveur, `resoudre_tous_blocs_conflit`
  refuse le traitement complet — aucun bloc n'est écrit, même
  partiellement — si le fichier a changé depuis l'affichage : nombre de
  blocs actuellement présents différent de ce qui a été soumis, ou
  empreinte (sha256 du contenu, calculée par `lire_conflits_fichier` au
  moment de l'affichage puis transmise par des champs cachés) qui ne
  correspond plus au contenu réel du fichier au moment de la
  soumission. Même principe que la résolution bloc par bloc, appliqué à
  l'ensemble du fichier plutôt qu'à un seul bloc.
- **Ordre d'application** : les remplacements sont appliqués du dernier
  bloc vers le premier — remplacer un bloc décale les index de ligne de
  tous les blocs qui le suivent dans le fichier, jamais ceux qui le
  précèdent, donc traiter dans l'ordre inverse garantit que chaque
  remplacement utilise encore des index valides pour les blocs restant
  à traiter.
- **Fin de ligne unique pour tous les blocs (issue #107)** : la fin de
  ligne dominante du fichier est calculée une seule fois, sur le contenu
  d'origine avant tout remplacement, puis appliquée à chaque texte final
  soumis — un fichier résolu en une seule fois ressort donc avec une
  convention unique même si ses blocs ont été composés par des chemins
  différents (ex. un bloc tapé à la main, un autre via « Garder les
  deux », chacun arrivé en CRLF côté formulaire).
- **Confirmation JS** avant soumission, qui liste explicitement les
  blocs dont le `<textarea>` est vide — un résultat vide est légitime
  (suppression pure et simple du bloc) mais facile à soumettre par
  inadvertance, d'où l'avertissement explicite plutôt qu'un silence sur
  ce cas particulier. Cette liste affiche la position 1-based de chaque
  bloc (celle de « Bloc X / N » dans l'en-tête), pas l'index 0-based
  interne évoqué ci-dessus — seul l'affichage diffère, les index transmis
  au serveur restent le 0-based habituel (issue #70).
- Une fois tous les blocs traités, `git add <fichier>` est lancé
  automatiquement, exactement comme pour le dernier bloc traité
  individuellement — le commit et le push restent des gestes manuels.
- « Traiter ce bloc » reste disponible, inchangé, pour un traitement
  bloc par bloc quand c'est plus adapté (vérifier un bloc à la fois
  avant de valider les suivants, par exemple).

**Finaliser le merge (issue #61)** : une fois que `git status` ne
signale plus aucun chemin non fusionné, la section « Fusion en
conflit » de la page projet ne liste plus de fichiers — elle affiche à
la place un unique bouton « ✅ Finaliser le merge », qui exécute
`git commit --no-edit` (équivalent non-interactif de `git commit` sans
`-m` : accepte tel quel le message déjà préparé par git dans
`.git/MERGE_MSG`, impossible à éditer depuis une page web). Avant
cette issue, ce commit restait la seule étape encore manuelle du flux
de résolution — obligeant à rebasculer en terminal juste pour ça.

Deux conditions cumulatives, revérifiées côté serveur à partir de
l'état git actuel (pas de la seule page déjà affichée) avant toute
exécution :
- un merge est réellement en cours (`git rev-parse --verify --quiet
  MERGE_HEAD` réussit — distingue un vrai merge en cours d'un simple
  conflit `UU` isolé, par exemple un cherry-pick ou un revert en
  conflit, qui ne créent jamais `MERGE_HEAD`) ;
- `get_fichiers_en_conflit` ne renvoie plus aucun fichier.

Si l'une des deux conditions n'est pas remplie (bouton absent, ou
formulaire soumis depuis une page obsolète après qu'un fichier a été
modifié en dehors de `relecture_web`), l'action est refusée par message
flash plutôt que de tenter un commit partiel.

Ce commit déclenche le hook `post-commit` du projet, qui appelle Claude
en ligne de commande pour générer le résumé fonctionnel
(`resumer_diff.py`) — une opération pouvant dépasser le timeout court
par défaut sur un fichier volumineux. `finaliser_commit_merge` utilise
donc le même timeout étendu (120s) que Push et Merger, avec la même
gestion d'erreur par message flash en cas de dépassement plutôt qu'une
page d'erreur brute (issue #64).

En cas de dépassement, `verifier_finalisation_merge_apres_timeout`
(`git_info.py`) revérifie l'état réel du dépôt avant d'afficher le
message flash final : dans ce flux précis, la seule façon connue de
faire disparaître `MERGE_HEAD` est le commit visé par
`finaliser_commit_merge` lui-même, donc sa disparition signale de façon
fiable que le commit a bien été créé avant que le timeout Python ne
tue le process (probablement resté bloqué dans le hook `post-commit`
ci-dessus) — Alain n'a plus besoin d'ouvrir un terminal pour le
confirmer à chaque fois (issue #66). Même principe de revérification
automatique après timeout pour Push (comparaison `git ls-remote` /
commit local) et Merger (branche source devenue ancêtre de la cible ?),
voir section 9.

**Retraiter le fichier en conflit (issues #72, #73)** : dans la section
« ⚠ Fusion en conflit », chaque fichier déjà résolu (`git add` fait)
pendant le merge en cours porte un bouton « 🔁 Retraiter ce fichier » —
à côté du fichier concerné tant que d'autres fichiers restent en conflit,
ou dans le même groupe que « ✅ Finaliser le merge » (`.ligne-finaliser-
merge`) une fois tous les fichiers résolus (issue #73 — avant cette
issue, cette seconde liste restait dans une section séparée plus bas,
visuellement loin du bouton « Finaliser »). La liste de ces fichiers
résolus vient de `get_fichiers_resolus_merge` (`git ls-files
--resolve-undo`, voir paragraphe « Réversibilité » section 9) ; le clic
exécute `retraiter_fichier_conflit` (`git checkout --conflict=merge --
<chemin>`), qui recrée les marqueurs de conflit d'origine pour ce fichier
précis — il redevient `UU` et réapparaît dans la liste des fichiers en
conflit.

Deux garde-fous, revérifiés côté serveur à partir de l'état git actuel
avant toute exécution, sur le même principe que « Finaliser le merge » et
la page Conflit :
- un merge est réellement en cours (`MERGE_HEAD` présent) ;
- le chemin demandé figure dans la liste actuelle renvoyée par
  `get_fichiers_resolus_merge` — jamais construit à l'aveugle à partir du
  seul paramètre d'URL.

**Aucune confirmation** (issue #73 — retirée par rapport à l'issue #72) :
refaire la résolution d'un fichier précis reste une action peu risquée, la
confirmation JS qui la précédait entretenait surtout la fatigue de
confirmation sans protéger grand-chose. Une fois l'action effectuée avec
succès, `relecture_web` amène directement sur la page Conflit de ce
fichier (issue #73 — auparavant sur la page projet, obligeant à recliquer
dessus pour l'ouvrir) ; le message flash de succès signale que les
marqueurs recréés portent les libellés génériques `ours`/`theirs` plutôt
que `HEAD` et le nom de la branche entrante (différence propre au
mécanisme resolve-undo, qui ne conserve pas ces noms) : la page Conflit
reste lisible dans ce cas, les libellés de branche entrante introduits
par l'issue #70 (`nom_branche_bloc`, dérivé de l'en-tête `>>>>>>>`)
affichent alors simplement « theirs ». Un conflit ajout/suppression
(codes `AU`/`UD`/`DU`/`UA` de `get_fichiers_en_conflit`) échoue
proprement, sans rien modifier : l'un des deux côtés n'a alors aucune
version du fichier, donc git refuse la reconstruction plutôt que
d'inventer un contenu — dans ce cas d'échec, la redirection reste celle
vers la page projet (rien n'a changé à rouvrir). Le bouton disparaît
naturellement une fois le merge finalisé (plus de `MERGE_HEAD`).

**« Garder les deux » (issue #90)** : une quatrième flèche, violette
(⇅), entre les flèches bleue/orange et le bouton ✕ vide. Contrairement
aux flèches bleue et orange (remplacement complet du résultat, comportement
inchangé), celle-ci concatène — le contenu HEAD puis celui de la branche
entrante à la suite dans le `<textarea>` du résultat, avec un saut de
ligne entre les deux uniquement si le texte HEAD n'en a pas déjà un en
fin (jamais de ligne vide dupliquée). Répond au cas fréquent de deux
ajouts indépendants au même endroit, où il faut garder les deux plutôt
que choisir un seul côté.

**« Copier ce bloc » (issue #90)** : dans le panneau gauche (lecture
seule), chaque bloc porte en plus son propre bouton `.bouton-copier`
(coin haut-droit), qui copie tout le texte affiché de ce bloc précis —
en-têtes `<<<<<<<`/`>>>>>>>` et contenu des deux côtés compris, tel
qu'affiché à l'écran — pour un collage direct dans une conversation
Claude Chat, sans passer par une capture d'écran (imprécise sur les gros
blocs). Le texte copié est précalculé côté serveur (`texte_affiche` dans
`_extraire_blocs_conflit`, `git_info.py`), avec la même règle de saut de
ligne que « Garder les deux » ci-dessus, pour ne jamais dupliquer une
ligne vide entre les deux moitiés du bloc. Le marqueur `=======` séparant
les deux versions dans un fichier en conflit brut n'apparaît volontairement
pas dans cette page (ni à l'écran ni dans le texte copié) : le panneau
gauche remplace déjà ce séparateur par l'en-tête `>>>>>>> <branche>` au-dessus
du contenu de la branche entrante, qui joue le même rôle de repère visuel
sans perdre le nom de la branche.

## 11. Le mode SSH vers le PC fixe Windows (CCW, issue #94)

Un seul PC physique Windows héberge tous les projets CCW (chemins locaux
du type `C:\CCW\<NomProjet>`), distinct du ThinkPad où tourne
`relecture_web`. Cette issue ajoute le **routage local/distant des
commandes git elles-mêmes** — étape 2 vers le pilotage de ces projets
depuis `relecture_web`, après le socle de centralisation de l'issue #93
(`_lancer_git`, point d'entrée unique de toute commande git de
`git_info.py`).

**Détection d'un projet distant** — un projet est considéré distant si
son `repertoire` (tel que retourné par `fetch_projets`, donc par
`BRIDGE_AGENT_DOC.md`) a la forme d'un chemin Windows (`^[A-Za-z]:\\`,
`est_projet_distant`) : heuristique gratuite, sans appel réseau ni
configuration par projet — le PC fixe CCW est aujourd'hui le seul cas où
ce format apparaît (le ThinkPad n'utilise que des chemins POSIX).

**Configuration (`relecture_web/ccw_host.conf`, personnel, hors git —
issue #110)** — même convention que `branches_cibles.conf` (`cle =
valeur`, une entrée par ligne, `#` pour les commentaires), mais un seul
hôte pour tous les projets CCW :

```
ccw_host = <utilisateur>@<ip-locale>
ccw_key = ~/.ssh/ccl_ccw   # optionnel, c'est déjà la valeur par défaut
```

- `ccw_host` : `utilisateur@hôte` (ou IP locale) du PC fixe. Tant qu'il
  n'est pas renseigné, `charger_config_ccw()` retourne `None` : toute
  tentative de commande git sur un projet distant échoue proprement
  (code de retour 1, message d'erreur clair), sans tenter de connexion.
- `ccw_key` : chemin de la clé SSH privée à utiliser, optionnel — repli
  sur `~/.ssh/ccl_ccw`, la clé déjà en place côté ThinkPad.
- Même statut que `branches_cibles.conf` (section 7) une fois renseigné :
  CCL ne modifie jamais ce fichier de sa propre initiative — seul Alain
  l'édite à la main.

**`ccw_host.conf` n'est PAS suivi par git (issue #110)** — ce fichier
contient l'identifiant de session et l'adresse locale réels du PC fixe
d'Alain, une information personnelle qui ne doit jamais être poussée sur
GitHub par accident (même traitement que `secret_key.conf`, voir §1 —
`relecture_web/.gitignore`). Un modèle suivi, lui, par git,
**`relecture_web/ccw_host.conf.example`**, documente le format et ne
contient que des lignes de commentaire (y compris la ligne `ccw_host`
elle-même, en exemple générique) — jamais d'identifiant ni d'adresse
réels. Pour configurer l'accès au PC fixe :

```
cp relecture_web/ccw_host.conf.example relecture_web/ccw_host.conf
# puis éditer ccw_host.conf : renseigner la ligne ccw_host (et
# éventuellement ccw_key) avec les vraies valeurs.
```

**Fichier absent (`ccw_host.conf`)** — installation neuve, ou après la
suppression du fichier réel devenue possible depuis que git ne le suit
plus : `charger_config_ccw()` dégrade proprement sur `None` (même
résultat qu'un fichier présent mais sans entrée `ccw_host`), sans
exception — voir le statut `"ccw_non_configure"` ci-dessous pour ce que
`relecture_web` affiche alors côté projet distant.

**Routage (`_lancer_git`)** — quand `repertoire` est distant,
`_lancer_git_distant` exécute la commande via
`ssh -i <ccw_key> -o ConnectTimeout=6 -o BatchMode=yes -o
StrictHostKeyChecking=accept-new <ccw_host> "git -C <repertoire> ..."`
plutôt qu'un `subprocess.run(["git", "-C", repertoire, ...])` local, en
conservant exactement la même interface de retour (code de retour,
stdout, stderr via un `subprocess.CompletedProcess`) — aucun appelant de
`git_info.py`/`app.py` n'a besoin de savoir si le projet qu'il manipule
est local ou distant.

- **`ConnectTimeout` court (6s)**, en plus du timeout applicatif déjà en
  place (`TIMEOUT_GIT`/`TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`) : un PC fixe
  éteint échoue vite plutôt que de bloquer — le serveur Flask de
  développement utilisé par `relecture_web` est mono-thread, une seule
  requête qui reste bloquée gèlerait l'outil entier pour Alain.
- **Échappement des chemins Windows** (`_quoter_argument_distant`) : un
  chemin comme `C:\CCW\Nom Projet` peut contenir des espaces ; chaque
  argument est entouré de guillemets doubles dès qu'un espace est
  présent, une forme acceptée aussi bien par `cmd.exe` (qui ne traite pas
  l'antislash comme caractère d'échappement) que par un shell POSIX
  (Git Bash) — le diagnostic de l'issue #91 n'ayant pas pu confirmer
  lequel des deux tourne réellement côté PC fixe.
- **Jamais de `&&` envoyé au shell distant** : une commande git est
  toujours envoyée seule à `_lancer_git_distant`. Les enchaînements
  visibles dans l'outil (ex. merge puis retour de branche dans
  `fusionner_worktree`, worktree remove puis branch -D) restent, côté
  exécution réelle, des appels `_lancer_git` séparés — jamais un seul
  `&&` shell — pour rester robuste au shell distant réel, quel qu'il
  soit. Les `&&` qu'Alain voit dans les commandes prévisualisées
  (paragraphe suivant) sont donc un résumé lisible de plusieurs commandes
  séquentielles, pas ce qui est littéralement envoyé au PC fixe.

**Commandes prévisualisées** — `commande_affichee(repertoire,
commande_git)` préfixe la commande git nue par la commande `ssh`
réellement utilisée (`ssh -i <clé> <ccw_host> <commande_git>`) pour un
projet distant, inchangée pour un projet local. Utilisée partout où
`git_info.py`/`app.py` construisaient déjà une commande à afficher avant
confirmation (push, merge, suppression de branche/worktree, revert,
sécurisation, finalisation de merge...) : Alain voit donc explicitement
qu'une action passera par le réseau avant de la confirmer, jamais
seulement la commande git nue comme s'il s'agissait d'un projet local.

**Statut « injoignable »** — `charger_etat_projet` (voir le paragraphe
suivant) teste la connectivité SSH (`tester_connectivite_ccw`, même
`ConnectTimeout` court) avant toute tentative de commande git sur un
projet distant, sur le modèle du test `os.path.isdir` déjà en place pour
les projets locaux. Un échec donne un statut `"injoignable"`, distinct
de `"introuvable"` (qui reste réservé aux projets locaux dont le dossier
n'existe pas) : `projet.html` affiche alors un message à la place du
contenu habituel, et `_projet_pret` (`app.py`) refuse toute action sur ce
projet avec le même message flash — même comportement dégradé que
l'existant (branches/diagnostics/conflits indisponibles), sans jamais
faire planter la page. Ce statut n'apparaît jamais sur la page d'accueil
ni dans la barre latérale (voir ci-dessous) : tant que la page du projet
distant n'a pas été ouverte, son statut y reste `"distant_a_charger"`,
jamais testé.

**Causes distinguées du statut « injoignable » (issue #111)** — un échec
de connexion SSH renvoie toujours le même code de sortie (255) quelle que
soit la cause : seul le texte d'erreur de `ssh` (en anglais, même sur un
système en français — vérifié pour « Connection refused », les autres
messages viennent du même programme) permet de distinguer les cas.
`tester_connectivite_ccw()` capture ce texte et le classe
(`_classer_echec_ssh_ccw`) en une des cinq catégories suivantes, dont les
libellés sont **alignés avec la procédure de réinstallation Windows du
PC fixe documentée par Bridge_Agent** (étape 3) — à ne renommer qu'après
accord avec Bridge_Agent :

| Libellé (`CCW_LIBELLES`) | Texte ssh reconnu | Message affiché |
|---|---|---|
| clé d'hôte modifiée | `Host key verification failed` | identité SSH changée (réinstallation probable) + commande `ssh-keygen -R <adresse>` à lancer sur le ThinkPad, `<adresse>` tirée de `ccw_host.conf` (jamais écrite en dur) |
| clé refusée | `Permission denied` + `publickey` | clé publique du ThinkPad non autorisée sur le PC fixe — à réinstaller selon la procédure CCW de Bridge_Agent |
| connexion refusée | `Connection refused` | serveur SSH du PC fixe non démarré ou n'écoutant pas |
| PC éteint ou adresse introuvable | `Connection timed out`, `No route to host`, `Network is unreachable`, `Could not resolve hostname`/`Temporary failure in name resolution`, ou dépassement du propre délai du test (`TimeoutExpired`) | message proche de l'ancien texte générique |
| cause non reconnue | tout le reste | message générique complété par la première ligne du texte d'erreur ssh, pour rester diagnosticable |

Premier contact avec un hôte jamais vu (clé d'hôte inconnue) : avec
`StrictHostKeyChecking=accept-new` (voir plus haut), ce cas est accepté
silencieusement par `ssh`, sans erreur — il ne se distingue donc jamais
en pratique d'une connexion réussie, et ne peut donc pas être confondu
avec « clé d'hôte modifiée » (qui, elle, suppose un hôte déjà connu dont
la clé a changé). La distinction demandée entre les deux n'avait donc pas
lieu d'être avec ces options.

`charger_etat_projet` stocke la catégorie et le message dans
`entree["ccw_categorie"]`/`entree["ccw_message"]` (absents si le projet
n'est pas au statut `"injoignable"`) ; `projet.html`, `index.html` et
`_projet_pret` (`app.py`, refus d'action) affichent ce message détaillé à
la place de l'ancien texte générique unique, avec repli sur ce dernier si
jamais absent. Une commande git distante qui échoue EN COURS D'ACTION
(pas seulement au chargement de la page) avec le même code de sortie 255
(donc un échec ssh, jamais git) est classée de la même façon par
`_lancer_git_distant`, qui préfixe alors le message de diagnostic au
texte brut de `ssh` (conservé pour le détail) avant de le renvoyer à
l'appelant.

**Statut « ccw_non_configure » (issue #110)** — `charger_etat_projet`
teste `charger_config_ccw()` AVANT `tester_connectivite_ccw()` : si
`ccw_host.conf` est absent, vide, ou sans entrée `ccw_host` (installation
neuve, ou fichier réel supprimé après cette issue), le statut devient
`"ccw_non_configure"` **sans tenter la moindre connexion SSH** — distinct
de `"injoignable"` (hôte configuré mais qui ne répond pas). `projet.html`
et `index.html` affichent alors un message explicite invitant à copier
`ccw_host.conf.example` vers `ccw_host.conf` puis à renseigner `ccw_host`,
plutôt que le message « PC fixe éteint ou injoignable », trompeur quand
aucune connexion n'a même été essayée ; `_projet_pret` (`app.py`) refuse
de même toute action sur ce projet avec ce message dédié
(`_MESSAGE_CCW_NON_CONFIGURE`).

### Chargement à la demande d'un projet distant (issue #109)

Avant cette issue, **chaque chargement de page** (accueil, barre
latérale, page d'un autre projet, actions diverses) appelait
`collect_etat_projets()`, qui chargeait TOUS les projets du tableau en
entier — y compris un test de connectivité SSH et des commandes git
distantes pour chaque ligne distante (section précédente, issue #94).
Avec l'apparition d'une ligne `<nom>_ccw` dans le tableau (issue #108),
cela ralentissait sensiblement *toutes* les pages de `relecture_web`,
même celles qui ne concernent aucun projet distant.

**`collect_etat_projets_legers()`** (`git_info.py`) remplace cet appel
pour toutes les pages qui n'ont pas besoin de l'état complet d'un projet
distant précis : les projets locaux sont chargés en entier (coût
purement local, déjà négligeable), les projets distants sont renvoyés
avec seulement leurs champs de base (nom/dépôt/répertoire/couleur,
champ `distant=True`) et le statut `"distant_a_charger"` — **aucun**
test de connectivité SSH, **aucune** commande git. C'est la fonction
que `_charger_projets()` (`app.py`) appelle désormais.

**`charger_etat_projet(projet, ...)`** (`git_info.py`) est le point
d'entrée unique qui charge un seul projet en entier, y compris le test
de connectivité SSH et les commandes git distantes s'il est distant —
réutilisé en interne par `collect_etat_projets_legers()` pour les
projets locaux (où il ne contacte jamais le réseau) et, côté `app.py`,
par `_charger_projet_complet(nom_projet)` pour charger à la demande
UN SEUL projet distant précis.

**Deux situations déclenchent ce chargement complet d'un projet
distant**, jamais plus :

1. L'ouverture de sa propre page (`projet_route`, `/projet/<nom_projet>`,
   qui appelle directement `_charger_projet_complet`).
2. Une action qui le concerne — toute route qui passe par
   `_trouver_projet`/`_projet_pret` (push, merge, suppression,
   sécurisation, revert...) résout désormais le projet visé via
   `_charger_projet_complet`, qui déclenche ce même chargement complet
   si ce projet est encore au statut `"distant_a_charger"`.

`_charger_projet_complet` mémoïse son résultat dans `g` par nom de
projet (durée d'une requête HTTP) : une même page ne déclenche ainsi
jamais plus d'un test de connectivité SSH, même si plusieurs morceaux de
cette page (route + panneau .gitignore + verrous actifs...) ont besoin
du même projet.

**`nettoyer_tous_les_projets_route`** (bouton « Nettoyer tous les
projets », issue #17) ignore déjà, sans code dédié, tout projet distant
: elle n'agit que sur les projets au statut `"ok"`, et un projet distant
reste au statut `"distant_a_charger"` tant que sa page n'a pas été
ouverte — donc jamais de contact SSH depuis ce bouton.

**« Nettoyer ce projet » sur un projet distant** (`nettoyer_projet_route`,
issue #68) est en revanche explicitement refusé (message flash clair),
et le bouton masqué côté template (`projet.html`) : cette action
nettoie les résumés déjà pushés dans `Relecture_Bridge/<dossier>/Non_Lu/`
— un dossier purement **local** au ThinkPad qui n'existe jamais pour un
clone Windows (aucun hook post-commit n'y est installé, voir
`installer.sh`). Avant l'issue #109, cette action restait silencieusement
sans effet sur un projet distant joignable (0 résumé supprimé, faute de
dossier local) plutôt que de signaler clairement qu'elle n'a pas de sens
ici.

**Page d'un projet distant** (`projet.html`) affiche désormais, en tête
de page, une indication discrète — « Projet du PC fixe (Windows), chemin
`C:\CCW\...`, accès par SSH » — qui explique pourquoi cette page
spécifique est plus lente à charger que les autres.

**Hors périmètre de cette issue** (suivi à prévoir) : la résolution de
conflit sur un fichier distant (`lire_conflits_fichier`,
`resoudre_bloc_conflit`, `resoudre_tous_blocs_conflit` — lecture/écriture
de fichier, pas des commandes git), l'exécution distante de
`scripts/fusionner_changelog.py` (déjà signalé hors du périmètre
`_lancer_git` par l'issue #93 : c'est un script Python, pas une commande
git), et l'équivalent Windows du badge « CCL travaille ici » (issue #88)
pour un worktree distant. Le mode LAN/externe d'exposition de
`relecture_web` lui-même (section « Lancement et modes réseau »
ci-dessus, issue #92) n'est pas non plus concerné par cette issue : elle
ne change rien à qui peut accéder à `relecture_web`, seulement à ce qu'il
peut atteindre une fois qu'on y accède.

### Lignes `<nom>_ccw` du tableau §2 (issue #108)

Côté Bridge_Agent, le tableau §2 de `BRIDGE_AGENT_DOC.md` peut contenir,
pour un projet buildé à la fois en local et pour Windows, une ligne
supplémentaire `<nom>_ccw` (premier cas : `rummikub_ccw`) dont la colonne
« Répertoire de travail CCL » contient le chemin Windows du clone sur le
PC fixe (`C:\CCW\<nom>`) — par opposition à la ligne `<nom>` ordinaire, qui
reste le clone local (ThinkPad, chemin POSIX). Ces lignes sont réservées à
la **relecture** de ce qui se passe sur le clone Windows (worktrees,
commits en attente, branches...) via le routage SSH de la section
ci-dessus : il n'y a ni watcher ni issue GitHub pour elles côté
Bridge_Agent, et `installer.sh` n'y installe pas de hook post-commit (voir
plus bas) — `relecture_web` les traite comme n'importe quel autre projet
distant, `fetch_projets`/`est_projet_distant` ne distinguant pas une ligne
`<nom>_ccw` d'une ligne `<nom>` ordinaire qui serait elle-même distante.

**Reconnaissance du worktree principal d'un projet distant**
(`worktree_est_principal`, `chemins_windows_egaux`) — comparer le chemin
du tableau (`C:\CCW\rummikub`, barres obliques inverses) à celui renvoyé
par `git worktree list` sur le PC fixe (`C:/CCW/rummikub`, barres obliques
normales, casse potentiellement différente) via `os.path.realpath` (comme
pour un projet local) les aurait jugés différents : le dossier principal
du clone Windows se serait alors affiché comme un worktree ordinaire, avec
des actions de fusion/suppression proposées là où elles n'ont aucun sens.
`worktree_est_principal(repertoire, chemin_worktree, projet_distant)`
bascule donc, pour un projet distant, sur une comparaison dédiée
(`chemins_windows_egaux`) qui ignore barres obliques (inverse vs normale),
casse, et une éventuelle barre finale — sans rien changer à la comparaison
`os.path.realpath` existante pour un projet local. Un autre worktree du
même clone (ex. un worktree dédié CCL) reste bien distingué du dossier
principal : la comparaison porte sur le chemin normalisé dans son
intégralité, jamais sur un simple préfixe.

**Résolution de conflit sur un projet distant : refus explicite** — reste
hors périmètre (voir paragraphe ci-dessus), mais la page Conflit
(`conflit_fichier_route`) et les deux actions de résolution
(`traiter_bloc_conflit_route`, `traiter_tous_blocs_conflit_route`) le
détectent maintenant explicitement (`est_projet_distant`) et affichent
« ❌ Résolution de conflit non disponible pour un projet distant (PC fixe
CCW). » avant toute tentative de lecture/écriture — plutôt que de laisser
`lire_conflits_fichier`/`resoudre_bloc_conflit` tenter d'ouvrir un chemin
local inventé (résultat d'un `os.path.join` sur un chemin Windows, sans
rapport avec le fichier réel du PC fixe) et n'afficher qu'un message
d'erreur système confus. `retraiter_fichier_conflit_route` n'a pas besoin
de ce garde-fou : elle ne fait qu'un `git checkout --conflict=merge`,
déjà correctement routé par `_lancer_git`.

**Fusion du changelog sur un projet distant : bouton « Fusionner le
changelog » (issue #114, remplace le refus explicite de l'issue #108)** —
`fusionner_worktree` (bouton « Fusionner ») reste utilisable sur un
worktree distant (le `git merge` lui-même est routé par `_lancer_git`),
mais l'étape suivante, l'intégration du CHANGELOG, ne peut pas s'appuyer
sur `fusionner_changelog_worktree` local (`os.listdir`,
`subprocess.run(["python3", "scripts/fusionner_changelog.py", ...])`
visent tous deux le filesystem LOCAL de ce process — inutilisables sur un
chemin Windows). Jusqu'à l'issue #108, ce cas était un refus explicite
inconditionnel après chaque merge ; depuis #114, un bouton dédié permet de
le faire réellement, sans quitter la page :

- **Détection** (`detecter_changelogs_a_fusionner`, appelée dans
  `charger_etat_projet` pour un projet distant uniquement, à CHAQUE
  ouverture de la page du projet — pas seulement juste après un merge) :
  `git ls-tree --name-only HEAD` (routé en SSH comme toute commande du
  module), filtré côté Python sur le motif `CHANGELOG-<N>.md`, jamais un
  `os.listdir` local ni un pathspec glob confié à un shell distant dont
  l'implémentation réelle (PowerShell, cmd.exe, Git Bash) n'est pas
  confirmée. Présence détectée -> bouton « Fusionner le changelog (#N) »
  affiché (plusieurs numéros possibles) sous le bandeau « 💻 Projet du PC
  fixe » ; rien détecté -> pas de bouton. Le message après un merge réussi
  (`fusionner_changelog_worktree`, toujours appelée juste après le merge)
  utilise maintenant cette même détection : s'il n'y a réellement rien à
  fusionner, elle ne signale plus rien (avant #114, le refus apparaissait
  systématiquement, qu'il y ait ou non un `CHANGELOG-<N>.md`) ; sinon, le
  message `⚠️` invite à utiliser le bouton plutôt qu'à « fusionner
  manuellement ».

- **Confirmation** : même niveau « légère » que les autres actions de
  l'outil (`ouvrirConfirmation({variant: "legere", ...})`), affichant les
  commandes réellement exécutées (ssh/scp/git), précalculées SANS connexion
  SSH par `commandes_previsualisees_fusion_changelog_distant` — l'
  interpréteur y est affiché comme « python » à titre représentatif, le
  repli éventuel vers « py » n'étant déterminé qu'à l'exécution.

- **Action** (`fusionner_changelog_distant`, route
  `POST /projet/<nom_projet>/fusionner-changelog-distant`) :
  1. Garde-fous, AVANT toute commande SSH/SCP : `repertoire` doit être sur
     sa branche principale (la branche cible de comparaison configurée
     pour ce projet, voir `get_branche_cible_comparaison` — **sans entrée
     explicite dans `branches_cibles.conf` pour ce projet, ce repli vaut
     par construction la branche actuellement extraite : seule une HEAD
     détachée est alors détectable, pas un changement de branche réel** —
     limitation connue, cohérente avec le fait que ce dépôt ne mémorise
     nulle part ailleurs « la » branche par défaut d'un projet sans
     configuration explicite) ; au moins un `CHANGELOG-<N>.md` détecté ;
     `git status` ne signalant AUCUNE modification en dehors de
     `CHANGELOG.md` et des `CHANGELOG-<N>.md` détectés (les exclusions
     locales `configs/`/`logs/` déjà posées sur les clones via
     `.git/info/exclude` s'appliquent d'elles-mêmes, `git status` les
     ignorant nativement).
  2. Interpréteur Python disponible sur le PC fixe (« python », repli
     « py » — `_detecter_interpreteur_python_ccw`) : précondition de tout
     le reste, vérifiée AVANT la moindre copie ; absent des deux ->
     erreur explicite, rien n'est modifié.
  3. Copie de `scripts/fusionner_changelog.py` (toujours celui de CE
     dépôt, jamais une copie du projet cible — même raison que pour la
     fusion locale) via `scp`, dans un dossier temporaire frère des
     dossiers de projets (`C:\CCW\_relecture_bridge_tmp_fusion_changelog`,
     créé au besoin par le même interpréteur Python détecté, JAMAIS à
     l'intérieur d'un worktree suivi par git — sinon la copie apparaîtrait
     comme fichier non suivi et serait prise à tort pour « une autre
     modification » par le garde-fou ci-dessus).
  4. Lancement du script sur `repertoire` ; échec à mi-chemin -> rien
     n'est ajouté à l'index ni committé, la commande de retour en arrière
     éventuellement utile est affichée dans le message d'erreur, jamais
     lancée automatiquement.
  5. `git add` puis `git commit` limités à `CHANGELOG.md` et aux
     `CHANGELOG-<N>.md` traités (même portée stricte que la fusion
     locale), message `chore: fusionne CHANGELOG-<N>.md dans CHANGELOG.md
     (auto)` — jamais `git push`.
  6. Affichage du commit créé et des trois derniers commits
     (`git log -3 --oneline`).
  7. Nettoyage SYSTÉMATIQUE de la copie temporaire du script sur le PC
     fixe (bloc `try`/`finally`), succès, échec (`returncode`) OU
     exception imprévue (voir le point suivant, issue #115).
  8. **Toute exception imprévue (issue #115)** pendant la préparation ou
     l'exécution (y compris un `subprocess.TimeoutExpired` sur n'importe
     quelle étape distante) est attrapée par un `try`/`except` englobant
     tout le corps de la fonction, pour ne jamais laisser remonter de page
     d'erreur serveur jusqu'à la route Flask. Le message produit précise
     l'étape atteinte (donc ce qui a pu être fait côté PC fixe — script
     lancé ou non, fichiers modifiés/supprimés dans le dossier de travail,
     jamais de commit) et la commande de retour en arrière, affichée mais
     jamais lancée par l'outil — en particulier, si l'exception survient
     APRÈS l'exécution du script mais AVANT le commit, le message le dit
     explicitement.

  Toute erreur SSH (code 255) réutilise le classement par catégorie de
  l'issue #111 (`_classer_echec_ssh_ccw`/`_message_echec_ssh_ccw`), via le
  même point de factorisation (`_classer_resultat_ssh_255`) que
  `_lancer_git_distant`.

- **Fins de ligne** (le point le plus important de l'issue #114) —
  `scripts/fusionner_changelog.py` ouvrait et réécrivait `CHANGELOG.md` en
  mode texte universel par défaut (`Path.read_text`/`write_text`) : sans
  effet visible tant que le script tournait sur le ThinkPad (Linux,
  `os.linesep` = `\n`), mais sur le PC fixe (`os.linesep` = `\r\n`), un
  `CHANGELOG.md` resté entièrement en LF se serait retrouvé entièrement
  converti en CRLF après un simple ajout d'entrée — tout le fichier serait
  alors apparu modifié dans le commit (le défaut déjà corrigé par #107
  côté résolution de conflit). Corrigé en reprenant le même principe que
  #107 (`_fin_de_ligne_dominante`/`_normaliser_fin_de_ligne`, dupliqués
  dans le script plutôt qu'importés : il est copié seul sur le PC fixe,
  sans le reste de `relecture_web`) : lecture/écriture avec `newline=""`
  (aucune traduction), contenu déjà présent dans `CHANGELOG.md` jamais
  retouché, seul le texte de chaque `CHANGELOG-<N>.md` inséré est ramené à
  la fin de ligne dominante du fichier cible (LF, CRLF, ou mixte — la
  dominante est alors celle qui l'est le plus).

**Accents Windows : décodage tolérant des sorties du PC fixe et encodage
forcé du script (issue #115, suite de #114)** — premier usage réel du
bouton a fait planter la page (« Internal Server Error ») avec une
`UnicodeDecodeError` sur l'octet `0xe9` : un programme Windows dont la
sortie est redirigée (ssh, scp, ou le script lancé à distance) n'écrit PAS
en UTF-8 par défaut mais dans l'encodage de la console Windows (`0xe9` =
« é » en cp1252) — `subprocess.run(text=True)` décode pourtant selon
l'encodage préféré du process LOCAL (UTF-8 sur ce ThinkPad Linux), ce qui
lève l'exception avant même d'atteindre le code appelant. Deux corrections
distinctes :

- **Décodage tolérant** (`_decoder_sortie_distante`/`_run_ssh_scp`) —
  TOUTE commande ssh/scp qui touche le PC fixe (commande git distante via
  `_lancer_git_distant`, test de connectivité `tester_connectivite_ccw`,
  détection de l'interpréteur Python, création du dossier temporaire,
  copie puis lancement du script de fusion, nettoyage de la copie) passe
  maintenant par `_run_ssh_scp`, qui capture stdout/stderr en octets bruts
  puis les décode en essayant UTF-8, puis cp1252 (encodage de console
  Windows le plus courant), puis cp850 (console « OEM », parfois utilisée
  selon la configuration régionale) — cp850 associe un caractère à chacun
  des 256 octets possibles, donc ne peut jamais lever cette exception : un
  des trois réussit toujours. Nuance : cp1252 ne lève `UnicodeDecodeError`
  que sur 5 octets précis (non définis dans cette page de code) ; un texte
  réellement écrit en cp850 qui n'en contient aucun est donc décodé sans
  exception par le repli cp1252, potentiellement avec un caractère
  différent de l'original — l'objectif (ne jamais planter) est rempli dans
  tous les cas, la reconstruction exacte ne l'est que si le texte est
  vraiment en cp1252, ou contient un de ces 5 octets.
- **UTF-8 forcé côté PC fixe** — le lancement du script de fusion est
  désormais fait avec l'option d'interpréteur `-X utf8` (`python -X utf8
  scripts/fusionner_changelog.py --repo ...`), pour que ses messages
  accentués (`print()`) soient écrits en UTF-8 plutôt que dans l'encodage
  de console par défaut, quel qu'il soit. `scripts/fusionner_changelog.py`
  lui-même précisait déjà `encoding="utf-8"` à chaque lecture/écriture de
  fichier (`CHANGELOG.md` et chaque `CHANGELOG-<N>.md`) depuis la
  correction des fins de ligne de l'issue #114 — vérifié à nouveau pour
  l'issue #115, aucun defaut trouvé là, donc inchangé : le contenu des
  fichiers n'a jamais dépendu de l'encodage de console, seul l'affichage
  des messages de progression pouvait planter.

**`installer.sh` et les chemins Windows** — pour une ligne dont le
répertoire est un chemin Windows (même motif que `MOTIF_CHEMIN_WINDOWS`
côté `git_info.py`), le script affiche désormais « ℹ Clone Windows
distant (PC fixe CCW) — pas de hook installé par ce script : ... »,
distinct du message « ⚠ Ignoré (pas un dépôt git) : ... » réservé à un
vrai dossier local sans `.git` — ce n'est pas un dépôt cassé, mais un
clone volontairement hors du champ de ce script (qui n'a aucun accès
filesystem au PC fixe). Comportement inchangé pour toute ligne à chemin
Linux.

## 12. Comment interpréter une capture ou un export de `relecture_web`

Si Alain montre une capture d'écran ou un texte copié depuis
`relecture_web` dans une conversation Claude Chat d'un autre projet
(ex. `alchess`) :

1. **Un badge de cas A-F n'est pas un verdict humain final** — c'est le
   résultat d'une comparaison de contenu (`git cherry`/`patch-id`)
   contre une branche cible précise (visible dans le sous-titre de la
   section diagnostic, ou absente si non configurée — cas E). Vérifier
   quelle branche cible est concernée avant d'interpréter un badge.
2. **Une branche `recuperation-<hash>`** n'est pas un artefact de
   Bridge_Agent ni un état anormal — c'est une sécurisation défensive
   volontaire d'un commit orphelin (section 6), qui n'a jamais de
   worktree et ne doit jamais être traitée comme une branche de travail
   ordinaire.
3. **Un texte « Rapport »** (section 5) copié depuis l'outil contient
   déjà toute l'information disponible côté `relecture_web` pour ce
   commit (résumé, sortie `git cherry`, branches locales/distantes,
   autres orphelins en attente) — reconstruire ce contexte à la main à
   partir de zéro est redondant ; le format du rapport lui-même indique
   ce qui a déjà été vérifié automatiquement et ce qui reste à
   trancher humainement.
4. **Un diff affiché sur la page Comparer** entre un commit orphelin et
   son commit correspondant dans la branche cible : un diff vide
   confirme un doublon strict ; un diff non vide signale un contenu
   *retouché* entre les deux versions, à examiner precisément sur ce
   diff plutôt que sur les deux commits pris séparément.
5. Ce document décrit l'état du code au moment de sa rédaction — en cas
   de doute sur un comportement précis (un badge inattendu, une action
   absente de ce document), le code source fait foi :
   `relecture_web/app.py` (routes et actions) et
   `relecture_web/git_info.py` (logique git, diagnostic A-F) dans le
   dépôt `relecture_bridge`.

## 13. Push en arrière-plan pour les projets équipés d'un crochet `pre-push` (issue #122)

Contexte : Alain prévoit d'installer, projet par projet, un crochet git
`pre-push` qui lance une suite de tests (environ 80 à 90 secondes) avant
chaque push et annule le push si un test échoue. Pour un tel projet, le
push synchrone décrit à la ligne « Push » de la section 9 (timeout de
120s, `TIMEOUT_GIT_LONG`) deviendrait peu praticable — un push proche ou
au-delà de 120s bloquerait la page, et le message « n'a PAS abouti »
pourrait même être faux (même piège que l'issue #66, mais plus probable
avec un crochet qui allonge franchement chaque push). Cette issue pose le
moteur et l'affichage sur la page du projet ; l'affichage sur les AUTRES
pages (pastille, panneau « Attention Refus », fenêtre de résultat) est
traité par l'issue #123, voir la fin de cette section. L'issue #127
ajoute, pour un push abouti seulement, l'affichage de la fin de sa sortie
(repliable) et un filtrage des secrets avant tout stockage — voir les
deux derniers paragraphes avant « Pas de contournement ».

**Détection du crochet (`git_info.chemin_hook_pre_push`/
`projet_equipe_hook_pre_push`) :** un projet est « équipé » si un crochet
`pre-push` EXÉCUTABLE existe à l'emplacement résolu par git lui-même
(`git rev-parse --git-path hooks/pre-push`, exécuté dans le répertoire du
projet) — respecte donc un `core.hooksPath` personnalisé, et fonctionne
aussi bien pour le dossier principal d'un dépôt que pour un de ses
worktrees (le crochet vit toujours dans le dépôt commun, jamais dupliqué
par worktree ; git renvoie alors un chemin absolu directement). Un fichier
présent mais non exécutable (`chmod +x` oublié) compte comme NON équipé,
exactement comme git lui-même l'ignorerait. **Jamais pour un projet
distant du PC fixe (`_ccw`, section 11) :** `projet_equipe_hook_pre_push`
retourne toujours False sans la moindre tentative de connexion SSH — le
push en arrière-plan de cette issue est strictement local, section 11
n'est pas affectée. Pour TOUT projet NON équipé, le comportement reste
l'exact comportement synchrone décrit à la ligne « Push » de la section 9
— aucun changement.

**Mode arrière-plan (projets équipés seulement, `push_arriere_plan.py`) :**
après la confirmation forte habituelle (dont le texte précise, pour un
projet équipé, qu'un crochet de tests va s'exécuter et que cela peut
durer plusieurs minutes), la requête revient tout de suite — la fenêtre
superposée « Push en cours... Ns » de l'issue #49 ne s'affiche plus pour
ce bouton (elle n'aurait plus de sens, rien ne reste bloqué). Le push
s'exécute dans un thread du serveur, avec le process git lancé dans son
propre groupe de processus (`start_new_session=True`) — toutes les
branches cochées sont poussées par UN SEUL `git push <remote> <branche1>
<branche2>...` (le crochet ne tourne qu'une fois), le résultat réel étant
de toute façon établi branche par branche après coup (voir ci-dessous),
indépendamment du code de sortie global de la commande. Délai propre à ce
module, `push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN` (10 minutes),
distinct de `TIMEOUT_GIT_LONG` : à son dépassement, tout le groupe de
processus est tué (`os.killpg`, pas seulement le process git — les tests
du crochet, enfants du même groupe, continueraient sinon à tourner et
pourraient chevaucher le push suivant), puis l'état réel est revérifié
par branche via `git_info.verifier_push_apres_timeout` (même fonction que
l'issue #66, ré-utilisée ici : poussé / non abouti / indéterminé).

**État global du projet** (`push_arriere_plan._etat_global`), à partir du
résultat RÉEL par branche, jamais de la seule supposition du code de
sortie ou du dépassement de délai :
- `en_cours` — le thread tourne encore.
- `pousse` — code de sortie nul ET toutes les branches confirmées
  poussées (`ls-remote` identique au commit local).
- `refuse` — au moins une branche confirmée NON poussée, sans dépassement
  de délai (le crochet ou git a rejeté le push).
- `interrompu` — le groupe de processus a été tué par ce module (délai
  dépassé) : le process n'est jamais allé jusqu'au bout de ses propres
  termes, sa sortie est nécessairement incomplète, même si le résultat
  réel révèle que le push a malgré tout abouti juste avant le `killpg`
  (même piège que l'issue #66) — le détail par branche reste consultable
  dans le panneau. Même état pour une entrée restée « en_cours » après un
  redémarrage de relecture_web (voir ci-dessous).
- `indetermine` — ni l'un ni l'autre n'a pu être établi (échec de la
  vérification réseau elle-même).

**Un seul push à la fois par projet, projet verrouillé pendant ce
temps :** l'état persistant (voir ci-dessous) sert lui-même de verrou —
un projet est considéré verrouillé tant que son entrée a `etat ==
"en_cours"` (`push_arriere_plan.projet_verrouille_par_push`), relu depuis
le fichier à chaque requête, jamais mémorisé en mémoire process (sauf la
durée de vie du process lui-même, voir le redémarrage ci-dessous). Un
second push sur le même projet est refusé par un message clair
(`demarrer_push_arriere_plan`, vérification et écriture de l'entrée sous
le même verrou d'écriture pour éviter toute course entre deux requêtes
simultanées). Pendant un push, toute AUTRE action qui modifie le dépôt
git de CE projet est refusée par le même message (« Push en cours sur ce
projet ») via le décorateur `app.refuse_si_push_en_cours`, appliqué à
Merger, Merger et supprimer, Finaliser le merge, Supprimer (fusionnées ou
forcées), Rejeter (simple ou forcé), Supprimer la/les branche(s) de
récupération, Sécuriser (un commit ou tous), Revert, fusion du changelog
distant, les trois actions du panneau `.gitignore`, et la résolution de
conflit (Traiter ce bloc/tous les blocs, Retraiter le fichier en
conflit) — en clair, toute route qui écrit dans le dépôt git de ce
projet. Les actions de lecture (Comparer, Générer rapport, Comparer la
sélection, panneaux de lecture...) et TOUS LES AUTRES PROJETS ne sont
jamais concernés — revérifié depuis l'état réel à chaque requête, jamais
mémorisé par avance. Le blocage vise un état stable pendant les tests ;
il pourra être assoupli plus tard si le crochet teste une copie du commit
poussé plutôt que le dépôt réel.

**État persistant** (`push_arriere_plan.CHEMIN_ETAT_PUSH`,
`relecture_web/push_arriere_plan_etat.json`, fichier local ignoré par git
comme `changelog_fusion.log`/`decisions_fichiers_ignores.log`/
`bruit_projets.log`) : un objet JSON, une entrée par projet, avec `etat`
(une des cinq valeurs ci-dessus), `branches` (liste), `repertoire`,
`debut`/`fin` (horodatages ISO), `sortie` (fin de la sortie combinée du
crochet et de git, **filtrée des secrets les plus courants puis**
plafonnée à `MAX_LIGNES_SORTIE_PUSH` = 60 lignes ET
`MAX_CARACTERES_SORTIE_PUSH` = 20000 caractères — voir « Filtrage des
secrets » plus bas), `vu` (bool, voir « Vu » ci-dessous), `masque` (bool,
optionnel, issue #127 — voir « Affichage sur la page du projet » plus
bas, sans effet ailleurs), `pid` (celui du process git, donc du groupe de
processus, tant qu'il tourne — None sinon), et `resultats` (détail par
branche, même forme que `git_info.verifier_push_apres_timeout`). Écrit au
lancement (`etat = "en_cours"`, qui repart toujours sans `masque`) et à la
fin du thread ; relu à chaque affichage de la page projet
(`push_arriere_plan.entree_affichable`), jamais mis en cache. Écriture
atomique (fichier temporaire puis `os.replace`), pour qu'un lecteur
concurrent ne voie jamais un JSON à moitié écrit. **Fichier absent ou
illisible (JSON corrompu, ou contenu qui n'est pas un objet) : traité
comme vide, sans erreur affichée** — dégradation systématique, même
principe que `bruit_projets.log`/`decisions_fichiers_ignores.log`. Un
fichier existant d'avant l'issue #127 (sans le champ `masque`) continue à
s'afficher sans erreur — ce champ n'est jamais obligatoire. **Une écriture
impossible (dossier en lecture seule, disque plein...) ne bloque jamais le
push lui-même** (garde-fou explicite de l'issue) : le push démarre malgré
tout, avec un message flash d'avertissement signalant que son résultat ne
sera pas affiché.

**Redémarrage de relecture_web pendant un push** (`push_arriere_plan.
reconcilier_au_demarrage`, appelée une seule fois juste avant
`app.run(...)`, jamais à chaque requête) : une entrée restée `en_cours`
ne peut provenir que d'un thread du process PRÉCÉDENT, sauf si le process
git lui-même — détaché dans son propre groupe, donc jamais tué par
l'arrêt du serveur — tourne encore en orphelin (`pid` toujours vivant,
`git_info._pid_vivant`) : dans ce seul cas, l'entrée est laissée telle
quelle (toujours verrouillée), faute de pouvoir savoir quand il se
terminera. Sinon, l'entrée est marquée `interrompu` puis revérifiée par
branche (même fonction que pour un dépassement de délai, résultat réel
noté dans `resultats`).

**Affichage sur la page du projet (panneau « Dernier push »,
`projet.html`) :** pour tout état AUTRE que `pousse`, n'apparaît que dans
deux cas (issue #125, `push_arriere_plan.entree_affichable`, même règle
que l'affichage global ci-dessous) — un push en cours (`etat ==
"en_cours"`), ou un résultat pas encore acquitté (`vu` faux : refusé,
interrompu, indéterminé). Montre l'état avec son libellé (⏳ En cours / ❌
Refusé / ⚠️ Interrompu / ❓ Indéterminé), les branches concernées, les
horaires de début/fin, le détail par branche quand disponible, et — pour
un refus/interrompu/indéterminé — la fin de la sortie du crochet et de
git directement (`<pre>`, jamais repliée), affichage **inchangé par
l'issue #127**. Pendant l'exécution : un compteur de secondes écoulées
calculé côté navigateur (`Date.now()` moins l'horodatage de début) et un
rafraîchissement automatique léger — un simple rechargement de la page
toutes les 4 secondes, jamais d'appel réseau supplémentaire ni d'API
JSON, cohérent avec le reste de cette page — pour relire l'état réel une
fois le push terminé ; rien de plus n'est affiché pendant cette phase. Le
bouton « Vu » (`POST /projet/<nom>/push/vu`, `push_arriere_plan.
marquer_vu` — ne change que le champ `vu`, jamais `etat` : un refus déjà
affiché reste un refus) fait disparaître le panneau de cette page dès le
prochain affichage ; l'entrée elle-même reste dans le fichier d'état (non
purgée), mais n'est plus signalée nulle part. Un résultat non acquitté
n'est jamais masqué par un push réussi survenu entre temps par un autre
chemin (ligne de commande, autre worktree) : seule l'entrée elle-même,
propre à `push_arriere_plan`, détermine l'affichage.

**Pour un push abouti (`etat == "pousse"`, issue #127, points 1 et 2) :**
`vu` est mis à `True` automatiquement dès la fin du thread, comme avant
cette issue — ce qui suffit à ce qu'un succès ne soit plus jamais signalé
dans la barre latérale, la route de sondage ou la fenêtre globale (#123,
tous trois basés sur `etats_a_signaler`/`vu`, voir plus bas). Mais SUR
CETTE PAGE SEULEMENT, le panneau reste affiché malgré ce `vu=True`, avec
la fin de la sortie (donc les lignes de comptage que le crochet imprime)
dans un bloc repliable « Sortie du push (tests du crochet) », fermé par
défaut (`<details>` sans attribut `open`) — absent si la sortie est vide.
C'est une exception délibérée au principe « un résultat acquitté
disparaît du panneau » : `push_arriere_plan.entree_affichable` retourne
l'entrée telle quelle pour tout état autre que `pousse`, mais la masque
(retourne `None`, donc aucun panneau) si `etat == "pousse"` ET que le
champ dédié `masque` est vrai. Ce champ est SÉPARÉ de `vu` précisément
pour cette raison : poser `vu=True` (ce que fait déjà le moteur à la
réussite, et ce que referait sans effet un appel à l'ancien bouton/route
« Vu ») ne masque jamais ce panneau — seul un clic explicite sur le
nouveau bouton « Masquer » (`POST /projet/<nom>/push/masquer`,
`push_arriere_plan.marquer_masque`, qui pose `masque=True` et ne touche à
rien d'autre) le fait disparaître. Le panneau réapparaît normalement au
push suivant : `demarrer_push_arriere_plan` remplace entièrement l'entrée
par une nouvelle, sans le champ `masque`. Comme `masque` n'entre dans
aucun des champs exposés par `etats_a_signaler` (`_CHAMPS_ETAT_PUBLIC`) et
n'est lu par aucune autre route ni aucun autre template, cette
conservation n'a AUCUN effet ailleurs : rien dans la barre latérale, pas
de réapparition de la fenêtre verte « Poussé » (#123, purement
transitoire, jamais rejouée), pas de préfixe persistant dans le titre de
l'onglet.

**Pas de contournement :** aucun bouton ni option `--no-verify` n'est
exposé dans l'interface — contourner les tests reste possible dans un
terminal, volontairement, mais jamais depuis `relecture_web`.

**Filtrage des secrets (issue #127, point 4,
`push_arriere_plan._filtrer_secrets`) :** appliqué par `_tronquer_sortie`
— donc avant toute troncature, et donc avant tout affichage ou écriture
dans l'état persistant, succès comme échecs. Reconnaît et remplace par un
marqueur neutre (`***secret masqué***`), sans toucher au reste de la
ligne, trois formes courantes : les identifiants (utilisateur, et mot de
passe/jeton s'il y en a un) dans une URL de dépôt
(`https://utilisateur:jeton@hôte/...`) ; les jetons GitHub reconnaissables
par leur préfixe (classiques `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`, ou
fine-grained `github_pat_`) ; la valeur d'une ligne `Authorization:` (en
entier, quel que soit son schéma — `Bearer`, `Basic`, ou autre). **Limite
assumée, documentée volontairement ici plutôt que cachée :** ce filtrage
ne peut PAS deviner un secret de forme arbitraire qu'un test ou le crochet
imprimerait sans l'un de ces formats reconnaissables (mot de passe en
clair sans contexte, clé API maison, variable d'environnement affichée
brute...). C'est un filet de sécurité en plus, jamais une garantie — la
vraie protection reste que le crochet et les tests n'impriment eux-mêmes
aucun secret dans leur sortie.

**Garde-fous :** les projets du PC fixe (`_ccw`) et tout projet sans
crochet `pre-push` exécutable : aucun changement de comportement.
`relecture_web` n'installe, ne modifie ni ne supprime jamais aucun
crochet, et ne touche à aucun fichier de Bridge_Agent ou d'un autre
projet. Même discipline de confirmation qu'avant cette issue (confirmation
forte avant le push, quitte la machine) — le texte de cette confirmation
précise simplement, en plus, qu'un crochet de tests va s'exécuter.

### Nettoyage automatique des résumés déjà pushés après un push (issue #128)

Jusqu'ici, après un push abouti, les résumés (`Non_Lu/`) des commits
désormais présents sur GitHub restaient affichés tant qu'Alain ne cliquait
pas explicitement sur « Nettoyer ce projet » (section 9, issue #68) — un
geste de plus, facile à oublier, pendant lequel le compteur de résumés en
attente restait faux. Les deux chemins de push ci-dessus déclenchent
désormais ce nettoyage automatiquement, SANS AUCUNE nouvelle
implémentation : les deux réutilisent littéralement
`resumes_info.nettoyer_resumes_pousses` (donc
`lister_fichiers_resumes_pushes`/`get_commit_est_pushe`), exactement la
fonction qu'appelle déjà « Nettoyer ce projet »/« Nettoyer tous les
projets » — même garde-fou, aucune suppression d'un résumé dont le commit
n'est pas encore un ancêtre d'une branche distante.

**Push synchrone (projet NON équipé d'un crochet pre-push,
`app.pousser_branches_route`) :** le nettoyage est tenté juste après la
confirmation du résultat de CHAQUE branche poussée avec succès (push
direct confirmé `ok`, ou vérification après dépassement de délai confirmée
`ok` — issue #66) — jamais pour une branche en échec, ni pour une
vérification restée `False`/indéterminée. Le nombre de résumés
effectivement supprimés est ajouté au message flash de succès existant
(`_suffixe_nettoyage_auto_apres_push`), jamais un message séparé.

**Push en arrière-plan (projet équipé d'un crochet pre-push,
`push_arriere_plan._executer_push_arriere_plan`) :** le nettoyage est
tenté une seule fois à la toute fin du thread, et seulement si l'état
global final est `pousse` — jamais pour `refuse`, `interrompu` ou
`indetermine`. Contrairement au chemin synchrone, **aucun message n'est
ajouté nulle part** et **aucun champ n'est ajouté à l'entrée d'état
persistante** : ce nettoyage n'a par construction aucun effet sur
l'affichage du panneau « Dernier push » ni sur l'acquittement (`vu`),
déjà posés juste avant par l'écriture habituelle de l'entrée.

**Jamais pour un projet distant du PC fixe CCW**, sur les deux chemins :
exactement comme le bouton « Nettoyer ce projet » (section 9), ce dossier
`Non_Lu/` est purement local au ThinkPad et n'existe jamais pour un clone
Windows. Le push en arrière-plan ne concerne de toute façon jamais un
projet distant (`projet_equipe_hook_pre_push` retourne toujours False pour
lui, voir plus haut) ; côté synchrone, le guard est explicite
(`projet.get("distant")`), avant même de tenter une lecture locale.

**Garde-fou sur les erreurs de nettoyage (dans les deux chemins) :** une
exception levée par `nettoyer_resumes_pousses` (dossier illisible,
permissions...) est systématiquement absorbée — elle ne remonte jamais
dans le message flash ni ne fait échouer la requête côté synchrone, et ne
modifie jamais l'état persistant ni ne fait planter le thread côté
arrière-plan. Dans les deux cas, le résultat du push lui-même reste
rapporté exactement comme si le nettoyage n'avait pas été tenté.

Les boutons « Nettoyer ce projet » et « Nettoyer tous les projets »
restent entièrement inchangés par cette issue : ce déclenchement
automatique ne couvre que les pushs faits depuis cette interface — un push
fait directement dans un terminal (hors `relecture_web`) continue de
laisser les résumés en place jusqu'au prochain clic sur l'un de ces deux
boutons.

### Affichage global sur toutes les pages (issue #123)

Pensé pour qu'Alain, parti travailler sur un autre projet pendant qu'un
push tourne en arrière-plan, soit prévenu du résultat où qu'il se trouve
dans `relecture_web`, sans dépendre d'une notification externe. Purement
de l'affichage : aucune action git, et le moteur/l'état persistant décrits
plus haut ne sont pas modifiés, hors l'indicateur `vu` déjà prévu.

**Route de sondage (`GET /push/etat`, `app.etat_push_route`) :** réponse
JSON `{"projets": {...}}`, un sous-ensemble de l'état persistant construit
par `push_arriere_plan.etats_a_signaler` — un projet y figure seulement si
son push est en cours (`etat == "en_cours"`) ou si son dernier résultat
n'a pas encore été acquitté (`vu` faux) ; jamais `repertoire` ni `pid`
(propres à cette machine, sans intérêt pour l'affichage). Un projet jamais
poussé en arrière-plan, ou dont le dernier résultat est déjà acquitté,
n'y figure pas du tout. Même filtre réutilisé côté serveur par
`app.injecter_barre_laterale` pour le premier rendu de chaque page, avant
même que le JS n'ait eu le temps de sonder quoi que ce soit.

**Sondage côté navigateur (`base.html`) :** toutes les pages interrogent
cette route en JS toutes les 5 secondes (20 secondes quand l'onglet est
caché, `document.hidden` — ressondé immédiatement dès qu'il redevient
visible), dès le chargement de la page sans attendre le premier
intervalle. Une erreur de sondage (réseau, HTTP) est ignorée
silencieusement ; le prochain sondage est planifié normalement, sans
accumulation ni backoff particulier.

**Barre latérale :** voir la section 2 pour le détail des deux
indicateurs (pastille animée pendant le push, panneau rouge/orange une
fois terminé tant que non acquitté).

**Fenêtre de résultat globale (`#modal-resultat-push`, distincte de
`#modal-confirmation` — jamais réutilisée pour autre chose) :** s'affiche
sur la page où se trouve Alain, quel que soit le projet concerné. Verte
« ✅ Poussé » avec un simple bouton « Fermer » dès que le sondage détecte
qu'une entrée vue « en_cours » lors du sondage précédent a disparu de la
réponse (seul un push abouti efface ainsi son entrée, `vu` étant mis à
True automatiquement par le moteur — jamais pour un refus, interrompu ou
indéterminé) — purement transitoire, jamais rejouée au rechargement.
Rouge « ❌ Refusé » avec la fin de la sortie des tests et un bouton « Vu »
(appel AJAX à `POST /push/<nom_projet>/vu`, `app.
acquitter_push_global_route` — même action que le bouton « Vu » de la page
projet, sans redirection) dès qu'un refus non acquitté est détecté ;
réapparaît à chaque chargement de page tant qu'il n'est pas acquitté,
disparaît de partout (y compris les autres onglets déjà ouverts) dès que
`vu` passe à True, au plus tard à leur sondage suivant. Plusieurs
résultats en attente s'affichent l'un après l'autre (file côté JS). Si
`#modal-confirmation` est ouverte au moment où un résultat devrait
s'afficher, il attend sa fermeture (Annuler ou Échap) — jamais affiché
par-dessus elle, pour qu'Alain ne valide jamais un résultat de push par
réflexe en croyant répondre à une confirmation d'action.

**Titre de l'onglet :** tant qu'un résultat n'est pas acquitté (refus,
interrompu, indéterminé — ou qu'une fenêtre verte de succès est en attente
d'être fermée), le titre de l'onglet porte un préfixe `❌ ` (prioritaire)
ou `✅ `, restauré à son texte d'origine une fois acquitté/fermé — pour
prévenir Alain même s'il consulte un autre onglet du navigateur.

**Garde-fous :** pas de son ni de notification système, tout reste dans la
page. Les liens et boutons déjà existants de la barre latérale gardent
leur comportement et leur ordre. Rien ne s'affiche pour un projet sans
push suivi — la barre latérale reste identique à avant cette issue.

### Adopter le crochet pour un projet (guide pratique)

Ce qui précède décrit ce que fait `relecture_web` une fois un projet
équipé. Cette sous-section décrit l'autre moitié : comment équiper un
projet du crochet lui-même, et ce qu'il faut savoir en dehors de
`relecture_web`.

**Principe d'activation.** Il n'existe aucun réglage ni aucune liste de
projets dans `relecture_web` : la seule condition, pour basculer en
arrière-plan, est la présence d'un crochet `pre-push` exécutable dans le
dépôt (voir la détection décrite plus haut). Sans un tel crochet, le
comportement reste exactement celui d'avant l'issue #122. Et jamais pour
un projet distant du PC fixe (`_ccw`, section 11), quel que soit l'état de
son crochet.

**Vérifier l'activation sans lancer de push (issue #129).** La page
« branches d'un projet » (section 2) affiche désormais 🪝 devant le nom du
projet dès qu'il est équipé d'un crochet exécutable, et ⚠️ si le fichier de
crochet existe mais que le `chmod +x` a été oublié — exactement le piège
décrit ci-dessous (droit d'exécution manquant, crochet silencieusement
ignoré par git). Plus besoin de lancer un push pour le savoir : ce symbole
réutilise la même détection que le push lui-même.

**Où vit le crochet.** Dans le dossier de crochets du dépôt — commun à
toutes ses worktrees, jamais dupliqué par worktree — qui n'est pas
versionné par git : un nouveau clone ou une réinstallation du projet ne le
retrouve donc pas, il faut le réinstaller à la main à chaque fois.
`relecture_web` ne l'installe, ne le modifie et ne le supprime jamais.
Attention à un réglage global de l'emplacement des crochets sur la
machine : posé en global plutôt qu'en local, il équiperait d'un coup tous
les dépôts de la machine — à poser uniquement dans le dépôt réellement
visé.

**Ce que le crochet devrait faire (recommandation, pas une garantie de
`relecture_web`).** Tester le commit réellement poussé plutôt que le
dossier de travail tel quel : git transmet au crochet les références
poussées, alors que `relecture_web` lance le push depuis le dossier
principal du projet, qui n'a pas forcément cette branche en cours. Tester
une copie propre de ce commit évite aussi un résultat faussé par une
action en parallèle sur le dossier principal — à ce sujet, `relecture_web`
bloque de toute façon toute autre action git sur ce projet pendant la
durée du push (voir plus haut).

**Prérequis d'un projet.** Sa suite de tests ne doit dépendre d'aucun
fichier local ignoré par git, sous peine d'échouer dans une copie propre
et de provoquer un faux refus — cas vécu avec `bruit_projets.log` sur
`relecture_bridge` lui-même, corrigé à l'issue #121.

**Hors `relecture_web`.** Un push lancé dans un terminal ou par un autre
agent déclenche le même crochet. `git push --no-verify` le saute : c'est
la porte de sortie volontaire, à réserver à une panne d'environnement
(aucun bouton équivalent dans `relecture_web`, voir « Pas de
contournement » plus haut) — un tel push n'apparaît pas dans le panneau
« Dernier push », les commits se voient simplement poussés après un
rafraîchissement.

**Adoption progressive.** Un projet à la fois, en commençant par
`Bridge_Agent` ; une fois le comportement jugé satisfaisant, un autre
projet peut recevoir le même crochet dans son propre dépôt — rien à
configurer côté `relecture_web`.

**Tester sans risque.** Avant d'équiper un vrai projet : poser un faux
crochet qui affiche quelques lignes, attend une quinzaine de secondes puis
refuse toujours, et pousser une branche jetable portant un commit vide
(créée sans toucher au dossier de travail actuel). Vérifier l'indicateur
dans la barre latérale, la fenêtre de résultat et le panneau « Attention
Refus », puis tout nettoyer : supprimer la branche de test ET le faux
crochet, qui bloquerait sinon tous les vrais pushes suivants. Le crochet
refuse avant tout envoi réseau, donc rien ne part sur GitHub pendant cet
essai — mais ne jamais fusionner la branche de test dans la branche
principale (cas vécu).
