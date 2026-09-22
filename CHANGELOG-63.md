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
