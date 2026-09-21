## 2026-09-21 — issue #56 (relecture_web)

- Page **Conflit** (issue #55) : à côté de chaque bloc affiché en
  lecture seule, ajout d'un `<textarea>` éditable pré-rempli avec la
  version « ours », dans lequel Alain compose le texte final à garder
  (copie d'une des deux versions, combinaison, ou tout autre texte, y
  compris vide pour supprimer le bloc). Bouton « Traiter ce bloc »
  (confirmation JS avec aperçu du texte) qui remplace ce bloc précis —
  marqueurs `<<<<<<<`/`=======`/`>>>>>>>` compris — par ce texte dans
  le fichier réel, en local uniquement.
- Nouvelle route `POST /projet/<nom_projet>/conflit/<chemin>/traiter` :
  revalide que le fichier est toujours en conflit avant d'écrire, comme
  la route de lecture voisine. Redirige vers la même page de conflit
  s'il reste des blocs (le suivant apparaît naturellement en premier),
  ou vers la page du projet avec un message clair une fois le fichier
  entièrement résolu.
- `git_info.py` : `_extraire_blocs_conflit` (issue #55) factorisée avec
  une nouvelle `_trouver_blocs_conflit`, partagée avec la nouvelle
  `resoudre_bloc_conflit` — garantit que la numérotation des blocs
  (0-based, ordre d'apparition) est strictement identique entre
  affichage et résolution, pour qu'une soumission ne puisse jamais
  toucher le mauvais bloc. Si le fichier a changé entre l'affichage et
  la soumission au point que le numéro de bloc ne corresponde plus
  (bloc déjà traité, fichier modifié ailleurs), `resoudre_bloc_conflit`
  échoue proprement avec un message d'erreur plutôt que d'écrire à
  l'aveugle. Lecture/écriture strictement UTF-8 (contrairement à la
  lecture seule d'issue #55, qui tolère les octets invalides puisqu'elle
  n'écrit jamais).
- Une fois le dernier bloc d'un fichier traité, `git add <fichier>` est
  lancé automatiquement pour marquer sa résolution — le commit et le
  push restent des gestes manuels d'Alain, volontairement non
  automatisés.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour (titre et contenu :
  détection **et résolution**, suppression de la mention "strictement
  en lecture seule" devenue fausse).
- Testé manuellement (dépôt de test jetable hors périmètre) : bloc
  unique, blocs multiples, texte final vide (suppression du bloc),
  index de bloc obsolète (erreur propre sans écriture) — tous les cas
  se comportent comme attendu, `git add` ne se déclenche qu'au dernier
  bloc.
