## Issue #103 — 2026-10-06

- `relecture_web` : constat en usage réel (rummikub, worktree-issue-133) —
  « Rejeter » a échoué avec « fatal: '<chemin>' contient des fichiers
  modifiés ou non-suivis, utilisez --force pour le supprimer » (garde-fou
  voulu : `git worktree remove` n'est jamais appelé avec `--force`), mais
  l'interface n'offrait ensuite aucune suite — Alain devait passer par un
  terminal pour comprendre ce que contenait le dossier puis forcer
  lui-même. Nouveau cas géré pour « Rejeter », « Supprimer la/les
  branche(s) fusionnée(s) » et « Merger et supprimer », `app.py`,
  `git_info.py`, nouveau template `echec_suppression_worktree.html` et
  `style.css` :
  - **Détection indépendante de la langue de git** : l'échec de
    `git worktree remove` n'est jamais interprété via le texte de son
    message d'erreur (traduit selon la locale de git). Nouvelle fonction
    `diagnostiquer_echec_suppression_worktree` : revérifie l'état réel du
    dossier via `git status --porcelain` exécuté DANS le worktree lui-même.
    Une sortie non vide confirme le cas « fichiers modifiés ou non
    suivis » (les fichiers ignorés par `.gitignore` n'y figurent jamais,
    comme pour git) ; une sortie vide (verrou, chemin déjà supprimé à la
    main, autre cause) laisse le message d'erreur brut de git s'afficher
    comme avant, sans bouton de forçage.
  - **Page dédiée montrant ce qui serait perdu** avant toute décision,
    `echec_suppression_worktree.html` : liste des fichiers avec leur statut
    (modifié / non suivi), plafonnée à 20 entrées puis « … et N autres »
    (`MAX_FICHIERS_AFFICHES_ECHEC_SUPPRESSION`) ; pour les fichiers suivis
    modifiés, `+ajouts −suppressions` par fichier (`git diff HEAD
    --numstat`) ; bouton « Copier le diff » (`.bouton-copier` existant)
    copiant le diff complet (`git diff HEAD`) des seuls fichiers suivis
    modifiés, plafonné à 2000 lignes et signalé si tronqué
    (`MAX_LIGNES_DIFF_ECHEC_SUPPRESSION`) — pour transmettre le contenu à
    un Claude Chat avant de trancher.
  - **Bouton « Forcer la suppression »**, affiché uniquement sur cette page
    (jamais permanent, jamais une case à cocher qui survivrait à un
    rechargement — leçon de la case « Purger », issue #102) : confirmation
    forte (bandeau rouge, focus par défaut sur Annuler, bouton nommé avec
    la portée réelle « Supprimer <branche> et ses N fichiers concernés »,
    commande équivalente affichée avec `--force`). Deux nouvelles routes,
    une par action d'origine puisque leurs garde-fous d'éligibilité sont
    strictement inverses : `supprimer_worktree_force_route` (branche
    confirmée fusionnée — partagée par « Supprimer » et « Merger et
    supprimer », le merge ayant déjà eu lieu avant cet échec) et
    `rejeter_worktree_force_route` (branche **non** fusionnée, reprend
    l'option « Purger réellement » de #96 via un champ caché). Les deux
    s'appuient sur une nouvelle fonction `supprimer_worktree_force`
    (`git worktree remove --force` puis `branch -D` habituel) et refusent,
    avec message explicite, si le badge « ⚠ CCL travaille ici » (#88) est
    actif sur ce worktree.
  - Si le worktree est en plus verrouillé (`git worktree lock`, qui exige
    alors deux `--force` consécutifs) ou si la suppression forcée échoue
    malgré tout, l'erreur brute de git est affichée telle quelle, sans
    nouvelle tentative automatique.
  - `RELECTURE_WEB_DOC.md` section 9 mise à jour (nouvelle ligne
    « Forcer la suppression »).
