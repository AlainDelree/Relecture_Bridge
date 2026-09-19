## Nature du changement
La route Flask `/relancer-issue` (`app/interruption.py::route_relancer`) redémarre désormais automatiquement le watcher CCL cible s'il était éteint, à condition que l'issue porte le label `for-linux`. Le résultat (démarrage, pid, échec éventuel) est tracé dans le commentaire posté sur l'issue et dans la réponse JSON. Côté front (`static/js/app.js`), `relancerIssue()` transmet désormais les labels de l'issue au serveur et met à jour le texte de confirmation. Un fichier de tests de non-régression (`tests/test_relancer_watcher_574.py`) couvre six scénarios.

## Intention probable
Aligner le troisième chemin de remise en circuit d'une issue (le bouton web « 🔄 Relancer ») sur les deux autres (#202 création, #572 bloc RELANCE), qui redémarraient déjà le watcher éteint par auto-extinction (#200) — combler une incohérence.

## Points d'attention
- Le redémarrage du watcher est gouverné par un `try/except Exception` large voulu non bloquant : vérifier qu'aucune exception hors périmètre (ex. import raté de `demarrer_watcher`) ne soit masquée silencieusement au-delà de l'intention.
- La garde `for-linux` repose sur des labels fournis par le client (`data.get("labels")`) et non revalidés côté serveur contre l'état réel GitHub : un client omettant/falsifiant les labels court-circuite ou déclenche indûment le démarrage. Impact limité (au pire un watcher démarré à tort), mais dépendance à une entrée non fiable à garder en tête.
- Ce commit doit rester cohérent avec les chemins #202 et #572 : toute divergence future de la garde `for-linux`/`for-windows` ou de la signature `demarrer_watcher(cfg, forcer=False)` devra être répercutée sur les trois.
- Les tests réassignent des fonctions de module (`interruption.projet_par_depot`, `_retirer_label_gh`, `demarrer_watcher`) et les restaurent dans un `finally` — à exécuter isolément, pas de fuite d'état vers d'autres suites.
