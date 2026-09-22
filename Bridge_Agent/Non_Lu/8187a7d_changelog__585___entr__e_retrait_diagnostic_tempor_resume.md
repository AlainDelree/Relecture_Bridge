## Nature du changement
Ajout d'un unique fichier `CHANGELOG-585.md` (22 lignes, création pure) documentant le retrait du diagnostic temporaire #157. Aucune modification de code applicatif dans ce commit : il ne fait qu'entériner par écrit le contenu du commit précédent (suppression de `diag_heartbeat.py`, des appels dans `cycle_vie.py`, de la route dans `__init__.py` et du bloc JS).

## Intention probable
Tracer proprement dans un changelog le nettoyage d'un code de diagnostic laissé câblé plus de deux mois, en gardant trace des vérifications effectuées et du point de sécurité au passage.

## Points d'attention
- Ce commit est purement documentaire, mais il **décrit** un changement sensible du commit précédent (`cf8c9fd`) : l'ordre d'application compte — ce changelog n'a de sens qu'une fois le retrait effectif poussé, ne pas le pousser isolément.
- Le changelog mentionne à juste titre la disparition de la route POST `/diag-visibilite` qui n'était **pas** protégée par `login_requis` : vérifier avant push que le retrait effectif (commit précédent) est bien inclus, sinon la documentation affirmerait une correction de sécurité non appliquée.
- Vérifier que l'affirmation « suite de tests verte hormis `test_init_git_local_258.py` pré-existant » reflète bien l'état réel du worktree avant de pousser (l'échec réseau annoncé doit correspondre à la réalité).
