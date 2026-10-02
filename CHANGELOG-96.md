## Issue #96 — 2026-10-02

- `relecture_web` : complément au bouton « Rejeter (sans fusionner) »
  (issue #95) — nouvelle case à cocher « Purger réellement le(s) commit(s)
  rejeté(s) », décochée par défaut. Constat fait en testant le geste manuel
  équivalent (chesscoach, worktree-issue-88) : `git branch -D` seul ne fait
  que détacher la branche, le commit reste récupérable via le reflog (90
  jours par défaut) et continue d'apparaître comme commit orphelin
  « ambigu » dans le diagnostic automatique — risque qu'un futur clic sur
  « Sécuriser tous les commits orphelins » l'embarque par erreur alors
  qu'Alain vient justement de décider de s'en débarrasser.
- `git_info.purger_reflog_et_gc` : `git reflog expire --expire=now --all`
  puis `git gc --prune=now`, déclenchée une seule fois après la boucle de
  rejet (jamais par branche) pour n'exécuter qu'un seul `gc` (coûteux) par
  clic. Ces deux commandes sont **globales au dépôt** — aucune option git
  ne permet de n'expirer/purger que le reflog d'une branche déjà supprimée
  — donc tout autre commit orphelin non sécurisé présent par ailleurs dans
  le dépôt serait aussi détruit. Aucune purge ciblée plus fine n'étant
  possible avec les commandes git disponibles, ce comportement est
  documenté explicitement plutôt qu'implémenté à l'aveugle : la case ne
  déclenche la purge qu'après confirmation explicite d'Alain (jamais en
  arrière-plan), et l'avertissement de confirmation liste nommément les
  autres commits orphelins non sécurisés qui seraient perdus en même
  temps (`projet.orphelins_non_securises_menaces`), pour qu'Alain sache ce
  qu'il perd en plus du commit qu'il rejette.
- `git_info.get_hashes_commits_non_fusionnes` (pendant de
  `get_nombre_commits_non_fusionnes` qui retourne les hashes plutôt qu'un
  compte) : capture les hashes propres à chaque branche rejetée **avant**
  le `branch -D`, la plage `principale..branche` ne se résolvant plus une
  fois la branche supprimée.
- `git_info.commit_existe` (`git cat-file -e <hash>^{commit}`) : revalide
  après la purge qu'un commit a réellement disparu avant de nettoyer son
  résumé, plutôt que de le supposer.
- Second résidu constaté lors du même test manuel : même après purge
  réelle du commit, le diagnostic de commits orphelins continuait à
  l'afficher comme « ambigu », car les fichiers résumé déposés par le hook
  post-commit (`Non_Lu/<hash>_*`) survivent à la suppression du commit — le
  diagnostic s'appuie sur leur présence sans revalider que le hash existe
  encore. Le bouton « Rejeter » supprime donc désormais, pour tout commit
  confirmé purgé (ciblé ou collatéral), ses fichiers `Non_Lu/` associés via
  `lister_fichiers_resumes_hash`/`_supprimer_fichiers` (déjà utilisés par
  « Supprimer la/les branche(s) de récupération » et « Nettoyer tous les
  projets »).
- Revalider plus généralement, dans le diagnostic de commits orphelins
  lui-même, qu'un hash trouvé dans `Non_Lu/` existe toujours dans le dépôt
  avant de le lister (plutôt que d'afficher un résumé obsolète comme
  « ambigu ») reste hors périmètre de cette issue — signalé ici comme
  amélioration possible, non traitée : le nettoyage explicite fait par le
  bouton Rejeter couvre le cas concret qui a motivé l'issue.
- Confirmation forte adaptée : cochée, elle rappelle que la purge est
  irréversible et globale, affiche la commande équivalente complète, et
  indique le nombre d'autres commits orphelins non sécurisés qui seraient
  détruits en même temps.
- `RELECTURE_WEB_DOC.md` (section 9, ligne « Rejeter (sans fusionner) »)
  mise à jour en conséquence.
