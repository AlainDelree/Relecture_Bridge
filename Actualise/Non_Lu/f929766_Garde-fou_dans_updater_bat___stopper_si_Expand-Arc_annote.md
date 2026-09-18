f929766

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f929766
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 14:22:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Garde-fou dans updater.bat : stopper si Expand-Archive echoue (issue #39)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9ce313e..cb669bb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 381 (6 ligne(s)) dans l'ancienne version → ligne 381 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -381,6 +381,11 @@ cd /d "{dossier_actualise}"
 if exist "_internal.old" rmdir /s /q "_internal.old"
 if exist "Actualise.exe.old" del /f "Actualise.exe.old"
 powershell -NoProfile -Command "Expand-Archive -LiteralPath '{chemin_zip}' -DestinationPath '{dossier_actualise}\\maj_bat' -Force"
+if not exist "maj_bat\\_internal" (
+    echo ERREUR : extraction du zip echouee, bascule annulee.
+    rmdir /s /q "maj_bat" 2>nul
+    goto :eof
+)
 ren "_internal" "_internal.old"
 move "maj_bat\\_internal" "_internal"
 ren "Actualise.exe" "Actualise.exe.old"
