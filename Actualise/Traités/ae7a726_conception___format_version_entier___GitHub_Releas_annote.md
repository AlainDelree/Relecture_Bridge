ae7a726

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ae7a726
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 21:28:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    conception : format version entier + GitHub Releases + timeout 2-3s + démarrage non bloquant (issue #4, chef #207)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 29aec9f..e437179 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 16 (36 ligne(s)) dans l'ancienne version → ligne 16 (120 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,36 +16,120 @@ s'exécute). Le raccourci Bureau/menu Démarrer de l'utilisateur final
 pointe vers Actualise, jamais directement vers l'application cible —
 sinon la mise à jour ne se déclenche jamais.
 
-### Séquence de démarrage
-
-1. Lancement d'Actualise (1ère instance).
-2. Actualise vérifie s'il existe une mise à jour de lui-même, via un
-   fichier `version.json` hébergé sur son dépôt GitHub (comparaison
-   version distante vs version locale — mécanisme portable Linux/Windows,
-   sans dépendance à `gh` CLI).
-3. Si une mise à jour d'Actualise est trouvée :
-   - Téléchargement et installation de la nouvelle version d'Actualise.
-   - Lancement d'une 2ème instance d'Actualise (la nouvelle version).
-   - Cette 2ème instance vérifie si Actualise est maintenant à jour :
-     - Si oui : procède à la vérification/mise à jour de l'application
-       cible (ex. Scrabble), puis lance l'application cible.
-     - Si non : envoie une notification ntfy, puis lance quand même
-       l'application cible (dans sa version actuelle) — pour ne jamais
-       bloquer l'utilisateur final.
-4. Si aucune mise à jour d'Actualise n'est trouvée à l'étape 2 : passe
-   directement à la vérification/mise à jour de l'application cible, puis
-   la lance.
+## Format de version — `version.json`
+
+La comparaison de version se fait via un **entier incrémental**
+(compteur de build), pas une chaîne semver ni une comparaison de
+chaînes brute :
+
+```json
+{"build": 47}
+```
+
+Comparaison : `distant.build > local.build`.
+
+**Piège explicite à éviter** : comparer `version.json` comme des
+chaînes de caractères donne un résultat lexicographiquement incorrect
+(ex. la chaîne `"9"` est jugée supérieure à `"10"`). L'entier
+incrémental élimine ce piège par construction et reste trivial à
+générer à chaque publication (incrémentation simple).
+
+### Deux fichiers `version.json` distincts
+
+- Un `version.json` dans le **dépôt Actualise** — version d'Actualise
+  lui-même.
+- Un `version.json` dans le **dépôt de chaque application cible** (ex.
+  Scrabble) — l'URL de ce fichier est construite à partir des
+  informations du `config.json` local (dépôt GitHub cible).
+
+Les deux logiques de mise à jour (Actualise vs application cible) sont
+**indépendantes** : chacune a son propre `build` courant, sa propre
+vérification réseau, son propre téléchargement.
+
+## Distribution des binaires — GitHub Releases
+
+Les binaires (Actualise et applications cibles) sont distribués comme
+**assets de GitHub Releases**, pas commités dans l'historique git.
+Téléchargement via l'URL stable :
+
+```
+github.com/<owner>/<repo>/releases/download/<tag>/<fichier>
+```
+
+Un diff binaire a été **écarté** : gain marginal face à la complexité
+ajoutée, les binaires PyInstaller étant recompilés en quasi-totalité à
+chaque changement de code (peu de contenu partagé d'une version à
+l'autre pour qu'un diff soit rentable).
+
+`version.json`, à l'inverse, reste un **petit fichier commité
+normalement** dans le dépôt (pas un asset de Release) — il doit rester
+trivialement accessible via `raw.githubusercontent.com` sans passer par
+l'API Releases.
+
+## Vérification réseau — timeout strict
+
+Toute requête HTTP de vérification de version (`version.json`, Actualise
+ou application cible) doit utiliser un **timeout court (2 à 3
+secondes)**. Passé ce délai, la vérification est traitée comme un échec
+réseau : comportement déjà acté, on se rabat silencieusement sur la
+version installée, sans bloquer l'utilisateur (voir « Décisions
+actées »).
+
+## Séquence de démarrage — vérification non bloquante
+
+Principe central : **le lancement de l'application cible n'attend
+jamais le réseau.**
+
+1. Lancement d'Actualise.
+2. Actualise **lance immédiatement** l'application cible dans sa version
+   actuellement installée, sans attendre aucune vérification.
+3. En parallèle, dans une **tâche de fond** (thread ou process séparé),
+   Actualise :
+   - vérifie `version.json` d'Actualise et `version.json` de
+     l'application cible (deux vérifications indépendantes, chacune
+     avec le timeout strict ci-dessus) ;
+   - télécharge (depuis les GitHub Releases correspondantes) toute
+     nouvelle version trouvée, et la place en zone d'attente locale —
+     **pour le prochain lancement**, jamais pour le lancement en cours ;
+   - si une nouvelle version a été téléchargée, envoie une
+     **notification ntfy informative** (mise à jour prête, effective au
+     prochain lancement).
+4. Au **lancement suivant**, avant de relancer l'application cible,
+   Actualise applique les mises à jour mises en attente :
+   - si une nouvelle version d'Actualise est en attente, l'exécutable
+     est basculé par renommage puis Actualise relance une **2ème
+     instance** de lui-même (la version fraîchement installée) avec le
+     **marqueur explicite** parent → enfant décrit ci-dessous, avant de
+     terminer le parent ; cette bascule est une opération locale
+     (renommage de fichier), donc quasi instantanée — elle ne réintroduit
+     pas d'attente réseau perceptible ;
+   - si une nouvelle version de l'application cible est en attente, elle
+     est basculée par renommage avant le lancement (étape 2) de ce
+     lancement.
+
+**Conséquence assumée** : dans tous les cas (réseau bon, lent ou coupé),
+l'utilisateur ne perçoit **aucun délai** au lancement. Le compromis en
+contrepartie est qu'une mise à jour n'est **jamais appliquée
+immédiatement** : elle est toujours détectée en arrière-plan pendant un
+lancement et n'est effective qu'au lancement suivant.
 
 ## Garde-fou anti-boucle infinie
 
