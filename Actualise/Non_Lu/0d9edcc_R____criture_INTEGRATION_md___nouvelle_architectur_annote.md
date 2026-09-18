0d9edcc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0d9edcc
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 20:27:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Réécriture INTEGRATION.md : nouvelle architecture multi-app (issue #37)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/INTEGRATION.md b/INTEGRATION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e94d43f..19af184 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/INTEGRATION.md
# ── Version APRÈS ce commit.
+++ b/INTEGRATION.md
# ── Zone modifiée : ligne 1 (143 ligne(s)) dans l'ancienne version → ligne 1 (113 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,143 +1,113 @@
 # Intégration — guide pratique pour une application cible
 
-## 1. Objectif du document
-
-Ce document est un guide **pratique, orienté checklist/action**, destiné
-à une conversation Claude qui travaille sur une application cible
-(Scrabble, Rummikub, ou un futur projet) et doit l'intégrer avec
-Actualise. Il rassemble les points opérationnels et les pièges déjà
-rencontrés en production, sous une forme directement actionnable.
-
-Il **complète** [CONCEPTION.md](CONCEPTION.md), qui reste la référence
-pour l'architecture complète, le détail de chaque champ et les
-justifications des choix de conception. En cas de doute ou de besoin de
-détail supplémentaire, se reporter à CONCEPTION.md — ce document ne
-duplique pas ce detail.
-
-## 2. Checklist d'intégration pour un nouveau projet cible
-
-- **Dossier d'installation dédié** : `C:\Actualise_<NomApplication>\`
-  (ex. `C:\Actualise_Scrabble\`) — **jamais** `C:\Actualise\` seul, sous
-  peine de collision entre applications cibles installées sur la même
-  machine (voir CONCEPTION.md « Configuration portable » et « Points de
-  vigilance connus »).
-- **Raccourci** (Bureau/menu Démarrer) pointant vers `Actualise.exe`
-  dans ce dossier — **jamais** vers l'exécutable de l'application cible
-  directement, sinon la mise à jour ne se déclenche jamais.
-- **Icône du raccourci** : déployer un fichier `.ico` propre à
-  l'application cible et utiliser **le même chemin** pour :
-  - le champ `IconFilename` du raccourci (qui continue de pointer vers
-    `Actualise.exe`) ;
-  - le champ `icone` du `config.json` généré (voir §3).
-- **`config.json` initial complet** généré par le setup, reflétant les
-  valeurs réelles de cette installation (voir §3 et §4).
-- **Copie intégrale du contenu extrait de `actualise.zip`** par le
-  setup : `Actualise.exe` **et** le dossier `_internal\` — jamais l'exe
-  seul. Incident réel : `Failed to load Python DLL` au lancement si
-  `_internal\` manque.
-- Le dépôt de l'application cible doit publier :
-  - son propre `version.json` (`{"build": N, "sha256": "..."}`) ;
-  - ses Releases GitHub au format `<préfixe>.zip` (asset de nom fixe,
-    tag `v<build>`), avec un `manifest.json` inclus à la racine du zip.
-
-  Voir CONCEPTION.md « Distribution des binaires » et « Manifeste de
-  mise à jour » pour le détail complet de ce format.
-
-## 3. Format de `config.json` (référence rapide)
+## 1. Objectif
 
+Guide pratique destiné à une conversation Claude qui intègre une nouvelle application cible avec Actualise. Complète CONCEPTION.md qui reste la référence architecturale.
+
+## 2. Architecture générale
+
+Actualise est une instance unique partagée entre toutes les applications cibles, installée dans `C:\Actualise\`. Chaque application cible a son propre fichier de configuration dans ce dossier. Actualise est lancé avec `--config <nom>` pour savoir quelle application gérer.
+
+## 3. Checklist d'intégration pour un nouveau projet cible
+
+- **Dossier Actualise partagé** : `C:\Actualise\` — jamais un dossier par app.
+- **Deux fichiers de config** à créer par le setup InnoSetup :
+  - `C:\Actualise\config_actualise.json` — uniquement s'il n'existe pas déjà (ne pas écraser si une autre app l'a déjà créé).
+  - `C:\Actualise\config_<nom>.json` — spécifique à cette app (ex. `config_scrabble.json`).
+- **Trois exécutables** à déployer dans `C:\Actualise\` par le setup :
+  - `Actualise.exe`
+  - `_internal\` (dossier complet — jamais l'exe seul, incident réel : `Failed to load Python DLL` si `_internal\` manque)
+  - `ActualiseUI.exe` (exécutable séparé, inclus dans `actualise-v<N>.zip`)
+  - Déployer uniquement si la version embarquée est plus récente que celle déjà présente (InnoSetup gère ça nativement).
+- **Raccourci** Bureau pointant vers `C:\Actualise\Actualise.exe` avec l'argument `--config <nom>` (ex. `--config scrabble`). Ne jamais pointer vers l'exécutable de l'app cible directement.
+- **Icône du raccourci** : fichier `.ico` propre à l'app cible, même chemin dans `config_<nom>.json` (champ `icone`).
+- **Nettoyage de l'ancien dossier** : si `C:\Actualise_<NomApp>\` existe (ancienne architecture), le supprimer entièrement lors de l'installation.
+- **Désinstallation** : supprimer `config_<nom>.json` mais pas `C:\Actualise\` si d'autres `config_*.json` y existent encore.
+- **Intégration dans le code de l'app cible** : voir §6.
+
+## 4. Format des fichiers de configuration
+
+### config_actualise.json (partagé, ne pas écraser s'il existe)
+```json
+{
+  "build_installe": 8,
+  "depot_github": "AlainDelree/Actualise",
+  "zone_attente": "C:\\Actualise\\attente\\"
+}
+```
+`build_installe` doit refléter la version réelle d'Actualise embarquée, lue dynamiquement depuis le zip téléchargé — jamais une valeur figée en dur (incident réel : boucle de fausse détection si la valeur ne correspond pas).
+
+### config_<nom>.json (spécifique à l'app)
 ```json
 {
-  "actualise": {
-    "build_installe": 3,
-    "depot_github": "AlainDelree/Actualise"
-  },
-  "application_cible": {
-    "nom": "Scrabble",
-    "depot_github": "AlainDelree/Scrabble",
-    "build_installe": 47,
-    "repertoire_installation": "C:\\Scrabble\\",
-    "executable": "Scrabble.exe",
-    "icone": "C:\\Scrabble\\Scrabble.ico"
-  },
-  "zone_attente": "C:\\Actualise_Scrabble\\attente\\",
-  "topic_ntfy": "actualise-scrabble"
+  "nom": "Scrabble",
+  "depot_github": "AlainDelree/Scrabble",
+  "build_installe": 8,
+  "repertoire_installation": "C:\\Scrabble\\",
+  "executable": "Scrabble.exe",
+  "icone": "C:\\Scrabble\\Scrabble.ico",
+  "topic_ntfy": "mon-topic-ntfy"
 }
 ```
 
-Le détail de chaque champ (rôle exact, portabilité Linux/Windows, cas
-particulier de `icone` non lu au runtime, etc.) est documenté dans
-CONCEPTION.md « Contenu de `config.json` » — ne pas dupliquer ici.
-
-## 4. Génération de `build_installe` — piège connu
-
-`build_installe` sous le bloc `actualise` doit refléter la **version
-réelle d'Actualise embarquée** au moment du build du setup, lue
-**dynamiquement** (ex. depuis le `manifest.json` du zip Actualise
-téléchargé/embarqué), **jamais une valeur figée en dur** dans le script
-de build.
-
-**Incident réel** : un `config.json` généré avec `build_installe: 1`
-alors que la v2 d'Actualise était réellement embarquée a provoqué une
-boucle de fausse détection de mise à jour (Actualise se croyait en
-retard sur lui-même en permanence).
-
-## 5. Bug bootstrap connu (Actualise ≤ v2) — implication permanente
-
-Un Actualise en **v1 ou v2** contient un bug qui l'empêche de
-s'auto-mettre-à-jour vers v3 : `PermissionError` lors de la bascule
-(l'exécutable en cours d'exécution ne peut pas être réécrit en place).
-Corrigé en v3 par la bascule via dossier temporaire + renommage — voir
-CONCEPTION.md « Garde-fou anti-boucle infinie » (section « Bascule
-sécurisée par dossier temporaire + renommage »).
-
-**Ce cas ne peut pas s'auto-réparer** : une instance encore en v1/v2 ne
-peut pas se corriger elle-même en se mettant à jour, puisque le bug est
-précisément dans son propre mécanisme de bascule. Toute installation
-encore en v1/v2 doit être **réinstallée** avec un setup embarquant
-directement v3 ou une version plus récente.
-
-**Contournement de secours** si un utilisateur est bloqué en attendant
-une réinstallation : éditer manuellement `build_installe` (bloc
-`actualise`) dans son `config.json` vers le numéro déjà présent en zone
-d'attente, et supprimer les zips résiduels de `zone_attente`. Ceci
-débloque l'usage immédiat (plus de boucle de fausse détection), mais
-laisse l'exécutable `Actualise.exe` **physiquement daté** (toujours en
-v1/v2) — seule une réinstallation corrige réellement la situation.
-
-Une fois une machine réellement mise à jour vers v3 ou plus récent, les
-mises à jour futures fonctionnent normalement : le bug ne concernait que
-cette transition précise (v1/v2 → v3), pas le mécanisme de mise à jour
-en général.
-
-## 6. Workflow de publication (mode `--publier`)
-
-Le principe déjà en place pour Actualise (documenté dans
-`BUILD_WINDOWS_CCW.md`, dépôt bridge_agent) :
-
-- numéro de build **auto-incrémenté** (ou forçable explicitement) ;
-- SHA-256 du zip publié **calculé automatiquement** ;
-- `version.json` mis à jour et **commit local automatisé** ;
-- `git push` et création de la **Release GitHub toujours manuels** (pas
-  d'automatisation qui pousserait ou publierait sans validation
-  explicite).
-
-**Recommandation** : adopter le même principe pour les scripts de build
-des applications cibles — cohérence de workflow entre Actualise et
-chaque application cible, et même garde-fou (aucune publication
-distante sans validation manuelle).
-
-## 7. Convention ntfy
-
-Le `topic_ntfy` d'une application cible peut être :
-
-- **réutilisé** depuis un topic existant, si pertinent — cas Scrabble :
-  réutilisation du topic de clôture d'issue Bridge_Agent déjà existant,
-  avec le préfixe `"MAJ - "` sur les messages d'Actualise pour les
-  distinguer visuellement des notifications de clôture d'issue dans le
-  même flux ;
-- ou **dédié**, dans un topic propre à l'application cible (règle par
-  défaut pour un public destinataire différent).
-
-Les deux options sont valables, tant que les messages restent
-identifiables (préfixe ou topic distinct). Voir CONCEPTION.md « Décisions
-actées » (ligne « Notifications ») pour le détail de cette règle.
+## 5. Format des Releases GitHub de l'application cible
+
+- Asset zip nommé `<prefixe>-v<build>.zip` (ex. `scrabble-v8.zip`) — Actualise construit l'URL dynamiquement à partir du numéro de build.
+- Tag GitHub : `v<build>` (ex. `v8`).
+- Le zip doit être à plat : exécutable et `_internal\` directement à la racine, sans sous-dossier intermédiaire.
+- Inclure un `manifest.json` à la racine : `{"supprimer": []}` (liste des fichiers à nettoyer lors de l'installation, vide par défaut).
+- L'app cible doit publier son propre `version.json` à la racine du dépôt : `{"build": N, "sha256": "..."}`.
+
+## 6. Intégration dans le code de l'application cible
+
+Deux ajouts dans le code de l'app, une seule fois, jamais à modifier ensuite.
+
+### Au démarrage (avant l'ouverture de la fenêtre)
+```python
+import json
+import subprocess
+from pathlib import Path
+
+_flag = Path(sys.executable).parent / "actualise_update.flag"
+if _flag.exists():
+    try:
+        _data = json.loads(_flag.read_text(encoding="utf-8"))
+        subprocess.Popen([
+            _data["actualise_ui"],
+            "--bat", _data["bat"],
+            "--flag", str(_flag),
+            "--relancer", sys.executable,
+        ])
+    except Exception:
+        pass  # ne jamais bloquer le démarrage
+```
+
+### À la fermeture de la fenêtre principale
+Adapter à la technologie UI utilisée (pywebview `window.events.closing`, tkinter `WM_DELETE_WINDOW`, etc.) :
+```python
+def _handler_fermeture_actualise():
+    _flag = Path(sys.executable).parent / "actualise_update.flag"
+    if _flag.exists():
+        try:
+            _data = json.loads(_flag.read_text(encoding="utf-8"))
+            _flag.unlink(missing_ok=True)
+            subprocess.Popen([_data["bat"]], shell=True)
+        except Exception:
+            pass
+```
+
+## 7. Workflow de publication (build script)
+
+- Numéro de build auto-incrémenté (ou forçable explicitement).
+- SHA-256 du zip calculé automatiquement.
+- `version.json` mis à jour et commit local automatisé.
+- `git push` et création de la Release GitHub toujours manuels.
+- URL de téléchargement d'Actualise dans le script de build : toujours pointer vers la dernière Release Actualise disponible — ne jamais hardcoder un numéro de version.
+
+## 8. Convention ntfy
+
+`topic_ntfy` peut être réutilisé depuis un topic existant (avec préfixe `"MAJ - "` pour distinguer les messages) ou dédié à l'application cible. Les deux sont valables.
+
+## 9. Bug bootstrap connu
+
+Les installations encore sur Actualise ≤ v2 ne peuvent pas s'auto-mettre-à-jour — le mécanisme de bascule contenait un bug qui empêche la mise à jour vers v3+. Ces machines doivent être réinstallées manuellement avec un setup embarquant une version récente d'Actualise.
