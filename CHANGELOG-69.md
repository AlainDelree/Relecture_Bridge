## 2026-09-24 — issue #69 (relecture_web)

- Ajout d'un bouton « 🔄 Rafraîchir » sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : simple lien GET vers l'URL
  courante de la page (pas un `location.reload()`), pour recharger l'état
  git à jour après une action faite en terminal sans jamais risquer de
  faire réapparaître l'avertissement « resoumettre le formulaire » du
  navigateur qu'un vrai F5 peut déclencher après un POST.
- Ajout d'un bouton « 📋 Copier » réutilisant le composant générique
  `.bouton-copier` déjà utilisé ailleurs (hash, nom de branche) pour
  copier dans le presse-papiers le chemin d'un fichier en conflit tel que
  renvoyé par `git status` : à côté de chaque fichier listé dans la
  section « ⚠ Fusion en conflit » de la page projet, et dans l'en-tête de
  la page Conflit. Purement côté navigateur, aucune route serveur.
- Ajout d'un bouton « Traiter tous les blocs » sur la page Conflit,
  variante « tout ou rien » de « Traiter ce bloc » qui applique en une
  seule opération le contenu de chaque `<textarea>` du panneau droit au
  bloc de conflit correspondant, sans recharger la page entre chaque
  bloc :
  - `relecture_web/git_info.py` : `lire_conflits_fichier` calcule
    désormais aussi une empreinte (sha256 du contenu) transmise à
    l'affichage ; nouvelle fonction `resoudre_tous_blocs_conflit`,
    réutilisant `_trouver_blocs_conflit` (même numérotation que
    l'affichage et que « Traiter ce bloc ») — refuse tout le traitement
    (aucun bloc écrit) si le nombre de blocs ou l'empreinte ne
    correspondent plus à ce qui a été affiché ; applique les
    remplacements du dernier bloc vers le premier pour que les décalages
    d'index provoqués par un remplacement ne perturbent jamais les blocs
    restant à traiter ; `git add` automatique une fois tous les blocs
    remplacés, comme pour le traitement bloc par bloc.
  - `relecture_web/app.py` : nouvelle route
    `POST /projet/<nom_projet>/conflit/<chemin_relatif>/traiter-tous`
    (`traiter_tous_blocs_conflit_route`).
  - `relecture_web/templates/conflit.html` : bouton « Traiter tous les
    blocs (N) », confirmation JavaScript avant soumission qui signale
    explicitement les blocs dont le textarea est vide (suppression du
    bloc). « Traiter ce bloc » reste disponible, inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` sections 9 et 10 pour les
  trois ajouts.
