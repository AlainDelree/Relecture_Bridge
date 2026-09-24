## 2026-09-24 — issue #72 (relecture_web)

- **Bouton « Retraiter le fichier en conflit »** : dans la section « ⚠
  Fusion en conflit » de la page projet, chaque fichier déjà résolu
  (`git add` fait) pendant le merge en cours porte désormais un bouton
  « 🔁 Retraiter ce fichier » — que d'autres fichiers restent en conflit
  ou que tous soient résolus (dans ce cas, à côté de « ✅ Finaliser le
  merge »). Le clic exécute `git checkout --conflict=merge --
  <chemin>` (nouvelle fonction `retraiter_fichier_conflit`,
  `relecture_web/git_info.py`), qui recrée les marqueurs de conflit
  d'origine pour ce fichier précis à partir du mécanisme « resolve-undo »
  de git (`git ls-files --resolve-undo`, nouvelle fonction
  `get_fichiers_resolus_merge`) ; le fichier redevient `UU` et réapparaît
  dans la liste des fichiers en conflit, prêt à être rouvert depuis la
  page Conflit.
  - Garde-fous côté serveur, revérifiés à partir de l'état git actuel :
    un merge réellement en cours (`MERGE_HEAD` présent, même principe que
    « Finaliser le merge ») et un chemin figurant dans la liste actuelle
    des fichiers résolus (jamais construit à l'aveugle depuis le seul
    paramètre d'URL, même principe que la page Conflit).
  - Confirmation JS légère avant soumission (efface la résolution déjà
    appliquée à ce fichier, en entier).
  - Message flash signalant que les marqueurs recréés portent les
    libellés génériques `ours`/`theirs` au lieu de `HEAD` et du nom de la
    branche entrante — vérifié que la page Conflit reste lisible dans ce
    cas (les libellés de branche entrante de l'issue #70 affichent alors
    simplement « theirs »).
  - Nouvelle route `POST
    /projet/<nom_projet>/conflit/<chemin_relatif>/retraiter`
    (`relecture_web/app.py`).
- **Correction de documentation (`RELECTURE_WEB_DOC.md`, section 9)** :
  le point de non-retour d'un fichier résolu pendant un merge n'est pas
  le `git add` de résolution — vérifié en local sur un conflit de test
  (git 2.43) : `git ls-files --resolve-undo` conserve les informations
  nécessaires, et `git checkout --conflict=merge -- <chemin>` recrée les
  marqueurs de conflit d'origine même après ce `git add` (seule
  différence : libellés `ours`/`theirs` génériques au lieu de `HEAD` et
  du nom de la branche entrante). La vraie limite reste la finalisation
  du merge (`git commit`, bouton « Finaliser le merge ») : une fois ce
  commit fait, `MERGE_HEAD` disparaît et `git merge --abort` cesse de
  fonctionner (vérifié). Section 10 complétée avec la description de la
  nouvelle action.
