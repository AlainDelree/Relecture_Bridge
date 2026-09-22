## Nature du changement
`_debut_traitement()` (`app/issues.py`) ne remet plus systématiquement `debut` à `None` en rencontrant un commentaire « Échec après N tentatives » : une nouvelle helper `_echec_recent()` et la constante `FENETRE_TRANSITOIRE_ECHEC_S = 120` limitent cette réinitialisation aux marqueurs anciens. Import de `timezone` ajouté, docstring/commentaires actualisés, plus un fichier de test pur (6 scénarios) et un CHANGELOG-588.md.

## Intention probable
Corriger l'affichage trompeur « ⏳ en file » pour une issue qui vient d'épuiser ses tentatives, pendant la fenêtre non atomique entre la pose du commentaire d'échec et du label `needs-human` côté `watcher.py`, tout en préservant le comportement #525.

## Points d'attention
- Le seuil de 120 s repose sur l'hypothèse que les deux appels `gh` de `watcher.py` (timeout 30 s chacun) restent séparés de moins de ~60 s ; si `watcher.py` change ses timeouts ou son enchaînement, cette marge devient un couplage implicite à revérifier.
- `_echec_recent()` dépend de l'horloge locale vs horodatages GitHub : un décalage d'horloge ou un fuseau mal normalisé pourrait faire basculer la borne `0 <= age_s <= 120` (un `createdAt` légèrement dans le futur renvoie `False` → retour au comportement d'origine, à confirmer comme voulu).
- La docstring référence `watcher.py:4374` (numéro de ligne codé en dur) : à garder synchronisé avec le fichier réel pour éviter une doc trompeuse.
- Rien de sensible côté secrets/authentification ; l'ordre d'application avec d'autres worktrees n'est pas critique ici (fonction pure, tests sans réseau).
