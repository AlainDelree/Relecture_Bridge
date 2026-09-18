68c1eab

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 68c1eab
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 12:43:16 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #406 : documenter fetch + reset --hard (au lieu de pull --ff-only) pour le clone CCW rummikub

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BUILD_WINDOWS_CCW.md b/BUILD_WINDOWS_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a9d6744..2aec2d6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BUILD_WINDOWS_CCW.md
# ── Version APRÈS ce commit.
+++ b/BUILD_WINDOWS_CCW.md
# ── Zone modifiée : ligne 81 (6 ligne(s)) dans l'ancienne version → ligne 81 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -81,6 +81,16 @@ build suit déjà ce schéma de staging local et, si oui, étendre le
 
 - **Chemin du clone CCW** : `Z:\CCW\rummikub`
 - **Script de build** : `build\rebuild_rummikub.bat` (6 étapes)
+- **Mise à jour du clone (issue #406)** : NE PAS utiliser
+  `git pull --ff-only` en étape 1 — le clone CCW accumule entre chaque
+  build des commits locaux non poussés (`version.json`, backup), donc le
+  fast-forward échoue systématiquement. Utiliser `fetch` + `reset --hard`,
+  qui aligne proprement le clone sur `origin/master` sans merge ni
+  conflit, quel que soit l'état local :
+  ```
+  git -C Z:\CCW\rummikub fetch origin
+  git -C Z:\CCW\rummikub reset --hard origin/master
+  ```
 - **`.spec`** : `rummikub.spec` — liste explicite des `datas`
   (`src/rummikub/ui/web/`), aucun `collect_tree` en bloc
 - **TIMEOUT de référence observé** : 1200s (build réel : ~333s)
# (diff du fichier suivant)
diff --git a/consignes/projet_rummikub.md b/consignes/projet_rummikub.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..98bc489
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/consignes/projet_rummikub.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,14 @@
+## Spécificités du projet Rummikub
+
+- **Build CCW — mise à jour du clone (issue #406) :** l'étape de mise à
+  jour du clone `Z:\CCW\rummikub` ne doit **jamais** utiliser
+  `git pull --ff-only` : ce clone accumule entre chaque build des commits
+  locaux non poussés (`version.json`, backup), donc le fast-forward échoue
+  systématiquement. Utiliser à la place `fetch` + `reset --hard`, qui
+  aligne proprement le clone sur `origin/master` sans merge ni conflit,
+  quel que soit l'état local :
+
+  ```
+  git -C Z:\CCW\rummikub fetch origin
+  git -C Z:\CCW\rummikub reset --hard origin/master
+  ```
