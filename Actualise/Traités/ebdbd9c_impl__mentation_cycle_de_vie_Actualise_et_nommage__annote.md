ebdbd9c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ebdbd9c
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 23:31:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    implémentation cycle de vie Actualise et nommage versionné des zips (issue #14, suite #4)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index be0a7a6..8d920a8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 203 (6 ligne(s)) dans l'ancienne version → ligne 203 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -203,6 +203,22 @@ jamais le réseau.**
    - si une nouvelle version a été téléchargée **et validée**, envoie une
      **notification ntfy informative** (mise à jour prête, effective au
      prochain lancement).
+**Cycle de vie du processus Actualise.** Le lancement de l'application
+cible (étape 2) se fait via un mécanisme **non bloquant** (ex. `Popen`
+sans `wait()`) : Actualise n'attend **jamais** la fermeture de
+l'application cible — leurs cycles de vie sont **indépendants** dès le
+lancement, que l'application cible tourne encore ou se soit déjà
+fermée n'a aucune incidence sur la suite. Une fois l'application cible
+lancée, Actualise attend uniquement la fin de sa propre **tâche de
+fond** (étape 3 ci-dessus), qui va jusqu'au bout de son cycle
+(vérification des deux `version.json`, téléchargement et validation
+SHA-256 si nécessaire, notification ntfy éventuelle). Dès que cette
+tâche de fond se termine, **Actualise se termine à son tour** — que
+l'application cible tourne encore ou non. Actualise n'est donc pas un
+processus permanent : il effectue son travail de vérification/
+téléchargement en arrière-plan puis se ferme, sans attendre une action
+de l'utilisateur ni la fermeture de l'application cible.
+
 4. Au **lancement suivant**, avant de relancer l'application cible,
    Actualise applique les mises à jour mises en attente. Pour chaque
    mise à jour en attente (Actualise ou application cible), la bascule
# ── Zone modifiée : ligne 242 (6 ligne(s)) dans l'ancienne version → ligne 258 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,6 +258,36 @@ contrepartie est qu'une mise à jour n'est **jamais appliquée
 immédiatement** : elle est toujours détectée en arrière-plan pendant un
 lancement et n'est effective qu'au lancement suivant.
 
+## Nommage versionné des zips en zone d'attente
+
+Convention de nommage dans `zone_attente` : `<préfixe>_<build>.zip` (ex.
+`actualise_48.zip`, `scrabble_112.zip`). Le préfixe identifie à qui
+appartient le zip (`actualise`, ou le nom de l'application cible tel
+que défini dans `config.json`) ; le numéro de build permet la
+comparaison directe avec le `build_installe` correspondant de
+`config.json` (voir « Contenu de `config.json` ») sans avoir à ouvrir
+le zip ni consulter un fichier séparé.
+
+Comportement au démarrage, **avant bascule** (étape 4 de la séquence
+ci-dessus) : pour chaque préfixe connu (`actualise`, nom de
+l'application cible), si un fichier `<préfixe>_<build>.zip` existe dans
+`zone_attente` :
+
+- si `build` > `build_installe` correspondant → mise à jour valide,
+  bascule appliquée (extraction + manifeste, voir étape 4 ci-dessus),
+  puis le zip est **supprimé après succès** de la bascule ;
+- si `build` ≤ `build_installe` correspondant → résidu obsolète (déjà
+  appliqué lors d'un cycle précédent, ou périmé pour toute autre
+  raison) → le zip est **supprimé sans être appliqué**, sans bloquer le
+  démarrage.
+
+Ce mécanisme remplit une double fonction : marqueur d'appartenance
+(quel préfixe identifie le zip) et garde-fou contre un zip laissé
+indéfiniment dans la zone d'attente — un nettoyage automatique des
+résidus obsolètes a lieu à chaque démarrage, complémentaire au
+garde-fou par marqueur décrit ci-dessous (« Garde-fou anti-boucle
+infinie »).
+
 ## Garde-fou anti-boucle infinie
 
 Le garde-fou par marqueur reste nécessaire pour l'auto-mise-à-jour
# ── Zone modifiée : ligne 339 (6 ligne(s)) dans l'ancienne version → ligne 385 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -339,6 +385,8 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Configuration portable | `C:\Actualise\` sous Windows, équivalent portable sous Linux (ex. `~/.config/actualise/` ou variable d'environnement) pour préserver la réutilisabilité Linux |
 | Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable` ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
 | Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
+| Cycle de vie d'Actualise | Lancement non bloquant de l'application cible (`Popen` sans `wait()`) : cycles de vie indépendants dès le lancement ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine à son tour — que l'application cible tourne encore ou non ; Actualise n'est pas un processus permanent |
+| Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) — voir « Nommage versionné des zips en zone d'attente » |
 
 ## Points de vigilance connus
 
