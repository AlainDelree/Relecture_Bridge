317f38d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 317f38d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 23:06:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #465 : chemin VirtualBox obsolète Z:\CCW\rummikub -> C:\CCW_Share\CCW\rummikub

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/consignes/projet_rummikub.md b/consignes/projet_rummikub.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 98bc489..e6f236b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/consignes/projet_rummikub.md
# ── Version APRÈS ce commit.
+++ b/consignes/projet_rummikub.md
# ── Zone modifiée : ligne 1 (7 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,7 +1,7 @@
 ## Spécificités du projet Rummikub
 
 - **Build CCW — mise à jour du clone (issue #406) :** l'étape de mise à
-  jour du clone `Z:\CCW\rummikub` ne doit **jamais** utiliser
+  jour du clone `C:\CCW_Share\CCW\rummikub` ne doit **jamais** utiliser
   `git pull --ff-only` : ce clone accumule entre chaque build des commits
   locaux non poussés (`version.json`, backup), donc le fast-forward échoue
   systématiquement. Utiliser à la place `fetch` + `reset --hard`, qui
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,6 @@
   quel que soit l'état local :
 
   ```
-  git -C Z:\CCW\rummikub fetch origin
-  git -C Z:\CCW\rummikub reset --hard origin/master
+  git -C C:\CCW_Share\CCW\rummikub fetch origin
+  git -C C:\CCW_Share\CCW\rummikub reset --hard origin/master
   ```
