## 2026-09-24 — issue #70 (relecture_web)

- Correction de deux problèmes constatés en test réel (suite de
  l'issue #69) sur la page Conflit
  (`relecture_web/templates/conflit.html`) :
  - **Numérotation dans l'avertissement « résultat vide »** : la
    confirmation de « Traiter tous les blocs » listait les blocs vides
    avec leur index interne 0-based (« Bloc(s) au résultat vide : 0, 1 »),
    incohérent avec la navigation de la même page qui affiche « Bloc 1 /
    3 ». Le message affiche désormais la position 1-based (celle de la
    navigation) au lieu de l'index interne — seul l'affichage change, les
    index transmis au serveur (`index_bloc`, champs cachés
    `texte_final_<index>`) restent le 0-based habituel de
    `_trouver_blocs_conflit`.
  - **Libellé « version locale » inversé** : le texte d'en-tête et
    l'infobulle de la flèche orange décrivaient à tort l'orange comme la
    « version locale », alors que la version locale est HEAD (la branche
    actuelle, en bleu) — l'orange est la branche entrante, celle qu'on
    fusionne (portée par le marqueur `>>>>>>>`). Le texte d'en-tête et
    l'infobulle de la flèche orange parlent maintenant de « branche
    entrante », avec son nom affiché entre parenthèses quand il est
    disponible (extrait du marqueur `>>>>>>>` de chaque bloc, resp. du
    premier bloc du fichier pour le texte d'en-tête général) ; l'infobulle
    de la flèche bleue est précisée en « HEAD (branche actuelle) » pour la
    cohérence. `relecture_web/git_info.py` n'a pas été modifié (numérotation
    et format du marqueur `>>>>>>>` déjà exploitables tels quels).
- `RELECTURE_WEB_DOC.md` (section 10) : la terminologie ours/HEAD/bleu et
  theirs/branche entrante/orange était déjà correcte, aucune correction
  nécessaire sur ce point ; ajout d'une précision sur la numérotation
  1-based de la liste des blocs vides dans la confirmation JS, par
  opposition à l'index 0-based interne inchangé.
