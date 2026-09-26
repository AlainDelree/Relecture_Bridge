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
