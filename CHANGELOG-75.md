## 2026-09-24 — issue #75 (post-commit)

Le hook `post-commit` construisait le nom des fichiers exportés dans
`<projet>/Non_Lu/` à partir du message de commit en remplaçant chaque
caractère non ASCII par un « _ » : un message en français (donc accentué)
donnait un nom quasi illisible, ex. « docs: régénère le tableau des
projets... » devenait `1963797_docs__r__g__n__re_le_tableau_des_projets...`.

- **Translittération des accents avant construction du nom** (`post-commit`) :
  le message de commit passe désormais par `iconv -f utf-8 -t
  ascii//translit` (é → e, à → a, ç → c, œ → oe...) avant le remplacement des
  caractères restants encore hors `[:alnum:]-_` par un « _ » — seul ce qui
  n'a pas d'équivalent ASCII devient un souligné. `iconv` absent de la
  machine : repli silencieux sur le message brut (comportement identique à
  avant l'issue #75 pour ce cas précis).
- **Soulignés en double et de fin de nom évités** : `tr -cs` (squeeze) ramène
  les runs de soulignés consécutifs (produits par exemple par une ponctuation
  suivie d'un espace) à un seul, et un `sed` final retire un éventuel
  souligné terminal — y compris celui que la troncature à 50 caractères
  pouvait faire apparaître en coupant juste après un souligné. Longueur
  maximale du champ message inchangée (50 caractères).
- **Aucun impact sur `relecture_web`** : vérifié dans `git_info.py` et
  `resumes_info.py` — seuls le hash en tête de nom (`_extraire_hash`,
  découpe sur le premier « _ ») et le suffixe (`.diff`, `_resume.md`,
  `_annote.md`) sont exploités ; le contenu du champ « message » n'est
  jamais reparsé.
- **Fichiers déjà exportés inchangés** : aucun renommage rétroactif, seuls
  les futurs exports bénéficient de la translittération.
- **Déploiement** : `installer.sh` déploie le hook par **copie**
  (`cp "$HOOK_SOURCE" "$projet/.git/hooks/post-commit"`), pas par lien
  symbolique — les projets déjà installés gardent l'ancien hook tant que
  `./installer.sh` n'est pas relancé depuis ce dépôt (`relecture_bridge`)
  pour redéployer la version corrigée sur les 8 projets actifs.
- Testé sur un dépôt temporaire (`git init` + commits avec messages
  accentués, incluant un cas avec tiret cadratin et caractères composés) :
  noms de fichiers lisibles, sans double ni souligné final.
- Documentation : `RELECTURE_WEB_DOC.md` section 8 ne détaille pas la règle
  de remplacement de caractères (seulement le motif générique
  `<hash>_<message>.diff`) — rien à mettre à jour de ce côté.
