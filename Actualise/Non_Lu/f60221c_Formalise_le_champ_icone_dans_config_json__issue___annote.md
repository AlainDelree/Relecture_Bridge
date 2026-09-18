f60221c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f60221c
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 14:17:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Formalise le champ icone dans config.json (issue #26, suite #4)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 69e82e8..d721989 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 154 (7 ligne(s)) dans l'ancienne version → ligne 154 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -154,7 +154,8 @@ les champs nécessaires au fonctionnement complet décrit ci-dessus
     "depot_github": "AlainDelree/Scrabble",
     "build_installe": 47,
     "repertoire_installation": "C:\\Scrabble\\",
-    "executable": "Scrabble.exe"
+    "executable": "Scrabble.exe",
+    "icone": "C:\\Scrabble\\Scrabble.ico"
   },
   "zone_attente": "C:\\Actualise\\attente\\",
   "topic_ntfy": "actualise-scrabble"
# ── Zone modifiée : ligne 175 (6 ligne(s)) dans l'ancienne version → ligne 176 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -175,6 +176,17 @@ Détail des champs :
   3 de la « Séquence de démarrage »).
 - `repertoire_installation` : dossier cible pour l'extraction du zip de
   mise à jour de l'application cible.
+- `icone` (sous `application_cible` uniquement, **optionnel**) : chemin
+  vers le fichier `.ico` de l'application cible, déployé par le setup de
+  cette application à un emplacement connu (ex. à côté de son
+  exécutable). Ce champ est **informationnel/documenté pour Actualise**
+  — Actualise n'a pas d'interface graphique et ne le lit **pas** au
+  runtime — mais sert de **convention** pour le setup de l'application
+  cible : le même chemin `.ico` doit être utilisé à la fois pour ce
+  champ et pour le champ `IconFilename` du raccourci créé par ce setup
+  (voir « Intégration avec le setup.exe d'une application cible »),
+  afin que la documentation de `config.json` reste cohérente avec
+  l'icône réellement affichée par le raccourci.
 - `zone_attente` : chemin du dossier où sont stockés les zip
   téléchargés en arrière-plan avant bascule au lancement suivant —
   commun à Actualise et à l'application cible. Ceci referme le point
# ── Zone modifiée : ligne 409 (6 ligne(s)) dans l'ancienne version → ligne 421 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -409,6 +421,18 @@ applications cibles, Scrabble servant de premier exemple concret :
    conforme à la décision actée dès le « Principe de fonctionnement »
    (« le raccourci ne doit jamais pointer directement vers l'application
    cible »).
+
+   Ce raccourci pointant vers `Actualise.exe` afficherait par défaut
+   l'icône générique d'Actualise plutôt que celle de l'application
+   cible. Pour éviter cela, le setup de l'application cible **déploie
+   son propre fichier `.ico`** (ex. à côté de l'exécutable cible) et
+   l'utilise à la fois pour :
+   - le champ `IconFilename` du raccourci créé (Bureau/menu Démarrer),
+     qui continue de pointer vers `Actualise.exe` mais affiche l'icône
+     de l'application cible ;
+   - le champ `icone` du `config.json` généré par ce même setup, avec
+     **le même chemin** dans les deux cas, pour cohérence documentée
+     (voir « Contenu de `config.json` »).
 3. **Déploiement d'Actualise par le setup.** Le setup dépose désormais
    `Actualise.exe` dans son dossier séparé, en plus des fichiers propres
    à l'application cible.
# ── Zone modifiée : ligne 441 (8 ligne(s)) dans l'ancienne version → ligne 465 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -441,8 +465,8 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Bootstrap séparé | Écarté pour l'instant — Actualise reste un exécutable unique qui se met à jour lui-même, avec le garde-fou par marqueur ci-dessus |
 | Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
 | Configuration portable | `C:\Actualise\` sous Windows, équivalent portable sous Linux (ex. `~/.config/actualise/` ou variable d'environnement) pour préserver la réutilisabilité Linux |
-| Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable` ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
-| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement `chemin_config_portable()`** — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
+| Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable`, et `icone` (optionnel, chemin `.ico` documenté pour le setup cible — non lu au runtime par Actualise) ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
+| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement `chemin_config_portable()`** — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées ; **icône du raccourci** : le setup de l'application cible déploie son propre fichier `.ico` et l'utilise à la fois pour `IconFilename` du raccourci (qui pointe vers `Actualise.exe` mais affiche l'icône de l'application cible) et pour le champ `icone` de `config.json` — même chemin dans les deux cas — voir « Intégration avec le setup.exe d'une application cible » |
 | Cycle de vie d'Actualise | Lancement non bloquant de l'application cible (`Popen` sans `wait()`) : cycles de vie indépendants dès le lancement ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine à son tour — que l'application cible tourne encore ou non ; Actualise n'est pas un processus permanent |
 | Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) ; **si plusieurs zips du même préfixe coexistent**, seul celui au build le plus élevé est considéré, les autres supprimés sans être appliqués (même logique que pour un résidu obsolète) — voir « Nommage versionné des zips en zone d'attente » |
 
