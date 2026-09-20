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

### Lancement

```bash
python3 relecture_web/app.py
```

Sert sur `http://127.0.0.1:5057/`. Usage strictement local, aucune
authentification (même choix assumé que `new_issue.py`) — l'outil n'est
jamais exposé au-delà de la machine d'Alain.

### Source de la liste des projets

Au démarrage, `relecture_web` récupère la liste des projets actifs
directement depuis le tableau public de `BRIDGE_AGENT_DOC.md`
(`raw.githubusercontent.com`), pas d'une config locale codée en dur —
si un projet est ajouté ou retiré de ce tableau, `relecture_web` le
reflète automatiquement au prochain chargement.

## 2. Navigation à trois niveaux

L'interface est organisée en trois niveaux, chacun avec sa page :

1. **Projets** (`/`) — un projet par ligne, avec le nombre de résumés
   en attente de relecture entre parenthèses, et un badge `🌿 N
   worktree(s)` s'il y a des worktrees secondaires actifs. Un projet
   dont le dossier est introuvable ou n'est pas un dépôt git est affiché
   grisé, sans lien cliquable.
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
navigation principale : **Comparer**, **Rapport** (section 5), et
**Comparer la sélection** (issue #47, section 5) — cette dernière
uniquement depuis le panneau d'actions du niveau 2, sur une sélection de
branches `recuperation-<hash>`.

Une **barre latérale gauche**, présente sur toutes les pages (`base.html`),
liste les noms de tous les projets avec un lien direct vers leur page
`/projet/<nom_projet>` — le projet actuellement affiché y est mis en
évidence. Volontairement minimale (juste les noms, sans compteur ni
badge) : la liste réutilise la même donnée déjà chargée par la route en
cours (mémoïsée le temps d'une requête), pour ne pas répéter l'appel
réseau vers `BRIDGE_AGENT_DOC.md` sur chaque page — le coût déjà corrigé
une fois côté page d'accueil (section suivante, issue #17/#19) ne devait
pas être réintroduit ailleurs (issue #44).

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
- **`⚠ point d'attention`** — sur une carte de commit repliée, le résumé
  fonctionnel généré automatiquement contient du texte non vide dans sa
  section « Points d'attention ».

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

Toutes les actions ci-dessous nécessitent une confirmation JavaScript
(`confirm()`) côté navigateur avant soumission, affichant la commande
git équivalente exacte qui sera exécutée — jamais d'exécution
silencieuse.

| Action | Portée | Commande équivalente | Garde-fou |
|---|---|---|---|
| **Revert** | Un commit précis, sur la page d'une branche. | `git revert --no-edit <hash>` | Aucun autre que la confirmation — crée un nouveau commit d'annulation, ne réécrit pas l'historique. |
| **Push** | Une ou plusieurs branches sélectionnées (cases à cocher, niveau « branches d'un projet »). | `git push <remote> <branche>` | Cible toujours une branche entière jusqu'à son dernier commit, jamais une sélection de commits épars. Timeout de 120s (dépôt volumineux, connexion lente) ; un dépassement ou une erreur inattendue est rapporté par un message flash explicite, jamais par une page d'erreur brute (issue #39). Après la confirmation, une fenêtre superposée « Push en cours... Ns » (compteur de secondes) reste affichée jusqu'au rechargement de la page avec le résultat — purement visuel côté navigateur, aucun changement serveur (issue #49). |
| **Merger** | Une ou plusieurs branches sélectionnées. | `git merge <branche>` (avec bascule temporaire si la branche cible n'a pas de worktree dédié) | Refusé si la branche est déjà la branche cible, ou si le diagnostic « doublons uniquement » (section 4) indique qu'elle n'apporterait aucun contenu nouveau. Un conflit laisse volontairement le dépôt en état de fusion non résolue (pas de rollback automatique), pour ne pas perdre l'information. Même timeout étendu (120s) et même gestion d'erreur par message flash que Push (issue #39). Projet à plusieurs cibles configurées (section 7, issue #52) : un sélecteur « Cible du merge » apparaît dans le panneau d'actions — aucune cible n'est devinée, refus par message flash si aucune n'est choisie explicitement. Même indicateur « Fusion en cours... Ns » que Push après confirmation (issue #49). |
| **Supprimer la/les branche(s) fusionnée(s)** | Une ou plusieurs branches sélectionnées confirmées fusionnées. | `git worktree remove <chemin>` **puis** `git branch -D <nom>` dans le même clic si la branche a encore un worktree actif (issue #54 — plus besoin de recliquer une seconde fois) ; sinon `git branch -D <nom>` directement (issue #43 — cas d'un worktree déjà retiré manuellement, ne laissant que la branche). | Refusé si c'est la branche principale, ou si elle n'est pas confirmée fusionnée dans la branche cible. Le `worktree remove` n'est jamais `--force` : git refuse de lui-même s'il reste des modifications non commitées ; si cette étape échoue, la branche n'est pas touchée. Le `branch -D` (sans worktree) n'a pas cette protection, d'où l'exigence stricte de `mergee` en amont. Même bouton dans tous les cas — seule la commande affichée en confirmation diffère, et le message flash rapporte les deux étapes quand les deux ont eu lieu. |
| **Sécuriser** (un commit ou tous) | Un commit orphelin, ou tous les commits orphelins d'un projet. | `git branch recuperation-<hash> <hash>` | Voir section 6 — geste purement défensif, idempotent. |
| **Supprimer la/les branche(s) de récupération** | Une ou plusieurs branches sélectionnées suivant la convention `recuperation-<hash>`. | `git branch -D <nom>` | Voir section 6 — refus structurel si le nom ne suit pas exactement la convention, indépendamment du badge affiché. Supprime aussi les fichiers `Non_Lu/` de toute la chaîne de commits protégée par la branche, pas seulement le hash nommé. |
| **Comparer** | Un commit orphelin (cas B), en lecture seule. | `git diff <hash1> <hash2>` (après localisation par `git patch-id`) | Aucune modification — voir section 5. |
| **Comparer la sélection** | Une ou plusieurs branches `recuperation-<hash>` sélectionnées, en lecture seule. | `comparer_commit_doublon` (donc `git diff`/`git patch-id`) relancé pour chacune | Aucune modification — voir section 5. Branche hors convention `recuperation-<hash>` ignorée. Le bouton de suppression groupée proposé sur le résultat ne couvre que les branches confirmées diff vide. |
| **Générer rapport** | Un commit non tranché (cas F, ou tout commit affiché sur une branche), en lecture seule. | `git cherry`, `git branch --contains`, `git branch -r --contains` (assemblés en texte) | Aucune modification — voir section 5. |
| **Nettoyer tous les projets** | Tous les projets accessibles. | suppression de fichiers `Non_Lu/` (pas de commande git) | Ne supprime que les résumés dont le commit est déjà un ancêtre d'une branche **distante** (`git branch -r --contains`) — jamais un résumé dont le commit n'est pas encore réellement en sécurité sur GitHub. |

## 10. Comment interpréter une capture ou un export de `relecture_web`

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
