## Nature du changement
La route Flask `POST /relancer-issue` (`app/interruption.py::route_relancer`) lit désormais les `labels` de l'issue et, si le projet est configuré et porte le label `for-linux`, appelle `demarrer_watcher(cfg, forcer=False)` pour rallumer le watcher CCL éteint par inactivité. Le résultat est tracé dans le commentaire GitHub posté et renvoyé dans la réponse JSON (`watcher_demarre`, `watcher_pid`). Côté front, `static/js/app.js` transmet les labels au serveur et met à jour le message de confirmation. Un test de non-régression complet (`tests/test_relancer_watcher_574.py`) couvre les six scénarios.

## Intention probable
Uniformiser le comportement des trois chemins de remise en circuit d'une issue (#202, #572, #574) pour que le bouton « Relancer » ne laisse plus un watcher éteint sans redémarrage, comme l'indique le message de commit.

## Points d'attention
- L'import `from app.watchers import demarrer_watcher` est fait en local dans la route (probablement pour éviter un import circulaire) : vérifier que ce choix est intentionnel et cohérent avec les deux autres chemins.
- Le `try/except Exception` est volontairement large pour ne jamais faire échouer la relance ; l'exception `e` est interpolée telle quelle dans le commentaire GitHub posté — s'assurer qu'un message d'erreur watcher ne peut pas fuiter d'information sensible (chemins, config) dans un commentaire public.
- La garde repose sur les labels transmis par le client (`static/js/app.js`) : un appelant qui ne fournit pas `labels` (ou de mauvais labels) contourne silencieusement le redémarrage — comportement testé mais à confirmer comme acceptable.
- Ce commit dépend de la cohérence avec #200/#202/#572 : si l'ordre d'application ou l'état du code des autres chemins diffère (fonction `demarrer_watcher`, sémantique `forcer=False`), la garde `for-linux` pourrait diverger.
