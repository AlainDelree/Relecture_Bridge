## Nature du changement
`_traiter_relance()` dans `scripts/watcher_issues_inbox.py` appelle désormais `demarrer_watcher(cfg_projet, forcer=False)` (réutilisé depuis `app/watchers.py`) pour redémarrer le watcher CCL du projet ciblé s'il s'était auto-éteint. Le résultat (redémarré/déjà actif/échec) est tracé dans le commentaire GitHub posté et le suffixe de log. Trois scénarios de test (#16, #17, #18) couvrent les cas watcher éteint, déjà actif et échec de démarrage.

## Intention probable
Débloquer les RELANCE déposées après l'auto-extinction par inactivité (#200) d'un watcher de projet, qui restaient jusqu'ici en attente d'un clic manuel sur « Relancer le watcher ».

## Points d'attention
- La variable `cfg_projet` passée à `demarrer_watcher` n'apparaît pas dans le diff : vérifier qu'elle est bien définie/résolue à ce point de `_traiter_relance` (chargement de la config du projet ciblé), sinon risque de `NameError`.
- Le `except Exception` est volontairement large pour ne pas faire échouer la relance ; c'est cohérent avec l'intention affichée, mais confirmer qu'un démarrage réellement problématique (config corrompue, droits) reste bien visible côté log et n'entraîne pas un watcher partiellement lancé.
- `demarrer_watcher` lance un process : s'assurer qu'aucun secret/token nécessaire au watcher CCL n'est requis dans l'environnement de `watcher_issues_inbox.py` et qu'il est disponible au moment du redémarrage automatique.
- Effet de bord observable (démarrage de process, commentaire GitHub public) déclenché automatiquement : rien de bloquant, mais point d'ordre d'exécution si plusieurs RELANCE ciblent le même projet en parallèle.