+Le garde-fou par marqueur reste nécessaire pour l'auto-mise-à-jour
+d'Actualise, mais s'inscrit désormais dans le flux non bloquant
+ci-dessus : le relancement parent → enfant n'intervient que pour
+**appliquer une mise à jour déjà téléchargée** (bascule locale rapide),
+jamais pour attendre une vérification réseau en tout début d'exécution.
+
 Quand une instance d'Actualise lance une 2ème instance (la nouvelle
-version), elle lui transmet un **marqueur explicite** signalant qu'il
-s'agit d'un enfant : variable d'environnement (ex. `ACTUALISE_CHILD=1`)
-ou argument de ligne de commande (ex. `--child`), au choix de
-l'implémentation. **Si ce marqueur est présent à son démarrage,
-l'instance saute inconditionnellement l'étape d'auto-mise-à-jour — quoi
-que dise `version.json` — et passe directement à la gestion de
-l'application cible.**
+version, après bascule), elle lui transmet un **marqueur explicite**
+signalant qu'il s'agit d'un enfant : variable d'environnement (ex.
+`ACTUALISE_CHILD=1`) ou argument de ligne de commande (ex. `--child`),
+au choix de l'implémentation. **Si ce marqueur est présent à son
+démarrage, l'instance saute inconditionnellement toute bascule
+d'auto-mise-à-jour supplémentaire — quoi que dise l'état local — et
+passe directement à l'étape 2 de la séquence de démarrage (lancement
+immédiat de l'application cible).**
 
 Ce marqueur est portable Linux/Windows et indépendant de l'état des PID
 au runtime (pas de lecture du parent, pas de dépendance à `psutil` ni au
# ── Zone modifiée : ligne 71 (24 ligne(s)) dans l'ancienne version → ligne 155 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -71,24 +155,28 @@ sans nécessiter de compteur ni d'état persistant à gérer.
 
 | Point | Décision |
 |---|---|
-| Déclenchement de version "officielle" | Alain décide manuellement quand publier une version (probablement via les Releases GitHub, avec tag de version) — pas à chaque commit |
+| Déclenchement de version "officielle" | Alain décide manuellement quand publier une version (via les Releases GitHub, avec tag de version) — pas à chaque commit |
 | Comportement hors-ligne / échec réseau | Se rabat silencieusement sur le lancement de la version déjà installée, sans bloquer l'utilisateur final |
 | Raccourci utilisateur | Pointe vers Actualise, jamais directement vers l'application cible |
 | Configuration | Répertoire dédié type `C:\Actualise\` avec un fichier `config.json` reprenant : version actuelle de l'exe cible, dépôt GitHub cible, répertoire d'installation cible, et autres éléments à définir. Prévoir un chemin **portable** pour les tests/usage Linux (ex. `~/.config/actualise/` ou une variable d'environnement) en plus de `C:\Actualise\`, pour ne pas entamer la réutilisabilité Linux visée par le projet |
-| Notifications | Un topic ntfy dédié par programme géré |
-| Détection de version | Fichier `version.json` sur le dépôt GitHub, comparaison distante vs locale — portable Linux/Windows |
+| Notifications | Un topic ntfy dédié par programme géré ; notification informative envoyée quand une mise à jour a été téléchargée en arrière-plan (effective au prochain lancement) |
+| Format de version | `version.json` avec entier incrémental `build` (ex. `{"build": 47}`), comparaison `>` entre entiers — pas de semver ni de comparaison de chaînes brute (piège "9" > "10" lexicographique) |
+| Fichiers `version.json` | Deux fichiers distincts et indépendants : un dans le dépôt Actualise, un dans le dépôt de chaque application cible (URL construite depuis `config.json`) |
+| Distribution des binaires | Assets de GitHub Releases (URL stable `releases/download/<tag>/<fichier>`), pas commités dans l'historique ; diff binaire écarté (gain marginal, binaires PyInstaller recompilés quasi-intégralement à chaque changement) |
+| `version.json` (stockage) | Reste un petit fichier commité normalement dans le dépôt, pas un asset de Release |
+| Timeout réseau | 2 à 3 secondes sur toute requête de vérification de version ; dépassement traité comme échec réseau |
+| Séquence de démarrage | Non bloquante : lancement immédiat de l'application cible dans sa version installée ; vérification et téléchargement en arrière-plan, appliqués au lancement suivant ; notification ntfy si mise à jour prête |
 | Bootstrap séparé | Écarté pour l'instant — Actualise reste un exécutable unique qui se met à jour lui-même, avec le garde-fou par marqueur ci-dessus |
-| Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), voir section dédiée ci-dessus |
+| Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
 | Configuration portable | `C:\Actualise\` sous Windows, équivalent portable sous Linux (ex. `~/.config/actualise/` ou variable d'environnement) pour préserver la réutilisabilité Linux |
 
 ## Points encore ouverts
 
-- Mécanisme exact de comparaison de version dans `version.json` (numéro
-  simple, semver, hash, autre).
-- Format exact du téléchargement/remplacement des fichiers (zip complet,
-  diff, autre).
 - Contenu détaillé de `config.json` au-delà de "version actuelle, dépôt
   GitHub, répertoire".
+- Emplacement et format exacts de la zone d'attente locale pour les
+  binaires téléchargés en arrière-plan (Actualise et application
+  cible) avant bascule au lancement suivant.
 - Interaction avec le futur `setup.exe` de Scrabble.
 
 ## Points de vigilance connus
