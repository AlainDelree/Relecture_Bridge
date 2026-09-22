## Nature du changement
Mise à jour du fichier `tests/test_init_git_local_258.py` uniquement. Le dictionnaire attendu de `test_deja_git` intègre désormais la clé `email_corrige: None` (ajoutée par le fix #530), et l'assertion de `test_contenu_preexistant_pas_de_push` n'exige plus le mot « public » dans `detail` (retiré par le fix #528). Les 5 fonctions `scenario_*` sont renommées en `test_*` (avec leurs références dans `main()`). Ajout d'un `CHANGELOG-586.md` documentant l'opération.

## Intention probable
Réparer un fichier de test devenu périmé et jamais collecté par pytest (diagnostic #579), pour qu'il reflète le comportement actuel de la production et s'exécute réellement lors d'un `pytest tests/`.

## Points d'attention
- **Effet de bord du renommage** : préfixer ces fonctions en `test_*` les rend collectables par pytest — jusqu'ici elles n'étaient jamais exécutées en CI. Vérifier que les 5 passent bien dans l'environnement d'intégration (et pas seulement en local/exécution directe), car de véritables régressions cachées peuvent maintenant faire échouer la suite.
- **Assertion assouplie** : `test_contenu_preexistant_pas_de_push` ne vérifie plus que « relu ». S'assurer que cet allègement ne masque pas une éventuelle régression sur le contenu du message `detail`.
- **Dépendance d'ordre entre commits** : ce test encode le comportement issu des fix #528 et #530 ; s'il est poussé/appliqué sans que ces correctifs de production soient présents dans la branche cible, les assertions échoueront. Vérifier la cohérence de l'ordre d'application avant de pousser.
