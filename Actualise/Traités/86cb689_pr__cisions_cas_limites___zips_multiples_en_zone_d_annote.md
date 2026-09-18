86cb689

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 86cb689
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 06:04:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    précisions cas limites : zips multiples en zone d'attente et manifeste absent (issue #20, suite #4)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 61ab221..7e170fc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 123 (6 ligne(s)) dans l'ancienne version → ligne 123 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -123,6 +123,19 @@ raisons :
   explicites — le manifeste JSON ne permet structurellement rien d'autre
   que cette suppression bornée.
 
+**Cas limite : `manifest.json` absent de l'archive.** Traité comme
+**bloquant** : la bascule de cette mise à jour échoue et n'est pas
+appliquée (ni extraction, ni suppression, ni lancement de la version
+mise à jour). Le zip **n'est pas supprimé** de `zone_attente` — une
+nouvelle tentative pourra avoir lieu à un lancement ultérieur si le zip
+est re-téléchargé (comportement précis de récupération, ex. nouvelle
+tentative immédiate ou attente du prochain cycle de fond, à préciser
+côté implémentation). Raison de ce choix : un zip sans manifeste est
+considéré **malformé** plutôt que de supposer silencieusement « rien à
+supprimer » — un manifeste manquant est plus probablement le signe d'un
+problème de publication (asset incomplet, erreur de packaging) qu'une
+intention volontaire de l'auteur de la Release.
+
 ## Contenu de `config.json`
 
 Reprend la base déjà actée (version actuelle, dépôt GitHub cible,
# ── Zone modifiée : ligne 292 (6 ligne(s)) dans l'ancienne version → ligne 305 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -292,6 +305,20 @@ l'application cible), si un fichier `<préfixe>_<build>.zip` existe dans
   raison) → le zip est **supprimé sans être appliqué**, sans bloquer le
   démarrage.
 
+**Cas limite : plusieurs zips du même préfixe présents simultanément**
+(ex. `scrabble_47.zip` et `scrabble_48.zip` coexistant dans
+`zone_attente`). Ce cas peut survenir légitimement si la tâche de fond
+télécharge une nouvelle version avant que la précédente n'ait été
+appliquée (l'utilisateur n'a pas relancé l'application entre les deux
+cycles de vérification). Comportement retenu : parmi les fichiers
+`<préfixe>_<build>.zip` d'un même préfixe, seul celui au **build le
+plus élevé** est considéré et éventuellement appliqué (selon la
+comparaison `build` > `build_installe` ci-dessus) ; tous les autres
+sont **supprimés sans être appliqués**, quelle que soit leur valeur de
+`build` — même logique que pour un unique zip obsolète décrite
+ci-dessus, un build inférieur au maximum présent étant nécessairement
+un résidu dépassé par une version plus récente déjà téléchargée.
+
 Ce mécanisme remplit une double fonction : marqueur d'appartenance
 (quel préfixe identifie le zip) et garde-fou contre un zip laissé
 indéfiniment dans la zone d'attente — un nettoyage automatique des
# ── Zone modifiée : ligne 397 (7 ligne(s)) dans l'ancienne version → ligne 424 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -397,7 +424,7 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Fichiers `version.json` | Deux fichiers distincts et indépendants : un dans le dépôt Actualise, un dans le dépôt de chaque application cible (URL construite depuis `config.json`) |
 | Distribution des binaires | Assets de GitHub Releases (URL stable `releases/download/<tag>/<fichier>`), pas commités dans l'historique ; **un seul asset par tag, sous forme d'archive zip** contenant tous les fichiers de la version (exécutable, données, DLL) et le manifeste ; **nom d'asset fixe `<préfixe>.zip`** (ex. `actualise.zip`, `scrabble.zip`), sans numéro de version dans le nom du fichier — chaque nouvelle Release re-uploade un asset de ce même nom ; **tag de Release au format `v<build>`** (ex. `v48`) ; diff binaire écarté (gain marginal, binaires PyInstaller recompilés quasi-intégralement à chaque changement) |
 | `version.json` (stockage) | Reste un petit fichier commité normalement dans le dépôt, pas un asset de Release |
-| Manifeste de mise à jour | `manifest.json` à la racine du zip (`{"build": N, "supprimer": [...]}`) ; `supprimer` est une liste noire optionnelle de chemins à effacer après extraction — fail-safe (un oubli laisse un fichier obsolète, jamais une perte de données) ; script `.bat`/`.sh` exécutable écarté pour portabilité Linux/Windows et sécurité (pas d'exécution de code téléchargé sans supervision) |
+| Manifeste de mise à jour | `manifest.json` à la racine du zip (`{"build": N, "supprimer": [...]}`) ; `supprimer` est une liste noire optionnelle de chemins à effacer après extraction — fail-safe (un oubli laisse un fichier obsolète, jamais une perte de données) ; script `.bat`/`.sh` exécutable écarté pour portabilité Linux/Windows et sécurité (pas d'exécution de code téléchargé sans supervision) ; **`manifest.json` absent → bloquant** : bascule échoue, non appliquée, zip conservé pour nouvelle tentative ultérieure (zip considéré malformé, pas une absence volontaire de suppression) |
 | Timeout réseau | 2 à 3 secondes sur toute requête de vérification de version ; dépassement traité comme échec réseau |
 | Séquence de démarrage | Non bloquante : lancement immédiat de l'application cible dans sa version installée ; vérification et téléchargement en arrière-plan, appliqués au lancement suivant ; notification ntfy si mise à jour prête |
 | Vérification SHA-256 du zip | `version.json` porte un champ `sha256` du zip complet publié ; après téléchargement, avant mise en zone d'attente, comparaison du SHA-256 calculé sur le fichier reçu ; non-correspondance → téléchargement rejeté, aucune zone d'attente mise à jour, nouvelle tentative au cycle suivant (même repli que pour un échec réseau) ; liste de fichiers attendus post-extraction écartée (redondante une fois le zip validé, une extraction incomplète relevant d'un problème d'environnement local détectable par vérification d'erreur d'extraction) |
# ── Zone modifiée : ligne 407 (7 ligne(s)) dans l'ancienne version → ligne 434 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -407,7 +434,7 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable` ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
 | Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement `chemin_config_portable()`** — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
 | Cycle de vie d'Actualise | Lancement non bloquant de l'application cible (`Popen` sans `wait()`) : cycles de vie indépendants dès le lancement ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine à son tour — que l'application cible tourne encore ou non ; Actualise n'est pas un processus permanent |
-| Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) — voir « Nommage versionné des zips en zone d'attente » |
+| Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) ; **si plusieurs zips du même préfixe coexistent**, seul celui au build le plus élevé est considéré, les autres supprimés sans être appliqués (même logique que pour un résidu obsolète) — voir « Nommage versionné des zips en zone d'attente » |
 
 ## Points de vigilance connus
 
