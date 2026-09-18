c0e8c26

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c0e8c26
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 23:57:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    précisions nom d'asset fixe, format tag Release et répertoire d'installation d'Actualise (issue #16, suite #4)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8d920a8..61ab221 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 68 (6 ligne(s)) dans l'ancienne version → ligne 68 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -68,6 +68,17 @@ des fichiers nécessaires à cette version, ainsi que le manifeste de mise
 à jour (voir « Manifeste de mise à jour » ci-dessous) — **un seul asset
 par tag de version**, quel que soit le nombre de fichiers concernés.
 
+**Nom de fichier de l'asset : fixe, sans numéro de version.** L'asset
+publié pour chaque Release porte toujours le même nom :
+**`<préfixe>.zip`** (ex. `actualise.zip`, `scrabble.zip`) — jamais de
+numéro de build dans le nom du fichier lui-même. Le numéro de version
+vit uniquement dans le **tag** de la Release, au format **`v<build>`**
+(ex. `v48`), directement dérivé de l'entier incrémental déjà acté (voir
+« Format de version »). Conséquence pratique : chaque nouvelle Release
+doit re-uploader un asset portant exactement ce nom fixe pour être
+trouvé par Actualise — c'est le tag qui change d'une Release à l'autre,
+jamais le nom de fichier de l'asset.
+
 Un diff binaire a été **écarté** : gain marginal face à la complexité
 ajoutée, les binaires PyInstaller étant recompilés en quasi-totalité à
 chaque changement de code (peu de contenu partagé d'une version à
# ── Zone modifiée : ligne 345 (6 ligne(s)) dans l'ancienne version → ligne 356 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -345,6 +356,16 @@ applications cibles, Scrabble servant de premier exemple concret :
    l'application cible n'entraîne pas nécessairement la désinstallation
    d'Actualise, qui peut continuer à gérer d'autres programmes sur la
    même machine.
+
+   Ce « propre dossier » d'Actualise **n'est pas distinct** de son
+   dossier de configuration : le répertoire d'installation d'Actualise
+   lui-même est exactement `chemin_config_portable()` (ex.
+   `C:\Actualise\` sous Windows, voir « Configuration portable »).
+   `Actualise.exe`, son `config.json` et sa zone d'attente cohabitent
+   dans ce même dossier — il n'existe pas de chemin d'installation
+   séparé pour l'exécutable d'Actualise, contrairement à l'application
+   cible qui a son propre `repertoire_installation` distinct dans
+   `config.json`.
 2. **Raccourcis modifiés.** Les raccourcis Bureau et menu Démarrer créés
    par le setup pointent vers `Actualise.exe` (dans son dossier séparé),
    jamais directement vers l'exécutable de l'application cible —
# ── Zone modifiée : ligne 374 (7 ligne(s)) dans l'ancienne version → ligne 395 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -374,7 +395,7 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Notifications | Un topic ntfy dédié par programme géré ; notification informative envoyée quand une mise à jour a été téléchargée en arrière-plan (effective au prochain lancement) |
 | Format de version | `version.json` avec entier incrémental `build` (ex. `{"build": 47}`), comparaison `>` entre entiers — pas de semver ni de comparaison de chaînes brute (piège "9" > "10" lexicographique) |
 | Fichiers `version.json` | Deux fichiers distincts et indépendants : un dans le dépôt Actualise, un dans le dépôt de chaque application cible (URL construite depuis `config.json`) |
-| Distribution des binaires | Assets de GitHub Releases (URL stable `releases/download/<tag>/<fichier>`), pas commités dans l'historique ; **un seul asset par tag, sous forme d'archive zip** contenant tous les fichiers de la version (exécutable, données, DLL) et le manifeste ; diff binaire écarté (gain marginal, binaires PyInstaller recompilés quasi-intégralement à chaque changement) |
+| Distribution des binaires | Assets de GitHub Releases (URL stable `releases/download/<tag>/<fichier>`), pas commités dans l'historique ; **un seul asset par tag, sous forme d'archive zip** contenant tous les fichiers de la version (exécutable, données, DLL) et le manifeste ; **nom d'asset fixe `<préfixe>.zip`** (ex. `actualise.zip`, `scrabble.zip`), sans numéro de version dans le nom du fichier — chaque nouvelle Release re-uploade un asset de ce même nom ; **tag de Release au format `v<build>`** (ex. `v48`) ; diff binaire écarté (gain marginal, binaires PyInstaller recompilés quasi-intégralement à chaque changement) |
 | `version.json` (stockage) | Reste un petit fichier commité normalement dans le dépôt, pas un asset de Release |
 | Manifeste de mise à jour | `manifest.json` à la racine du zip (`{"build": N, "supprimer": [...]}`) ; `supprimer` est une liste noire optionnelle de chemins à effacer après extraction — fail-safe (un oubli laisse un fichier obsolète, jamais une perte de données) ; script `.bat`/`.sh` exécutable écarté pour portabilité Linux/Windows et sécurité (pas d'exécution de code téléchargé sans supervision) |
 | Timeout réseau | 2 à 3 secondes sur toute requête de vérification de version ; dépassement traité comme échec réseau |
# ── Zone modifiée : ligne 384 (7 ligne(s)) dans l'ancienne version → ligne 405 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -384,7 +405,7 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
 | Configuration portable | `C:\Actualise\` sous Windows, équivalent portable sous Linux (ex. `~/.config/actualise/` ou variable d'environnement) pour préserver la réutilisabilité Linux |
 | Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable` ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
-| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
+| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement `chemin_config_portable()`** — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
 | Cycle de vie d'Actualise | Lancement non bloquant de l'application cible (`Popen` sans `wait()`) : cycles de vie indépendants dès le lancement ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine à son tour — que l'application cible tourne encore ou non ; Actualise n'est pas un processus permanent |
 | Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) — voir « Nommage versionné des zips en zone d'attente » |
 
