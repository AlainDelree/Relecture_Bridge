## Nature du changement
Retrait complet de l'onglet « Git » introduit à l'issue #569 : suppression de la route `/git-etat` et de son import dans `app/__init__.py`, suppression du module `app/git_etat.py` (fonctions `commits_non_pousses` et `etat_git`), retrait de l'onglet et du panneau dans `templates/index.html`, et suppression de la fonction JS `chargerGitEtat` ainsi que de l'entrée `'git'` dans `basculerOnglet` de `static/js/app.js`.

## Intention probable
Abandon de la fonctionnalité « Git » (worktrees + commits non poussés) jugée non retenue ou remplacée, comme l'indique le message `fix #573 : retire l'onglet Git`.

## Points d'attention
- Cohérence de l'index des onglets : `basculerOnglet` associe les noms au DOM via l'index positionnel (`noms[i]`). Le retrait de `'git'` dans le tableau JS **et** de la `<div class="onglet">` correspondante dans le template doivent rester alignés — vérifier que l'ordre des `.onglet` du HTML correspond bien au nouveau tableau, sinon les onglets « ccw » et suivants seront décalés.
- Vérifier qu'aucun autre appelant (autre fichier JS, test, endpoint) ne référence encore `chargerGitEtat`, `/git-etat`, `app.git_etat` ou `commits_non_pousses` après suppression.
- `app/git_etat.py` importait `_lister_worktrees_secondaires` et `_est_depot_git` de `watcher` : ce commit n'y touche pas, mais si d'autres commits (issue #569) faisaient dépendre ces helpers de cette vue, s'assurer de l'ordre d'application pour éviter un état intermédiaire incohérent.
