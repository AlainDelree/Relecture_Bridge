# Concepts et vocabulaire — session du 24/07/2026

> **Thèmes :** Git interne · Shell · Hooks · Tests · Conception & Python · Réflexes transversaux
> **Date :** 24/07/2026

## Git : modèle interne

- **Blob / Tree / Commit** — les trois objets de git, chacun identifié par
  l'empreinte de son contenu. Le *blob* est le contenu d'un fichier, le *tree*
  le contenu d'un dossier (liste nom → type → identifiant), le *commit* pointe
  vers un tree racine + un ou plusieurs parents. Un commit ne contient AUCUN
  fichier : que des renvois.
- **Adressage par contenu** — l'identifiant d'un objet est le hachage de son
  contenu. Deux contenus identiques = le même objet (dédoublonnage gratuit).
  Modifier un objet change son identifiant.
- **Chaîne / arbre de Merkle** — chaque commit inscrit l'identifiant de son
  parent. Modifier un vieux commit change son identifiant, donc invalide tous
  les suivants. L'historique est infalsifiable par construction. (Même principe
  que les blockchains.)
- **DAG** (graphe orienté acyclique) — un commit peut avoir plusieurs parents
  (merge). Cas courant (un seul parent) = simple liste chaînée.
- **Merge vs rebase** — merge crée un commit à deux parents, conserve la forme
  réelle du graphe. Rebase RECRÉE les commits avec un nouveau parent (nouveaux
  identifiants). Règle : ne jamais rebaser ce qui a déjà été partagé.
- **Rename** — git détecte un déplacement au niveau du fichier ENTIER, jamais
  d'un bout de fichier.
- **Diff : lecture** — `/dev/null` à gauche = création, à droite = suppression.
  `@@ -a,b +c,d @@` : b lignes à partir de a (avant), d lignes à partir de c
  (après). Le décalage s'accumule d'un bloc à l'autre. 3 lignes de contexte par
  défaut. Le texte après `@@` situe dans le fichier (fonction/section).
- **Push** — fait avancer une étiquette de branche et envoie les objets
  manquants (compressés en deltas au niveau STOCKAGE seulement). `..` = fast-
  forward sain, `+` = forcé, `!` = rejeté.

## Shell

- **`.bashrc`** — lu à chaque terminal interactif. S'arrête tôt si le shell
  n'est pas interactif (garde-fou en tête de fichier).
- **`bash script.sh` vs `source script.sh`** — `bash` lance un PROCESSUS séparé
  qui meurt à la fin (rien ne remonte au shell courant). `source` exécute DANS
  le shell courant : seul moyen de définir une fonction, une variable, ou de
  changer de répertoire.
- **Fonction vs script** — une fonction n'est nécessaire que si le code doit
  modifier l'état du shell (ex. `cd`). Sinon, un script suffit.
- **Code de sortie** — 0 = succès, toute autre valeur = échec.
- **`"$@"`** — transmet les arguments en préservant leur découpage.

## Hooks

- **Hook** — code accroché à un moment précis d'un programme, exécuté
  automatiquement quand ce moment arrive (ex. `post-commit`). C'est le NOM du
  fichier qui détermine quand il tourne.
- **Trigger** — synonyme courant côté événement. Cf. `TRIGGER AFTER INSERT` en
  SQL : même concept.

## Tests

- **Test unitaire / intégration / bout-en-bout** — portée croissante : une
  fonction / plusieurs pièces ensemble / le système complet.
- **Automatisé vs manuel** — axe indépendant de la portée. Le manuel reste
  légitime quand automatiser coûte plus que le bénéfice, quand le jugement est
  humain, ou quand l'environnement est dur à reproduire.
- **Non-régression** — test qui doit ÉCHOUER sur le code bugué et PASSER sur le
  code corrigé. Un test vert sur les deux ne prouve rien.
- **Contrôle négatif** — scénario vérifiant que le correctif n'a pas neutralisé
  la fonctionnalité au passage.
- **Test structurel vs comportemental** — le comportemental fait tourner le
  code ; le structurel LIT le code pour vérifier une propriété (ex. absence de
  doublon de noms).
- **Mock / bouchon** — faux composant remplaçant une vraie dépendance (temps,
  réseau, BDD) pour rendre le test rapide, reproductible, sans effet de bord.
- **Assertion, fixture, couverture, TDD, CI** — vocabulaire d'outillage autour
  de ces idées.

## Conception / Python

- **Refactoring** — changer la STRUCTURE du code sans changer son COMPORTEMENT.
  Preuve : suite de tests verte au même chiffre.
- **Source unique de vérité** — ne pas dupliquer une information ; les copies
  divergent silencieusement.
- **Mixin** — classe apportant des méthodes DÉJÀ ÉCRITES à une autre, en se
  fondant en elle (`self` partagé). L'organe greffé, pas l'outil autonome.
- **Héritage** — `class Enfant(Parent1, Parent2)` : l'enfant reçoit les
  méthodes de ses parents comme siennes.
- **MRO** (Method Resolution Order) — ordre de recherche d'une méthode parmi les
  classes héritées. Le premier gagne ; un doublon est ignoré EN SILENCE.
- **AST** (Abstract Syntax Tree) — le code vu comme un arbre structuré, pas
  comme du texte. Permet de raisonner sur la FORME du code là où une recherche
  textuelle est fragile.
- **Stub** — coquille de méthode au corps vide (`def f(self): ...`), pour le
  typage, sans logique. `...` = l'objet `Ellipsis`.
- **Import circulaire** — A dépend de B qui dépend de A. Parades : bloc
  `if TYPE_CHECKING:` (import réservé aux outils de type, jamais exécuté) et
  *lazy import* (import écrit DANS la méthode, résolu tardivement).
- **Docstring** — chaîne de documentation en tête de module/classe/fonction.
- **Annotation de type** — `x: Type` : déclarer un type sans donner de valeur.
  Proche du rôle d'une interface Java.

## Réflexes transversaux vus en situation

- **Path traversal / injection** — une donnée externe interprétée comme une
  instruction. Toujours valider côté « serveur », jamais faire confiance à
  l'entrée. Raisonner sur la structure, pas sur le texte.
- **`--dry-run`** — « montre ce que tu ferais sans rien écrire ». Premier appel
  à faire avec un outil qui manipule des données.
- **Découper le travail en petits commits** — un pas = une issue. Localise les
  régressions, permet d'annuler un pas isolé, garde les diffs relisables.
- **Livrer puis durcir** — une version correcte et simple d'abord, renforcée
  ensuite, plutôt que la perfection du premier coup.

## Index détaillé (repère de couverture)

> **Thèmes :** Git interne (blobs/trees/commits, adressage par contenu, Merkle,
> DAG, merge/rebase, rename, lecture de diff, push) · Shell (bashrc, source vs
> bash, fonction vs script, code de sortie, `"$@"`) · Hooks (post-commit,
> trigger) · Tests (unitaire/intégration/bout-en-bout, automatisé vs manuel,
> non-régression, contrôle négatif, structurel vs comportemental, mock) ·
> Conception & Python (refactoring, source unique de vérité, mixin, héritage,
> MRO, AST, stub, import circulaire, docstring, annotation de type) · Réflexes
> (path traversal/injection, `--dry-run`, petits commits, livrer puis durcir)
> **Date :** 24/07/2026

