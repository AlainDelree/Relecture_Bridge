## Issue #122 — 2026-11-03

- `relecture_web` : push en arrière-plan pour les projets équipés d'un
  crochet git `pre-push` exécutable (détecté par `git_info.
  chemin_hook_pre_push`/`projet_equipe_hook_pre_push`, résolu par git
  lui-même — `core.hooksPath` personnalisé et worktrees inclus, jamais
  pour un projet distant du PC fixe CCW). Pensé pour le crochet de tests
  (~80-90s) qu'Alain prévoit d'installer projet par projet : le push
  synchrone actuel (120s, `TIMEOUT_GIT_LONG`) bloquerait sinon la page, et
  le message « n'a PAS abouti » pourrait même être faux (même piège que
  l'issue #66, en pire).
- Nouveau module `relecture_web/push_arriere_plan.py` : pour un projet
  équipé, le push tourne dans un thread serveur (process git dans son
  propre groupe de processus), un seul `git push` pour toutes les
  branches cochées (le crochet ne tourne qu'une fois), délai propre de 10
  minutes distinct de `TIMEOUT_GIT_LONG` — à son dépassement, tout le
  groupe de processus est tué (`os.killpg`, pas seulement git) puis
  l'état réel est revérifié branche par branche (réutilise `git_info.
  verifier_push_apres_timeout`, même logique que l'issue #66). Un projet
  NON équipé garde l'exact comportement synchrone d'avant cette issue.
- État persistant par projet (`push_arriere_plan_etat.json`, fichier
  local ignoré par git comme les autres journaux de ce dossier) : état
  (en cours/poussé/refusé/interrompu/indéterminé), branches, horaires,
  fin de la sortie du crochet et de git (plafonnée), indicateur « vu ».
  Sert aussi de verrou par projet : un second push sur le même projet est
  refusé, de même que toute autre action qui modifie le dépôt git de ce
  projet (Merger, Merger et supprimer, Finaliser le merge, Supprimer,
  Rejeter, Sécuriser, Revert, fusion du changelog, panneau .gitignore,
  résolution de conflit — décorateur `app.refuse_si_push_en_cours`) ; les
  autres projets restent libres. Au démarrage de `relecture_web`, toute
  entrée « en cours » dont le process git n'est plus vivant est marquée
  « interrompu » puis revérifiée (`reconcilier_au_demarrage`). Fichier
  absent/corrompu -> traité comme vide ; écriture impossible -> le push
  démarre malgré tout, avec un avertissement.
- Page projet (`projet.html`) : nouveau panneau « Dernier push » (état,
  branches, horaires, détail par branche, fin de sortie), compteur de
  secondes écoulées et rafraîchissement automatique léger pendant
  l'exécution, bouton « Vu » qui acquitte un refus (la sortie des tests
  reste visible jusqu'au clic) sans jamais changer l'état lui-même ; un
  push abouti efface son propre besoin d'acquittement automatiquement.
  La confirmation forte avant Push précise, pour un projet équipé, qu'un
  crochet de tests va s'exécuter et que cela peut durer plusieurs
  minutes ; la fenêtre superposée « Push en cours... Ns » de l'issue #49
  ne s'affiche plus pour ce bouton (la requête revient tout de suite).
  Aucun bouton ni option `--no-verify` nulle part — contourner les tests
  reste possible dans un terminal, volontairement.
- 25 nouveaux tests (`test_push_arriere_plan.py`) : détection du crochet
  (présent/absent/non exécutable/`core.hooksPath`/worktree/projet
  distant), projet non équipé strictement inchangé, un seul push pour
  plusieurs branches (compte réel des invocations du crochet), verrou par
  projet (second push refusé, autre action refusée, autre projet libre),
  dépassement de délai (groupe de processus réellement tué, vérifié via
  `/proc`), redémarrage avec entrée « en cours » devenue « interrompu »
  (et cas où le process est encore vivant), fichier d'état absent/
  corrompu, acquittement « Vu ». Dépôts/remotes/état jetables dans des
  dossiers temporaires, aucun accès aux vrais fichiers locaux de
  `relecture_web`.
- `RELECTURE_WEB_DOC.md` : ligne « Push » du tableau §9 mise à jour,
  nouvelle section 13 décrivant le moteur en détail.
