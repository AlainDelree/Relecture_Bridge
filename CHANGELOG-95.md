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
