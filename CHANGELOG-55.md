## 2026-09-21 — issue #55 (relecture_web)

- Nouvelle section **⚠ Fusion en conflit** sur la page « branches d'un
  projet » : détecte, via `git status --porcelain` (codes `UU`, `AA`,
  `DD`, `AU`, `UA`, `DU`, `UD`), les fichiers en conflit d'une fusion
  non résolue et les liste, sans avoir à taper `git status`/`grep` en
  terminal.
- Nouvelle page **Conflit** (`/projet/<nom_projet>/conflit/<chemin>`)
  pour un fichier sélectionné : localise chaque bloc entre `<<<<<<<`,
  `=======` et `>>>>>>>`, affiche les deux versions dans des blocs de
  texte à fond coloré distinct (bleu « ours »/`HEAD`, orange « theirs »
  — volontairement pas un `<textarea>`, qui ne supporte pas le texte en
  couleur), et le texte hors conflit normalement autour pour le
  contexte. Un éventuel marqueur de base commune diff3 (`|||||||`) est
  ignoré, seules les deux versions en conflit sont affichées.
- Strictement en lecture seule : aucune écriture sur le fichier. Le
  chemin demandé n'est accepté que s'il figure dans la liste actuelle
  des fichiers en conflit renvoyée par `git status` (recalculée à
  chaque requête), jamais construit à l'aveugle depuis le paramètre
  d'URL — protège aussi contre un chemin en dehors du dépôt du projet.
  La résolution (choisir/éditer le texte final et l'écrire) fait
  l'objet d'une issue de suivi séparée.
- `git_info.py` : `get_fichiers_en_conflit`, `_extraire_blocs_conflit`,
  `lire_conflits_fichier`.
- `RELECTURE_WEB_DOC.md` mise à jour (nouvelle section 10, ancienne
  section 10 renumérotée 11, mention dans la navigation section 2).
