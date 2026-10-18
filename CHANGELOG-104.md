## Issue #104 — 2026-10-18

- `scripts/fusionner_changelog.py` : la ligne de titre d'échange en tête
  d'un `CHANGELOG-<N>.md` (« # CHANGELOG-N — à fusionner dans CHANGELOG.md »,
  tiret cadratin ou simple, N quelconque, lignes vides tolérées avant)
  n'était reprise dans `CHANGELOG.md` que parce que `fusionner` insérait le
  contenu du fichier d'échange tel quel — 64 lignes de ce type accumulées
  sur Bridge_Agent au fil des fusions, tous les projets fusionnés via
  relecture_web étant potentiellement concernés (issue #87). Nouvelle
  fonction `_retirer_entete_echange` : retire cette ligne et la ou les
  lignes vides qui la suivent directement avant insertion, si elle est
  présente en tout début de fichier ; absente, le contenu de l'entrée est
  repris intégralement, comme avant (jamais de perte d'une vraie entrée).
  Reste inchangé : tri par N décroissant, points d'insertion (en-tête
  « Convention d'ajout » ou repli), suppression des fichiers traités après
  fusion, idempotence, rapport affiché. Docstring du script et
  `RELECTURE_WEB_DOC.md` (section 9, action Merger) mis à jour en
  conséquence. Testé manuellement (dépôt jetable) : fichier avec en-tête
  tiret cadratin, fichier avec en-tête tiret simple et lignes vides
  avant/après, fichier sans en-tête, lot de plusieurs fichiers — dans tous
  les cas seule la ligne d'en-tête d'échange est retirée, le reste de
  l'entrée et le contenu déjà présent dans `CHANGELOG.md` restent intacts.
  Portée hors périmètre (volontairement non traitée) : nettoyage rétroactif
  des lignes déjà présentes dans les `CHANGELOG.md` d'autres projets
  (Bridge_Agent et autres), qui relèvent d'autres dépôts.
