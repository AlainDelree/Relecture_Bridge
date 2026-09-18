9528236

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9528236
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 15:41:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #413 : echappement des parentheses dans echo (bloc if/else final) de rebuild_scrabble.bat

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e30a74d..9654368 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 339 (7 ligne(s)) dans l'ancienne version → ligne 339 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -339,7 +339,7 @@ if "%PUBLIER%"=="1" (
     echo place^), aucun reset. Push et release restent MANUELS.
     echo.
 ) else (
-    echo Nettoyage du clone CCW (reset commits locaux)...
+    echo Nettoyage du clone CCW ^(reset commits locaux^)...
     git -C C:\CCW_Share\CCW\scrabble reset --hard origin/master
     echo Clone CCW propre.
     echo.
