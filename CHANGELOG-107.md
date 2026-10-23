## Issue #107 — 2026-10-23

- `relecture_web` : suite de l'issue #105 — la résolution de conflit
  (`resoudre_bloc_conflit`, `resoudre_tous_blocs_conflit`, `git_info.py`)
  aplatissait tout le fichier en LF dès la résolution d'un seul bloc,
  y compris un fichier entièrement en CRLF depuis l'origine : la lecture
  et l'écriture se faisaient en mode texte Python par défaut, qui traduit
  silencieusement `\r\n`/`\r` en `\n` à la lecture (mode « universal
  newlines ») sans jamais les restituer à l'écriture. `lire_conflits_fichier`,
  `resoudre_bloc_conflit` et `resoudre_tous_blocs_conflit` ouvrent désormais
  le fichier avec `newline=""` (lecture et écriture), qui désactive cette
  traduction — un fichier CRLF reste CRLF, un fichier LF reste LF, un
  fichier mixte garde chaque ligne de contexte (y compris un bloc non
  traité) avec exactement sa terminaison d'origine, seul le bloc remplacé
  change.
- Le texte validé soumis par le formulaire (`texte_final`) est maintenant
  normalisé, avant insertion, vers la fin de ligne **dominante du fichier
  cible** (la plus fréquente entre CRLF et LF ; LF par défaut en cas
  d'égalité ou d'absence de toute fin de ligne — nouvelles fonctions
  `_fin_de_ligne_dominante_fichier`/`_normaliser_fin_de_ligne_texte`).
  Nécessaire parce qu'un navigateur convertit les retours à la ligne d'un
  `<textarea>` en CRLF à la soumission d'un formulaire HTML, quelle que
  soit leur forme dans le DOM — y compris pour un texte composé par une
  flèche de copie (« ours »/« theirs »/« garder les deux »), pas seulement
  pour du texte tapé à la main ; c'est ce qui expliquait le cas réel
  constaté (deux blocs résolus par deux chemins différents, les deux
  ressortis en CRLF dans un fichier historiquement LF).
- Points adjacents corrigés en cours de route (cassés dès que les lignes
  gardent leur terminaison d'origine) : `_trouver_blocs_conflit` utilisait
  `ligne.rstrip("\n")` pour les en-têtes de marqueurs (`<<<<<<<`/`>>>>>>>`),
  laissant un `\r` résiduel sur un fichier CRLF — `rstrip("\r\n")`
  désormais. `_texte_affiche_bloc` (texte précalculé du bouton « Copier ce
  bloc ») normalise maintenant explicitement vers `\n`, pour ne jamais
  exposer de caractère `\r` à l'utilisateur dans le presse-papiers, même
  sur un fichier CRLF. La détection des marqueurs et la numérotation des
  blocs (`_trouver_blocs_conflit`) n'ont pas eu besoin de changement
  (comparaison par `str.startswith`, indépendante de la terminaison de
  ligne) ; l'empreinte sha256 comparée entre l'affichage
  (`lire_conflits_fichier`) et la soumission (`resoudre_tous_blocs_conflit`)
  reste cohérente puisque les deux lisent désormais le fichier de la même
  façon (`newline=""`) — un test dédié vérifie cette cohérence.
- Tests : nouveau fichier autonome `relecture_web/test_resolution_conflit_fin_de_ligne.py`
  (`unittest`, stdlib seule — aucun framework de test externe dans ce
  dépôt au moment de cette issue), 18 tests travaillant chacun dans un
  dépôt git jetable. Couvrent : fichier entièrement LF/CRLF/mixte, un seul
  bloc puis tous les blocs ; texte validé CRLF dans un fichier LF et LF
  dans un fichier CRLF ; chaque origine de texte (saisi, ours, theirs,
  garder les deux, vider) soumise une fois en LF et une fois en CRLF ; un
  fichier à deux blocs résolus par deux chemins différents (l'un « tapé »,
  l'autre « garder les deux »), les deux soumis en CRLF dans un fichier LF
  → fichier final entièrement LF ; un bloc ignoré conserve exactement les
  octets d'origine du reste du fichier ; un conflit dont les deux côtés
  contiennent eux-mêmes du CRLF (îlot CRLF local dans un fichier à
  dominante LF). Vérifié que 16 des 18 tests échouent contre le code
  d'avant cette issue (les 2 restants portaient uniquement sur le
  comportement déjà correct de la suppression de bloc vide), confirmant
  qu'ils couvrent bien la régression corrigée.
- `RELECTURE_WEB_DOC.md` (section 10) : nouveaux paragraphes décrivant la
  préservation des fins de ligne et la règle de normalisation du texte
  validé, plus une puce dédiée dans la description de « Traiter tous les
  blocs » (fin de ligne unique calculée une fois pour tout le fichier).
- Hors périmètre, volontairement non traité (demandé explicitement ainsi) :
  aucune conversion des fichiers déjà existants dans les dépôts, aucun
  changement du hook post-commit, aucun changement d'interface (`app.py`
  et `conflit.html` inchangés — la normalisation est centralisée côté
  `git_info.py`, point de passage unique de toutes les origines de texte
  avant écriture).
