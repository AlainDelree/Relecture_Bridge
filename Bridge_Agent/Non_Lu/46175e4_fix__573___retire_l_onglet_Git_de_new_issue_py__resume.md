## Nature du changement
Suppression de l'onglet « Git » ajouté par erreur : retrait du fichier `app/git_etat.py` (vue lecture seule listant worktrees et commits non poussés), de sa route `/git-etat` dans `app/__init__.py`, de l'onglet + panneau dans `templates/index.html`, et du JS associé (`chargerGitEtat`, entrée `'git'` dans `basculerOnglet`) dans `static/js/app.js`. Ajout d'un `CHANGELOG-573.md`. Le paramètre `rep_travail` de `watcher.py::_lister_worktrees_secondaires()` est conservé.

## Intention probable
Déplacer cette fonctionnalité (worktrees + commits en attente) hors de l'outil de création d'issues vers un futur programme dédié `relecture_bridge`, conformément au message de commit `fix #573`.

## Points d'attention
- **Cohérence de l'index des onglets dans `basculerOnglet`** : la liste `noms` est appariée par position (`noms[i]`) aux éléments `.onglet` du DOM. Le retrait simultané de `'git'` dans le tableau JS et de la `<div class="onglet">` correspondante dans le HTML doit rester aligné — vérifier que l'ordre des onglets restants (`creation, resultats, inbox, journal, config, watchers, ccw`) correspond exactement à l'ordre du HTML, sinon la bascule d'onglet se décale.
- **Dépendance conservée dans `watcher.py`** : le paramètre `rep_travail` reste dans `_lister_worktrees_secondaires()` alors que son seul consommateur externe (`git_etat.py`) disparaît ; s'assurer qu'aucun autre commit/worktree en attente ne s'appuie encore dessus, et que la rétrocompatibilité annoncée avec `verifier_accumulation_worktrees()` tient réellement.
- **Ordre d'application** : ce commit annule du code introduit par l'issue #569 ; si des commits liés à #569 restent à pousser ailleurs, coordonner l'ordre pour éviter une réintroduction ou une route orpheline.
