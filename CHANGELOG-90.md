## 2026-09-26 — issue #90 (relecture_web)

Sur la page Conflit, cliquer sur la flèche bleue puis sur la flèche orange
remplaçait le résultat au lieu de l'ajouter — impossible de garder les deux
versions l'une après l'autre, un cas fréquent (deux ajouts indépendants au
même endroit). Par ailleurs, transmettre le contenu d'un gros bloc de
conflit à Claude Chat obligeait à une capture d'écran, imprécise.

- **Ajout — « Garder les deux »** (`templates/conflit.html`) : quatrième
  flèche (⇅, violette) dans le groupe bleu/orange/✕ de chaque bloc. Place
  le contenu HEAD puis celui de la branche entrante à la suite dans le
  `<textarea>` du résultat, avec un saut de ligne entre les deux uniquement
  si le texte HEAD n'en a pas déjà un en fin. Les flèches bleue et orange
  restent des remplacements complets, inchangées.
- **Ajout — « Copier ce bloc »** (`templates/conflit.html`,
  `static/style.css`) : bouton `.bouton-copier` (📋) en coin haut-droit de
  chaque bloc du panneau gauche (lecture seule), copiant tout le texte
  affiché du bloc — en-têtes `<<<<<<<`/`>>>>>>>` et contenu des deux côtés
  compris, tel qu'affiché à l'écran — via le mécanisme `.bouton-copier`
  déjà utilisé ailleurs dans `relecture_web` (retour visuel bref identique).
- **`git_info.py`** : nouvelle fonction `_texte_affiche_bloc`, et nouveau
  champ `texte_affiche` par segment de conflit dans `_extraire_blocs_conflit`
  — précalcule côté serveur le texte exact du panneau gauche pour un bloc
  donné, avec la même règle de saut de ligne que « Garder les deux »
  (jamais de ligne vide dupliquée entre les deux moitiés).
- Le marqueur `=======` d'un conflit brut n'a volontairement pas été
  réintroduit dans l'affichage ni dans le texte copié : le panneau gauche
  remplaçait déjà ce séparateur par l'en-tête `>>>>>>> <branche>` au-dessus
  du contenu de la branche entrante (issue #59), qui joue le même rôle de
  repère visuel sans perdre le nom de la branche — copier « tel qu'affiché »
  respecte ce choix existant plutôt que de le contredire silencieusement.
- **Doc** : `RELECTURE_WEB_DOC.md` section 10 complétée avec les deux
  nouveaux boutons.
- Vérifié : `python3 -m py_compile git_info.py app.py` OK ; sortie de
  `_extraire_blocs_conflit`/`_texte_affiche_bloc` testée manuellement sur un
  conflit simple et sur un bloc à côté HEAD vide (cas des deux ajouts
  indépendants) — aucune ligne vide dupliquée dans les deux cas. Pas de
  suite de tests automatisés existante pour `relecture_web` à étendre.
