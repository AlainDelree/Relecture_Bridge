## Nature du changement
Retrait complet du dispositif de diagnostic temporaire lié à l'issue #157. Suppression du module `app/diag_heartbeat.py`, des appels de journalisation (`log_heartbeat`, `log_sse`, `log_arret`) dans `app/cycle_vie.py`, de l'enregistrement de la route `/diag-visibilite` et de son import dans `app/__init__.py`, ainsi que du bloc `console.log`/`fetch` sur `visibilitychange` dans `static/js/app.js`.

## Intention probable
Le correctif du heartbeat/SSE de l'issue #157 étant validé, on nettoie l'instrumentation temporaire prévue pour être retirée, conformément à la procédure documentée dans l'en-tête du fichier supprimé.

## Points d'attention
- Le retrait suit exactement la procédure documentée : vérifier que l'appel `envoyerHeartbeat()` sur `visibilitychange` et le relèvement du seuil (le correctif réel de #157) ont bien été conservés — c'est le cas dans ce diff (ligne `if (!document.hidden) envoyerHeartbeat();`).
- La route `/diag-visibilite` était **non authentifiée** (ajoutée sans `login_requis`) : son retrait supprime aussi cette petite surface d'exposition, ce qui est plutôt une amélioration.
- Point de propreté hors diff : l'ancien fichier `logs/heartbeat_diag.log` (étape 5 de la procédure) n'est pas concerné par ce commit ; penser à le supprimer manuellement s'il subsiste.
